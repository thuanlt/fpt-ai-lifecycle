# ./utils/logger.py
import os
import json
from datetime import datetime
from rich.panel import Panel
from rich.console import Console
from rich.pretty import pretty_repr
from rich.text import Text

class Logger:
    """
    Manages session-based file logging and formatted console output for the agent framework.
    """
    def __init__(self, base_dir: str = "logs"):
        """
        Initializes the logger and creates a unique directory for the current session.
        """
        self.session_id = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.log_dir = os.path.join(base_dir, self.session_id)
        os.makedirs(self.log_dir, exist_ok=True)
        self.console = Console()
        self.agent_colors = {
            "OrchestratorAgent": "green",
            "PlannerAgent": "cyan",
            "QCAgent": "magenta",
            "VerifierAgent": "yellow",
            "ToolCall": "white",
        }
        print(f"DEBUG: Logging session started. Log files will be saved in: {os.path.abspath(self.log_dir)}")

        self.current_panel = None
        self.current_text = None

    def console_log(self, step_index: int, agent_name: str, title: str):
        """
        Prints a colored and bounded message to the console for an agent's step.
        """
        color = self.agent_colors.get(agent_name, "white")
        # self.current_text = Text(f"[{color}]{title}[/]", style=color)
        
        self.current_panel = Panel(
            # f"[bold]{title}[/bold]",
            f"{title}",
            title=f"[bold]{agent_name}[/bold]",
            subtitle=f"Step {step_index}",
            border_style=color,
            expand=False,
            padding=(1, 2)
        )
        self.console.print(self.current_panel)

    def log_agent_step(self, step_index: int, agent_name: str, system_prompt: str, user_prompt: str, llm_response: object, tool_responses: list = None):
        """
        Logs the detailed inputs and outputs of an agent's step to a text file.
        """
        timestamp = datetime.now().strftime('%H%M%S_%f')
        filename = f"{step_index}-{agent_name}-{timestamp}.txt"
        filepath = os.path.join(self.log_dir, filename)

        # Use rich's pretty_repr for complex objects like the LLM response
        pretty_llm_response = pretty_repr(llm_response)

        content = f"""==================================================
STEP: {step_index}
AGENT: {agent_name}
TIMESTAMP: {datetime.now().isoformat()}
==================================================

########## SYSTEM PROMPT ##########
{system_prompt}


########## USER PROMPT ##########
{user_prompt}


########## LLM RESPONSE ##########
{pretty_llm_response}
"""

        if tool_responses:
            content += "\n\n########## TOOL RESPONSES ##########\n"
            for i, res in enumerate(tool_responses):
                content += f"\n--- Response {i+1} ---\n"
                # Pretty print tool responses as well
                content += pretty_repr(res)
                content += "\n"

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)