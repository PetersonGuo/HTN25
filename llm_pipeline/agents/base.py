from typing import Protocol, Dict, Any
from ..config.models import PipelineConfig, AgentDecision

class ExternalAgent(Protocol):
    def decide(self, input_data: Dict[str, Any], config: PipelineConfig) -> AgentDecision:
        ...
