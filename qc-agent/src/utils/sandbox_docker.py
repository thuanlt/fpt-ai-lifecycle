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
from typing import List, Optional

# --- Configuration Placeholders ---
# In a real application, these would be properly defined classes.
class SandboxConfig:
    def __init__(self, command: str, image: str):
        self.command = command
        self.image = image

class ConsolePatcher:
    """A placeholder for a class that would patch stdout/stderr."""
    def __init__(self, debugMode: bool, stderr: bool):
        pass
    def patch(self):
        print("INFO: Console patcher activated.", file=sys.stderr)
    def cleanup(self):
        print("INFO: Console patcher cleaned up.", file=sys.stderr)

# --- Constants ---
SETTINGS_DIRECTORY_NAME = ".qc-agent"
USER_SETTINGS_DIR = os.path.join(os.path.expanduser("~"), SETTINGS_DIRECTORY_NAME)
LOCAL_DEV_SANDBOX_IMAGE_NAME = "qc-agent-sandbox"
SANDBOX_NETWORK_NAME = "qc-agent-sandbox"
SANDBOX_PROXY_NAME = "qc-agent-sandbox-proxy"

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
    """
    env_var = os.environ.get("SANDBOX_SET_UID_GID", "").lower().strip()
    if env_var in ("1", "true"):
        return True
    if env_var in ("0", "false"):
        return False
    # Default to True on Linux for better file permission handling
    return platform.system() == "Linux"

def parse_image_name(image: str) -> str:
    """Shortens an image name to be a valid container name."""
    full_name, _, tag = image.partition(":")
    name = full_name.split("/")[-1]
    return f"{name}-{tag}" if tag else name

def get_ports() -> List[str]:
    """Gets a list of ports to expose from the environment variable."""
    return [p.strip() for p in os.environ.get("SANDBOX_PORTS", "").split(",") if p.strip()]

def get_entrypoint(workdir: str, cli_cmd: str) -> List[str]:
    """Constructs the entrypoint command for the container."""
    container_workdir = get_container_path(workdir)
    shell_cmds = []
    
    # Append project-specific paths to PATH and PYTHONPATH inside the container
    path_separator = os.pathsep
    if os.environ.get("PATH"):
        path_suffix = "".join(f":{get_container_path(p)}" for p in os.environ["PATH"].split(path_separator) if get_container_path(p).lower().startswith(container_workdir.lower()))
        if path_suffix:
            shell_cmds.append(f'export PATH="$PATH{path_suffix}";')

    if os.environ.get("PYTHONPATH"):
        python_path_suffix = "".join(f":{get_container_path(p)}" for p in os.environ["PYTHONPATH"].split(path_separator) if get_container_path(p).lower().startswith(container_workdir.lower()))
        if python_path_suffix:
            shell_cmds.append(f'export PYTHONPATH="$PYTHONPATH{python_path_suffix}";')

    # Source a project-specific bashrc if it exists
    project_sandbox_bashrc = os.path.join(SETTINGS_DIRECTORY_NAME, "sandbox.bashrc")
    if os.path.exists(project_sandbox_bashrc):
        shell_cmds.append(f"source {get_container_path(project_sandbox_bashrc)};")

    # Forward ports using socat for network accessibility
    for p in get_ports():
        shell_cmds.append(
            f"socat TCP4-LISTEN:{p},bind=$(hostname -i),fork,reuseaddr TCP4:127.0.0.1:{p} 2> /dev/null &"
        )
    
    cli_args = [shlex.quote(arg) for arg in sys.argv[1:]]
    
    # The actual command to run inside the sandbox
    # cli_cmd = "echo '--- Hello from inside the Docker sandbox! ---' && sleep 2 && echo '--- Sandbox finished. ---' && ls -lia"
    
    full_command = " ".join([*shell_cmds, cli_cmd, *cli_args])
    return ["bash", "-c", full_command]

async def image_exists(sandbox_cmd: str, image: str) -> bool:
    """Checks if a container image exists locally."""
    proc = await asyncio.create_subprocess_exec(
        sandbox_cmd, "images", "-q", image,
        stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    stdout, _ = await proc.communicate()
    return proc.returncode == 0 and bool(stdout.strip())

async def pull_image(sandbox_cmd: str, image: str) -> bool:
    """Pulls a container image from a registry."""
    print(f"Attempting to pull image '{image}' using {sandbox_cmd}...", file=sys.stderr)
    proc = await asyncio.create_subprocess_exec(
        sandbox_cmd, "pull", image, stdout=sys.stdout, stderr=sys.stderr
    )
    await proc.wait()
    return proc.returncode == 0

async def ensure_sandbox_image_is_present(sandbox_cmd: str, image: str) -> bool:
    """Ensures the sandbox image is available, pulling it if necessary."""
    print(f"Checking for sandbox image: {image}", file=sys.stderr)
    if await image_exists(sandbox_cmd, image):
        print(f"Sandbox image '{image}' found locally.", file=sys.stderr)
        return True
    
    print(f"Sandbox image '{image}' not found locally.", file=sys.stderr)
    if image == LOCAL_DEV_SANDBOX_IMAGE_NAME:
        return False
        
    if await pull_image(sandbox_cmd, image):
        print(f"Successfully pulled image '{image}'.", file=sys.stderr)
        return True
            
    print(f"Failed to obtain sandbox image '{image}'.", file=sys.stderr)
    return False

def run_sync_command(command: str, check=False) -> subprocess.CompletedProcess:
    """Helper to run a synchronous command, ignoring non-zero exit codes unless check=True."""
    return subprocess.run(command, shell=True, check=check, capture_output=True, text=True)

# --- Main Sandbox Logic ---

async def start_docker_sandbox(cli_cmd: str, config: SandboxConfig, node_args: List[str] = [], capture_output: bool = False):
    """Main function to configure and start the Docker/Podman sandbox."""
    patcher = ConsolePatcher(debugMode=bool(os.environ.get('DEBUG')), stderr=True)
    patcher.patch()

    sandbox_process = None
    proxy_process = None

    def cleanup_processes():
        print("Cleaning up child processes...", file=sys.stderr)
        if proxy_process and proxy_process.poll() is None:
            os.killpg(os.getpgid(proxy_process.pid), signal.SIGTERM)
        
        if sandbox_process and sandbox_process.returncode is None:
            try:
                sandbox_process.terminate()
            except ProcessLookupError:
                pass # Already terminated

    atexit.register(cleanup_processes)

    try:
        print(f"Hopping into sandbox (command: {config.command}) ...", file=sys.stderr)
        
        workdir = os.path.abspath(os.getcwd())
        container_workdir = get_container_path(workdir)

        if not await ensure_sandbox_image_is_present(config.command, config.image):
            remedy = ("Try building it locally." if config.image == LOCAL_DEV_SANDBOX_IMAGE_NAME
                      else "Please check the image name and your network connection.")
            print(f"ERROR: Sandbox image '{config.image}' is missing. {remedy}", file=sys.stderr)
            sys.exit(1)
        
        args = ["run", "-i", "--rm", "--init", "--workdir", container_workdir]

        if os.environ.get("SANDBOX_FLAGS"):
            args.extend(shlex.split(os.environ["SANDBOX_FLAGS"]))
        
        if sys.stdin.isatty():
            args.append("-t")
        
        if platform.system() == "Linux":
            args.extend(["--add-host=host.docker.internal:host-gateway"])

        # --- Volume Mounts ---
        args.extend(["--volume", f"{workdir}:{container_workdir}"])

        if not os.path.exists(USER_SETTINGS_DIR):
            os.makedirs(USER_SETTINGS_DIR)
        args.extend(["--volume", f"{USER_SETTINGS_DIR}:{get_container_path(USER_SETTINGS_DIR)}"])

        tmp_dir = os.path.realpath("/tmp")
        args.extend(["--volume", f"{tmp_dir}:{get_container_path(tmp_dir)}"])
        
        gcloud_config_dir = os.path.join(os.path.expanduser("~"), ".config", "gcloud")
        if os.path.exists(gcloud_config_dir):
            args.extend(["--volume", f"{gcloud_config_dir}:{get_container_path(gcloud_config_dir)}:ro"])
        
        if os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"):
            adc_file = os.environ["GOOGLE_APPLICATION_CREDENTIALS"]
            if os.path.exists(adc_file):
                args.extend(["--volume", f"{adc_file}:{get_container_path(adc_file)}:ro"])
                args.extend(["--env", f"GOOGLE_APPLICATION_CREDENTIALS={get_container_path(adc_file)}"])

        # --- Networking ---
        for p in get_ports():
            args.extend(["--publish", f"{p}:{p}"])

        if os.environ.get("DEBUG"):
            debug_port = os.environ.get("DEBUG_PORT", "9229")
            args.extend(["--publish", f"{debug_port}:{debug_port}"])

        proxy_command = os.environ.get("GEMINI_SANDBOX_PROXY_COMMAND")
        if proxy_command:
            proxy = os.environ.get("HTTPS_PROXY", "http://localhost:8877").replace("localhost", SANDBOX_PROXY_NAME)
            args.extend([f"--env", f"HTTPS_PROXY={proxy}", f"--env", f"HTTP_PROXY={proxy}"])
            if os.environ.get("NO_PROXY"):
                args.extend(["--env", f"NO_PROXY={os.environ['NO_PROXY']}"])
            
            run_sync_command(f"{config.command} network inspect {SANDBOX_NETWORK_NAME} >/dev/null 2>&1 || {config.command} network create {SANDBOX_NETWORK_NAME}")
            # run_sync_command(f"{config.command} network inspect {SANDBOX_NETWORK_NAME} >/dev/null 2>&1 || {config.command} network create --internal {SANDBOX_NETWORK_NAME}") # this one is isolated
            args.extend(["--network", SANDBOX_NETWORK_NAME])

        # --- Identity and Naming ---
        container_name = f"{parse_image_name(config.image)}-{os.getpid()}"
        args.extend(["--name", container_name, "--hostname", container_name])
        
        # --- Environment Variables ---
        env_vars_to_pass = [
            'GEMINI_API_KEY', 'GOOGLE_API_KEY', 'OPENAI_API_KEY', 'TERM',
            'COLORTERM', 'DEBUG', 'DEBUG_PORT'
        ]
        for var in env_vars_to_pass:
            if os.environ.get(var):
                args.extend(["--env", f"{var}={os.environ[var]}"])

        if os.environ.get("SANDBOX_ENV"):
             for env in os.environ["SANDBOX_ENV"].split(','):
                if env.strip() and '=' in env:
                    args.extend(['--env', env.strip()])
        
        args.extend(['--env', f'SANDBOX={container_name}'])
        
        # --- User and Permissions ---
        final_entrypoint = get_entrypoint(workdir, cli_cmd)
        user_flag_for_proxy = ''

        if should_use_current_user_in_sandbox() and platform.system() != "Windows":
            args.extend(["--user", "root"]) # Start as root to create the user
            uid, gid = os.getuid(), os.getgid()
            username = "sandbox"
            home_dir = f"/home/{username}"

            setup_user_cmds = (
                f"groupadd -f -g {gid} {username} && "
                f"id -u {username} &>/dev/null || useradd -o -u {uid} -g {gid} -m -d {home_dir} -s /bin/bash {username}"
            )

            print(setup_user_cmds)
            
            original_command = final_entrypoint[2]
            su_command = f"su -p {username} -c {shlex.quote(original_command)}"
            final_entrypoint[2] = f"{setup_user_cmds} && {su_command}"

            user_flag_for_proxy = f"--user {uid}:{gid}"
            args.extend(["--env", f"HOME={home_dir}"])
        
        # --- Final Assembly ---
        args.append(config.image)
        args.extend(final_entrypoint)

        # --- Proxy Container (if needed) ---
        if proxy_command:
            proxy_container_command = (
                f"{config.command} run --rm --init {user_flag_for_proxy} --name {SANDBOX_PROXY_NAME} "
                f"-p 8877:8877 -v {workdir}:{container_workdir} "
                f"--workdir {container_workdir} {config.image} {proxy_command}"
            )
            proxy_process = subprocess.Popen(
                proxy_container_command, shell=True, preexec_fn=os.setsid,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )

            def stop_proxy_container():
                print("Stopping proxy container...", file=sys.stderr)
                run_sync_command(f"{config.command} rm -f {SANDBOX_PROXY_NAME}")
            atexit.register(stop_proxy_container)
            
            print("Waiting for proxy container to start...", file=sys.stderr)
            await asyncio.sleep(5)
            await asyncio.create_subprocess_shell(f"{config.command} network connect {SANDBOX_NETWORK_NAME} {SANDBOX_PROXY_NAME}")

        # --- Execution ---
        print(f"Executing: {config.command} {' '.join(args)}", file=sys.stderr)
        
        if capture_output:
            sandbox_process = await asyncio.create_subprocess_exec(
                config.command, *args,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await sandbox_process.communicate()
            return {
                "stdout": stdout.decode(errors='replace'),
                "stderr": stderr.decode(errors='replace'),
                "exit_code": sandbox_process.returncode
            }
        else:
            sandbox_process = await asyncio.create_subprocess_exec(config.command, *args)
            await sandbox_process.wait()
            return None

    finally:
        patcher.cleanup()

# --- Example Usage ---
if __name__ == "__main__":
    print("--- Python Docker Sandbox Starter ---")
    
    # Configuration for the sandbox
    sandbox_cmd = "docker"  # or "podman"
    image_name = "qc-agent-framework:latest"  # A public image for a simple demonstration
    
    example_config = SandboxConfig(command=sandbox_cmd, image=image_name)
    
    print(f"Starting sandbox with command: '{sandbox_cmd}' and image: '{image_name}'")
    print("This example runs a simple echo command inside the container.")
    print("Press Ctrl+C to exit.")
    
    try:
        # asyncio.run(start_docker_sandbox("echo '--- Hello from inside the Docker sandbox! ---' && sleep 2 && echo '--- Sandbox finished. ---' && ls -lia", example_config))
        asyncio.run(start_docker_sandbox("chmod 777 tmp && ls -liah tmp/ && HF_HOME=`pwd`/.huggingface python3 src/app.py", example_config))
    except KeyboardInterrupt:
        print("\nExiting.")
    except Exception as e:
        print(f"\nAn error occurred: {e}", file=sys.stderr)