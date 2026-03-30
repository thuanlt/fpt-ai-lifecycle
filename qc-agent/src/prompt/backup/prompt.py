# File: prompt.py
# This file contains the prompt definitions used in the application.
# Base class for prompts

from abc import ABC, abstractmethod

class Prompt(ABC):

    @abstractmethod
    def MODEL(self, *args, **kwargs):
        """Returns the orchestration prompt."""
        pass

    @abstractmethod
    def PROMPT_TEMPLATE(self, *args, **kwargs):
        """Returns the orchestration prompt."""
        pass

    @abstractmethod
    def PLANNER_AGENT_PROFILE(self, *args, **kwargs):
        """Returns the orchestration prompt."""
        pass

    @abstractmethod
    def QC_AGENT_PROFILE(self, *args, **kwargs):
        """Returns the orchestration prompt."""
        pass

    @abstractmethod
    def VERIFIER_AGENT_PROFILE(self, *args, **kwargs):
        """Returns the planner prompt."""
        pass

    @abstractmethod
    def ORCHESTRATOR_AGENT_PROFILE(self, *args, **kwargs):
        """Returns the planner prompt."""
        pass

    @abstractmethod
    def BROWER_USE_AGENT_PROFILE(self, *args, **kwargs):
        """Returns the planner prompt."""
        pass
    
    @abstractmethod
    def FILE_MANAGER_AGENT_PROFILE(self, *args, **kwargs):
        """Returns the planner prompt."""
        pass

    @abstractmethod
    def EXECUTOR_AGENT_PROFILE(self, *args, **kwargs):
        """Returns the planner prompt."""
        pass