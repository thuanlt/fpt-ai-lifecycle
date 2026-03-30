import os
import yaml
from jinja2 import Environment, FileSystemLoader

class PromptBuilder:
    def __init__(self, base_dir="src"):
        self.profiles_dir = os.path.join(base_dir, "agent", "profiles")
        self.skills_dir = os.path.join(base_dir, "agent", "skills")
        
        template_dir = os.path.join(base_dir, "prompt", "templates")
        
        # We ensure standard behaviors of Jinja logic without breaking lines unintentionally
        self.env = Environment(loader=FileSystemLoader(template_dir), trim_blocks=True, lstrip_blocks=True)

    def _load_yaml(self, filepath: str) -> dict:
        if not os.path.exists(filepath):
            return {}
        with open(filepath, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f) or {}

    def load_agent_profile(self, agent_name: str) -> dict:
        """Loads an agent's yaml profile and attaches dynamic skills data."""
        profile_path = os.path.join(self.profiles_dir, f"{agent_name}.yaml")
        profile = self._load_yaml(profile_path)
        
        loaded_skills = []
        if "attached_skills" in profile:
            for skill_file in profile["attached_skills"]:
                skill_path = os.path.join(self.skills_dir, f"{skill_file}.yaml")
                skill_data = self._load_yaml(skill_path)
                if skill_data:
                    loaded_skills.append(skill_data)
        
        profile['skills_data'] = loaded_skills 
        return profile

    def build_system_prompt(self, agent_name: str, dynamic_data: dict = None) -> str:
        """Assembles the final text prompt to be sent to the LLM."""
        data = self.load_agent_profile(agent_name)
        # Note: We provide dynamic_data separately so it doesn't pollute the core agent profile.
        template = self.env.get_template("master_agent.jinja2")
        return template.render(agent=data, data=dynamic_data or {})

# Singleton instance for easy importing
builder = PromptBuilder()
