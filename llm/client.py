import instructor
import litellm
import yaml
import os
from pathlib import Path
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables from .env file
_env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(_env_path)

# Load config
_config_path = Path(__file__).resolve().parent.parent / "config.yaml"
with open(_config_path) as f:
    _config = yaml.safe_load(f)

_model_name = _config["llm"]["model"]
_max_retries = _config["llm"].get("max_retries", 3)
_api_base = _config["llm"].get("api_base")  # e.g. "http://localhost:11434" for Ollama
_api_key_assignments = _config["llm"].get("api_key_assignments", {})

# Set timeout for all models
if _model_name.startswith("ollama"):
    litellm.request_timeout = 600  # 10 minutes for large local models
else:
    # For cloud APIs, set higher timeout for large structured outputs (e.g., portfolio assembly)
    litellm.request_timeout = 300  # 5 minutes (reasonable for cloud APIs)

# Patch litellm with instructor for structured output
# Use JSON mode for Ollama compatibility (avoids tool calling issues)
client = instructor.from_litellm(litellm.acompletion, mode=instructor.Mode.JSON)


async def call_llm(
    system_prompt: str,
    user_message: str,
    response_model: type[BaseModel],
    temperature: float = 0.7,
    max_retries: int | None = None,
    stage: str | None = None,
) -> BaseModel:
    """Core LLM call function used by all stages.
    Every call returns a validated Pydantic model.
    Supports both cloud APIs and local models (Ollama).

    Args:
        stage: Optional stage name for API key distribution (e.g., 'paradigm_agents')
    """
    kwargs = dict(
        model=_model_name,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        response_model=response_model,
        temperature=temperature,
        max_retries=max_retries or _max_retries,
    )

    # Pass api_base for local models (Ollama, LM Studio, etc.)
    if _api_base:
        kwargs["api_base"] = _api_base

    # Use stage-specific API key if configured
    if stage and stage in _api_key_assignments:
        api_key_env_var = _api_key_assignments[stage]
        api_key = os.getenv(api_key_env_var)
        if api_key:
            kwargs["api_key"] = api_key

    return await client.chat.completions.create(**kwargs)
