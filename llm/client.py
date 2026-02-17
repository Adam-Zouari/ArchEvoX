import instructor
import litellm
import yaml
from pathlib import Path
from pydantic import BaseModel

# Load config
_config_path = Path(__file__).resolve().parent.parent / "config.yaml"
with open(_config_path) as f:
    _config = yaml.safe_load(f)

_model_name = _config["llm"]["model"]
_max_retries = _config["llm"].get("max_retries", 3)

# Patch litellm with instructor for structured output
client = instructor.from_litellm(litellm.acompletion)


async def call_llm(
    system_prompt: str,
    user_message: str,
    response_model: type[BaseModel],
    temperature: float = 0.7,
    max_retries: int | None = None,
) -> BaseModel:
    """Core LLM call function used by all stages.
    Every call returns a validated Pydantic model."""
    return await client(
        model=_model_name,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        response_model=response_model,
        temperature=temperature,
        max_retries=max_retries or _max_retries,
    )
