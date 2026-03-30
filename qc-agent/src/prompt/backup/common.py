from .qwen_3_32b import Qwen3_32bPrompt
from .qwen_3_235b import Qwen3_235bPrompt
from .glm_4_5 import GLM45Prompt
from .glm_4_5_air import GLM45AirPrompt
from .default_prompt import DefaultPrompt
from .qwen_3_coder_480b import GLM45Coder480BPrompt

default_prompt = DefaultPrompt()

supported_models = [
    Qwen3_32bPrompt(),
    Qwen3_235bPrompt(),
    GLM45Prompt(),
    GLM45AirPrompt(),
    GLM45Coder480BPrompt(),
]

def PROMPT_TEMPLATE(model_name: str = None) -> str:
    """
    Returns the prompt template based on the model name.
    """
    for model in supported_models:
        if model.MODEL() == model_name:
            return model.PROMPT_TEMPLATE()
    return default_prompt.PROMPT_TEMPLATE()

def PLANNER_AGENT_PROFILE(model_name: str = None) -> dict:
    """
    Returns the profile for the planner agent.
    """
    for model in supported_models:
        if model.MODEL() == model_name:
            return model.PLANNER_AGENT_PROFILE()
    return default_prompt.PLANNER_AGENT_PROFILE()

def QC_AGENT_PROFILE(model_name: str = None) -> dict:
    """
    Returns the profile for the QC agent.
    """
    for model in supported_models:
        if model.MODEL() == model_name:
            return model.QC_AGENT_PROFILE()
    return default_prompt.QC_AGENT_PROFILE()

def BROWER_USE_AGENT_PROFILE(model_name: str = None) -> dict:
    """
    Returns the profile for the QC agent.
    """
    for model in supported_models:
        if model.MODEL() == model_name:
            return model.BROWER_USE_AGENT_PROFILE()
    return default_prompt.BROWER_USE_AGENT_PROFILE()

def FILE_MANAGER_AGENT_PROFILE(model_name: str = None) -> dict:
    """
    Returns the profile for the QC agent.
    """
    for model in supported_models:
        if model.MODEL() == model_name:
            return model.FILE_MANAGER_AGENT_PROFILE()
    return default_prompt.FILE_MANAGER_AGENT_PROFILE()

def VERIFIER_AGENT_PROFILE(model_name: str = None) -> dict:
    """
    Returns the profile for the verifier agent.
    """
    for model in supported_models:
        if model.MODEL() == model_name:
            return model.VERIFIER_AGENT_PROFILE()
    return default_prompt.VERIFIER_AGENT_PROFILE()

def ORCHESTRATOR_AGENT_PROFILE(model_name: str = None) -> dict:
    """
    Returns the profile for the orchestrator agent.
    """
    for model in supported_models:
        if model.MODEL() == model_name:
            return model.ORCHESTRATOR_AGENT_PROFILE()
    return default_prompt.ORCHESTRATOR_AGENT_PROFILE()

def EXECUTOR_AGENT_PROFILE(model_name: str = None) -> dict:
    """
    Returns the profile for the orchestrator agent.
    """
    for model in supported_models:
        if model.MODEL() == model_name:
            return model.EXECUTOR_AGENT_PROFILE()
    return default_prompt.EXECUTOR_AGENT_PROFILE()
