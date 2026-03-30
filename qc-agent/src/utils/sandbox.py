# -*- coding: utf-8 -*-
#
# Copyright 2025 Google LLC
# SPDX-License-Identifier: Apache-2.0

import asyncio
import os
import sys
import shlex
import platform
import subprocess
import signal
import atexit
from pathlib import Path
from typing import List, Optional, Any, Dict

# Placeholder for project-specific configurations.
# In a real application, these would be properly defined classes.
class SandboxConfig:
    def __init__(self, command: str, image: str):
        self.command = command
        self.image = image

class WorkspaceContext:
    def getDirectories(self) -> List[str]:
        # This is a mock implementation.
        # It should return a list of workspace directories.
        return []

class Config:
    def getDebugMode(self) -> bool:
        return bool(os.environ.get('DEBUG'))

    def getTargetDir(self) -> str:
        return os.getcwd()
        
    def getWorkspaceContext(self) -> WorkspaceContext:
        return WorkspaceContext()


class ConsolePatcher:
    """A placeholder for the ConsolePatcher class."""
    def __init__(self, debugMode: bool, stderr: bool):
        pass
    def patch(self):
        pass
    def cleanup(self):
        pass


# --- Constants ---
# In a real project, these might come from a dedicated config file.
SETTINGS_DIRECTORY_NAME = ".qwen-code"
USER_SETTINGS_DIR = os.path.join(os.path.expanduser("~"), SETTINGS_DIRECTORY_NAME)
LOCAL_DEV_SANDBOX_IMAGE_NAME = "qwen-code-sandbox"
SANDBOX_NETWORK_NAME = "qwen-code-sandbox"
SANDBOX_PROXY_NAME = "qwen-code-sandbox-proxy"
BUILTIN_SEATBELT_PROFILES = [
    "permissive-open",
    "permissive-closed",
    "permissive-proxied",
    "restrictive-open",
    "restrictive-closed",
    "restrictive-proxied",
]

# --- Helper Functions ---

def get_container_path(host_path: str) -> str:
    """Converts a host path to a path usable inside the container."""
    if platform.system() != "Windows":
        return host_path
    
    with_forward_slashes = host_path.replace("\\", "/")
    if ":" in with_forward_slashes:
        drive, _, path_part = with_forward_slashes.partition(":")
        return f"/{drive.lower()}{path_part}"
    return host_path

def should_use_current_user_in_sandbox() -> bool:
    """
    Determines if the sandbox should run with the current user's UID/GID.
    See original TypeScript docstring for detailed behavior.
    """
    env_var = os.environ.get("SANDBOX_SET_UID_GID", "").lower().strip()

    if env_var in ("1", "true"):
        return True
    if env_var in ("0", "false"):
        return False

    if platform.system() == "Linux":
        try:
            with open("/etc/os-release", "r", encoding="utf-8") as f:
                os_release_content = f.read()
            if (
                "ID=debian" in os_release_content
                or "ID=ubuntu" in os_release_content
                or "ID_LIKE=debian" in os_release_content
                or "ID_LIKE=ubuntu" in os_release_content
            ):
                print(
                    "INFO: Defaulting to use current user UID/GID for Debian/Ubuntu-based Linux.",
                    file=sys.stderr,
                )
                return True
        except IOError:
            print(
                "Warning: Could not read /etc/os-release to auto-detect Debian/Ubuntu for UID/GID default.",
                file=sys.stderr,
            )
    return False

def parse_image_name(image: str) -> str:
    """Shortens an image name to be a valid container name."""
    full_name, _, tag = image.partition(":")
    name = full_name.split("/")[-1]
    return f"{name}-{tag}" if tag else name

def get_ports() -> List[str]:
    """Gets a list of ports to expose from the environment variable."""
    return [p.strip() for p in os.environ.get("SANDBOX_PORTS", "").split(",") if p.strip()]

def get_entrypoint(workdir: str) -> List[str]:
    """Constructs the entrypoint command for the container."""
    container_workdir = get_container_path(workdir)
    shell_cmds = []
    
    path_separator = os.pathsep
    
    path_suffix = ""
    if os.environ.get("PATH"):
        for p in os.environ["PATH"].split(path_separator):
            container_path = get_container_path(p)
            if container_path.lower().startswith(container_workdir.lower()):
                path_suffix += f":{container_path}"
    if path_suffix:
        shell_cmds.append(f'export PATH="$PATH{path_suffix}";')

    python_path_suffix = ""
    if os.environ.get("PYTHONPATH"):
        for p in os.environ["PYTHONPATH"].split(path_separator):
            container_path = get_container_path(p)
            if container_path.lower().startswith(container_workdir.lower()):
                python_path_suffix += f":{container_path}"
    if python_path_suffix:
        shell_cmds.append(f'export PYTHONPATH="$PYTHONPATH{python_path_suffix}";')

    project_sandbox_bashrc = os.path.join(SETTINGS_DIRECTORY_NAME, "sandbox.bashrc")
    if os.path.exists(project_sandbox_bashrc):
        shell_cmds.append(f"source {get_container_path(project_sandbox_bashrc)};")

    for p in get_ports():
        shell_cmds.append(
            f"socat TCP4-LISTEN:{p},bind=$(hostname -i),fork,reuseaddr TCP4:127.0.0.1:{p} 2> /dev/null &"
        )
    
    cli_args = [shlex.quote(arg) for arg in sys.argv[1:]]
    
    if os.environ.get("NODE_ENV") == "development":
        cli_cmd = "npm run debug --" if os.environ.get("DEBUG") else "npm rebuild && npm run start --"
    else:
        debug_port = os.environ.get('DEBUG_PORT', '9229')
        cli_cmd = f"node --inspect-brk=0.0.0.0:{debug_port} $(which qwen)" if os.environ.get("DEBUG") else "qwen"

    full_command = " ".join([*shell_cmds, cli_cmd, *cli_args])
    return ["bash", "-c", full_command]

async def image_exists(sandbox_cmd: str, image: str) -> bool:
    """Checks if a container image exists locally."""
    proc = await asyncio.create_subprocess_exec(
        sandbox_cmd, "images", "-q", image,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, _ = await proc.communicate()
    return proc.returncode == 0 and bool(stdout.strip())

async def pull_image(sandbox_cmd: str, image: str) -> bool:
    """Pulls a container image from a registry."""
    print(f"Attempting to pull image {image} using {sandbox_cmd}...", file=sys.stderr)
    proc = await asyncio.create_subprocess_exec(
        sandbox_cmd, "pull", image,
        stdout=sys.stdout,
        stderr=sys.stderr
    )
    await proc.wait()
    if proc.returncode == 0:
        print(f"Successfully pulled image {image}.", file=sys.stderr)
        return True
    else:
        print(f"Failed to pull image {image}.", file=sys.stderr)
        return False

async def ensure_sandbox_image_is_present(sandbox_cmd: str, image: str) -> bool:
    """Ensures the sandbox image is available, pulling it if necessary."""
    print(f"Checking for sandbox image: {image}", file=sys.stderr)
    if await image_exists(sandbox_cmd, image):
        print(f"Sandbox image {image} found locally.", file=sys.stderr)
        return True
    
    print(f"Sandbox image {image} not found locally.", file=sys.stderr)
    if image == LOCAL_DEV_SANDBOX_IMAGE_NAME:
        return False
        
    if await pull_image(sandbox_cmd, image):
        if await image_exists(sandbox_cmd, image):
            print(f"Sandbox image {image} is now available after pulling.", file=sys.stderr)
            return True
        else:
            print(f"Sandbox image {image} still not found after a successful pull attempt.", file=sys.stderr)
            return False
            
    print(f"Failed to obtain sandbox image {image}.", file=sys.stderr)
    return False

def run_sync(command: str):
    """Helper to run a synchronous command."""
    subprocess.run(command, shell=True, check=True, capture_output=True, text=True)

# --- Main Sandbox Logic ---

async def start_sandbox(config: SandboxConfig, node_args: List[str] = [], cli_config: Optional[Config] = None):
    """Main function to configure and start the sandbox environment."""
    if not cli_config:
        cli_config = Config()

    patcher = ConsolePatcher(
        debugMode=cli_config.getDebugMode(),
        stderr=True
    )
    patcher.patch()
    
    proxy_process = None
    sandbox_process = None
    
    def cleanup_processes():
        print("Cleaning up child processes...", file=sys.stderr)
        if proxy_process and proxy_process.poll() is None:
            # Kill the whole process group to stop detached children
            os.killpg(os.getpgid(proxy_process.pid), signal.SIGTERM)
        
        # sandbox_process is usually handled by `docker rm`, but this is a fallback
        if sandbox_process and sandbox_process.poll() is None:
             sandbox_process.terminate()


    atexit.register(cleanup_processes)

    try:
        if config.command == "sandbox-exec":
            # --- macOS Seatbelt Logic ---
            if os.environ.get("BUILD_SANDBOX"):
                print("ERROR: cannot BUILD_SANDBOX when using macOS Seatbelt", file=sys.stderr)
                sys.exit(1)

            profile = os.environ.get("SEATBELT_PROFILE", "permissive-open")
            if profile in BUILTIN_SEATBELT_PROFILES:
                # This assumes the script is run from a location where it can find './sandbox-macos-....sb'
                profile_file = Path(__file__).parent / f"sandbox-macos-{profile}.sb"
            else:
                profile_file = Path(SETTINGS_DIRECTORY_NAME) / f"sandbox-macos-{profile}.sb"

            if not profile_file.exists():
                print(f"ERROR: missing macos seatbelt profile file '{profile_file}'", file=sys.stderr)
                sys.exit(1)
            
            print(f"using macos seatbelt (profile: {profile}) ...", file=sys.stderr)
            
            node_options = " ".join([
                *(['--inspect-brk'] if os.environ.get("DEBUG") else []),
                *node_args,
            ])
            
            # Prepare arguments for sandbox-exec
            args = [
                '-D', f'TARGET_DIR={os.path.realpath(os.getcwd())}',
                '-D', f'TMP_DIR={os.path.realpath(os.path.join("/tmp"))}', # Simplified from os.tmpdir()
                '-D', f'HOME_DIR={os.path.realpath(os.path.expanduser("~"))}',
                '-D', f'CACHE_DIR={os.path.realpath(subprocess.check_output(["getconf", "DARWIN_USER_CACHE_DIR"]).decode().strip())}',
            ]
            
            target_dir = os.path.realpath(cli_config.getTargetDir() or '')
            included_dirs = [
                os.path.realpath(d) 
                for d in cli_config.getWorkspaceContext().getDirectories()
                if os.path.realpath(d) != target_dir
            ]

            MAX_INCLUDE_DIRS = 5
            for i in range(MAX_INCLUDE_DIRS):
                dir_path = included_dirs[i] if i < len(included_dirs) else "/dev/null"
                args.extend(['-D', f'INCLUDE_DIR_{i}={dir_path}'])
            
            # Construct the final command to be executed inside the sandbox
            inner_cmd = " ".join([
                f'SANDBOX=sandbox-exec',
                f'NODE_OPTIONS="{node_options}"',
                *(shlex.quote(arg) for arg in sys.argv),
            ])
            
            args.extend(['-f', str(profile_file), 'sh', '-c', inner_cmd])

            proxy_command = os.environ.get("GEMINI_SANDBOX_PROXY_COMMAND")
            sandbox_env = os.environ.copy()

            if proxy_command:
                proxy = os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy") or os.environ.get("HTTP_PROXY") or os.environ.get("http_proxy") or "http://localhost:8877"
                sandbox_env.update({
                    "HTTPS_PROXY": proxy, "https_proxy": proxy,
                    "HTTP_PROXY": proxy, "http_proxy": proxy
                })
                no_proxy = os.environ.get("NO_PROXY") or os.environ.get("no_proxy")
                if no_proxy:
                    sandbox_env.update({"NO_PROXY": no_proxy, "no_proxy": no_proxy})
                
                print("Starting proxy...", file=sys.stderr)
                proxy_process = subprocess.Popen(
                    proxy_command, shell=True, preexec_fn=os.setsid,
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE
                )
                
                print("Waiting for proxy to start...", file=sys.stderr)
                # Simple sleep, as the original `until curl` is complex to replicate robustly
                await asyncio.sleep(5)
            
            sandbox_process = await asyncio.create_subprocess_exec(
                config.command, *args, env=sandbox_env,
            )
            await sandbox_process.wait()
            return

        # --- Docker/Podman Logic ---
        print(f"hopping into sandbox (command: {config.command}) ...", file=sys.stderr)
        
        # gc_path = os.path.realpath(sys.argv[0]) # Simplified from original
        workdir = os.path.abspath(os.getcwd())
        container_workdir = get_container_path(workdir)

        if os.environ.get("BUILD_SANDBOX"):
            print("Building sandbox...", file=sys.stderr)
            # This part is highly specific to the original project's structure.
            # A generic implementation would require more context.
            print("BUILD_SANDBOX logic needs to be adapted from the original JS project.", file=sys.stderr)
            sys.exit(1)

        if not await ensure_sandbox_image_is_present(config.command, config.image):
            remedy = (
                "Try building it locally from the source repository."
                if config.image == LOCAL_DEV_SANDBOX_IMAGE_NAME
                else "Please check the image name and your network connection."
            )
            print(f"ERROR: Sandbox image '{config.image}' is missing or could not be pulled. {remedy}", file=sys.stderr)
            sys.exit(1)
        
        args = ["run", "-i", "--rm", "--init", "--workdir", container_workdir]

        if os.environ.get("SANDBOX_FLAGS"):
            args.extend(shlex.split(os.environ["SANDBOX_FLAGS"]))
        
        if sys.stdin.isatty():
            args.append("-t")

        args.extend(["--volume", f"{workdir}:{container_workdir}"])

        if not os.path.exists(USER_SETTINGS_DIR):
            os.makedirs(USER_SETTINGS_DIR)
        
        user_settings_dir_in_sandbox = get_container_path(f"/home/node/{SETTINGS_DIRECTORY_NAME}")
        args.extend(["--volume", f"{USER_SETTINGS_DIR}:{user_settings_dir_in_sandbox}"])
        if user_settings_dir_in_sandbox != get_container_path(USER_SETTINGS_DIR):
            args.extend(["--volume", f"{USER_SETTINGS_DIR}:{get_container_path(USER_SETTINGS_DIR)}"])

        tmp_dir = os.path.realpath("/tmp") # Simplified
        args.extend(["--volume", f"{tmp_dir}:{get_container_path(tmp_dir)}"])
        
        gcloud_config_dir = os.path.join(os.path.expanduser("~"), ".config", "gcloud")
        if os.path.exists(gcloud_config_dir):
            args.extend(["--volume", f"{gcloud_config_dir}:{get_container_path(gcloud_config_dir)}:ro"])
        
        if os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"):
            adc_file = os.environ["GOOGLE_APPLICATION_CREDENTIALS"]
            if os.path.exists(adc_file):
                args.extend(["--volume", f"{adc_file}:{get_container_path(adc_file)}:ro"])
                args.extend(["--env", f"GOOGLE_APPLICATION_CREDENTIALS={get_container_path(adc_file)}"])

        if os.environ.get("SANDBOX_MOUNTS"):
            for mount in os.environ["SANDBOX_MOUNTS"].split(','):
                mount = mount.strip()
                if not mount: continue
                parts = mount.split(':')
                host_path, container_path, opts = (parts + [None, None, None])[:3]
                container_path = container_path or host_path
                opts = opts or 'ro'
                if not os.path.isabs(host_path):
                    print(f"ERROR: path '{host_path}' in SANDBOX_MOUNTS must be absolute.", file=sys.stderr)
                    sys.exit(1)
                if not os.path.exists(host_path):
                    print(f"ERROR: missing mount path '{host_path}' in SANDBOX_MOUNTS.", file=sys.stderr)
                    sys.exit(1)
                print(f"SANDBOX_MOUNTS: {host_path} -> {container_path} ({opts})", file=sys.stderr)
                args.extend(["--volume", f"{host_path}:{container_path}:{opts}"])

        for p in get_ports():
            args.extend(["--publish", f"{p}:{p}"])

        if os.environ.get("DEBUG"):
            debug_port = os.environ.get("DEBUG_PORT", "9229")
            args.extend(["--publish", f"{debug_port}:{debug_port}"])

        proxy_command = os.environ.get("GEMINI_SANDBOX_PROXY_COMMAND")
        if proxy_command:
            proxy = (os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy") or os.environ.get("HTTP_PROXY") or os.environ.get("http_proxy") or "http://localhost:8877")
            proxy = proxy.replace("localhost", SANDBOX_PROXY_NAME)
            args.extend([
                "--env", f"HTTPS_PROXY={proxy}", "--env", f"https_proxy={proxy}",
                "--env", f"HTTP_PROXY={proxy}", "--env", f"http_proxy={proxy}"
            ])
            no_proxy = os.environ.get("NO_PROXY") or os.environ.get("no_proxy")
            if no_proxy:
                args.extend(["--env", f"NO_PROXY={no_proxy}", "--env", f"no_proxy={no_proxy}"])
            
            run_sync(f"{config.command} network inspect {SANDBOX_NETWORK_NAME} >/dev/null 2>&1 || {config.command} network create --internal {SANDBOX_NETWORK_NAME}")
            args.extend(["--network", SANDBOX_NETWORK_NAME])
            run_sync(f"{config.command} network inspect {SANDBOX_PROXY_NAME} >/dev/null 2>&1 || {config.command} network create {SANDBOX_PROXY_NAME}")


        image_name = parse_image_name(config.image)
        # Simplified container name logic
        container_name = f"{image_name}-0"
        args.extend(["--name", container_name, "--hostname", container_name])
        
        # Pass through various environment variables
        env_vars_to_pass = [
            'GEMINI_API_KEY', 'GOOGLE_API_KEY', 'OPENAI_API_KEY', 'TAVILY_API_KEY',
            'OPENAI_BASE_URL', 'OPENAI_MODEL', 'GOOGLE_GENAI_USE_VERTEXAI',
            'GOOGLE_GENAI_USE_GCA', 'GOOGLE_CLOUD_PROJECT', 'GOOGLE_CLOUD_LOCATION',
            'GEMINI_MODEL', 'TERM', 'COLORTERM', 'QWEN_CODE_IDE_SERVER_PORT',
            'QWEN_CODE_IDE_WORKSPACE_PATH', 'TERM_PROGRAM'
        ]
        for var in env_vars_to_pass:
            if os.environ.get(var):
                args.extend(["--env", f"{var}={os.environ[var]}"])

        if os.environ.get("SANDBOX_ENV"):
             for env in os.environ["SANDBOX_ENV"].split(','):
                env = env.strip()
                if env and '=' in env:
                    args.extend(['--env', env])
        
        all_node_options = " ".join(filter(None, [os.environ.get("NODE_OPTIONS"), *node_args]))
        if all_node_options:
            args.extend(['--env', f'NODE_OPTIONS="{all_node_options}"'])
            
        args.extend(['--env', f'SANDBOX={container_name}'])
        
        user_flag = ''
        final_entrypoint = get_entrypoint(workdir)

        if os.environ.get("GEMINI_CLI_INTEGRATION_TEST") == "true":
            args.extend(["--user", "root"])
            user_flag = "--user root"
        elif should_use_current_user_in_sandbox():
            args.extend(["--user", "root"])
            uid, gid = os.getuid(), os.getgid()
            username = 'gemini'
            home_dir = get_container_path(os.path.expanduser('~'))

            setup_user_cmds = (
                f"groupadd -f -g {gid} {username} && "
                f"id -u {username} &>/dev/null || useradd -o -u {uid} -g {gid} -d {home_dir} -s /bin/bash {username}"
            )
            
            original_command = final_entrypoint[2]
            su_command = f"su -p {username} -c {shlex.quote(original_command)}"
            final_entrypoint[2] = f"{setup_user_cmds} && {su_command}"

            user_flag = f"--user {uid}:{gid}"
            args.extend(["--env", f"HOME={os.path.expanduser('~')}"])

        args.append(config.image)
        args.extend(final_entrypoint)

        if proxy_command:
            proxy_container_command = (
                f"{config.command} run --rm --init {user_flag} --name {SANDBOX_PROXY_NAME} "
                f"--network {SANDBOX_PROXY_NAME} -p 8877:8877 -v {os.getcwd()}:{workdir} "
                f"--workdir {workdir} {config.image} {proxy_command}"
            )
            proxy_process = subprocess.Popen(
                proxy_container_command, shell=True, preexec_fn=os.setsid,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )

            def stop_proxy_container():
                print("stopping proxy container ...", file=sys.stderr)
                run_sync(f"{config.command} rm -f {SANDBOX_PROXY_NAME}")

            atexit.register(stop_proxy_container)
            
            print("Waiting for proxy container to start...", file=sys.stderr)
            await asyncio.sleep(5) # Simplified wait
            await asyncio.create_subprocess_shell(
                f"{config.command} network connect {SANDBOX_NETWORK_NAME} {SANDBOX_PROXY_NAME}"
            )

        sandbox_process = await asyncio.create_subprocess_exec(config.command, *args)
        await sandbox_process.wait()

    finally:
        patcher.cleanup()

# --- Example Usage ---
if __name__ == "__main__":
    # This is an example of how you might run the function.
    # You would need to determine the sandbox command (docker, podman)
    # and the image name based on your environment.
    
    print("--- Python Sandbox Starter ---")
    
    # Example configuration:
    sandbox_cmd = "docker" # or "podman"
    image_name = "ubuntu:latest" # A public image for demonstration
    
    example_config = SandboxConfig(command=sandbox_cmd, image=image_name)
    
    print(f"Starting sandbox with command: '{sandbox_cmd}' and image: '{image_name}'")
    print("NOTE: This example uses a basic 'ubuntu' image and will likely not run a complex node app.")
    print("The logic is designed for a custom-built sandbox image.")
    print("Press Ctrl+C to exit.")
    
    # To test the full logic, you would set environment variables like:
    # export SANDBOX_PORTS=8080,8081
    # export DEBUG=true
    
    try:
        # In a real CLI, you'd parse sys.argv to get node_args and cli_config
        asyncio.run(start_sandbox(example_config, node_args=[], cli_config=Config()))
    except KeyboardInterrupt:
        print("\nExiting.")
    except Exception as e:
        print(f"\nAn error occurred: {e}", file=sys.stderr)
