from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from enum import Enum

class ExecutorType(str, Enum):
    CEREBRAS = "cerebras"
    OPENAI = "openai"

class PipelineConfig(BaseModel):
    default_model: str = Field(..., description='Model to use if agent does not override')
    default_executor: ExecutorType = Field(ExecutorType.CEREBRAS, description='Default executor type')
    template_namespace: str = Field('templates', description='Base directory for templates')
    timeout_seconds: int = Field(60, ge=1, le=600, description='Request timeout in seconds')
    max_output_tokens: int = Field(1024, ge=16, le=8192, description='Maximum output tokens')
    output_schema: Dict[str, Any] = Field(..., description='JSON Schema to validate LLM output')
    json_retry_attempts: int = Field(3, ge=1, le=5, description='Number of retry attempts for schema validation')

class AgentDecision(BaseModel):
    model: str
    template_name: str
    executor_type: ExecutorType
    tools_allowed: Optional[Dict[str, Any]] = None
