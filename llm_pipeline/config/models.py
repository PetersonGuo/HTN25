from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

class PipelineConfig(BaseModel):
    default_model: str = Field(..., description='Default model if agent does not override')
    template_namespace: str = Field('templates', description='Base directory for templates')
    timeout_seconds: int = Field(60, ge=1, le=600)
    max_output_tokens: int = Field(1024, ge=16, le=8192)
    output_schema: Dict[str, Any] = Field(
        ...,  # required
        description='JSON Schema to validate LLM output (required)'
    )
    json_retry_attempts: int = Field(
        1,
        ge=1,
        le=5,
        description='Number of attempts to re-ask the model to conform to schema'
    )

class AgentDecision(BaseModel):
    model: str
    template_name: str
    tools_allowed: Optional[Dict[str, Any]] = None
