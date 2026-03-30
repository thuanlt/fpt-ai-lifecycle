from dataclasses import dataclass

@dataclass
class ModelInfo:
    model_name: str = ""
    api_key: str = "faked"
    base_url: str = "http://localhost:4000/v1" # Default to a local server litellm
    max_tokens: int = -1
    temperature: float = 0.0
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    use_responses_api: bool = False