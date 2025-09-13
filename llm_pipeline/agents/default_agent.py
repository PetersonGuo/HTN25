from typing import Dict, Any
from ..config.models import PipelineConfig, AgentDecision

class DefaultAgent:
    def decide(self, input_data: Dict[str, Any], config: PipelineConfig) -> AgentDecision:
        template_name = input_data.get('template_name', 'qna')
        model = input_data.get('model') or config.default_model
        executor_type = config.default_executor
            
        return AgentDecision(
            model=model,
            template_name=template_name,
            executor_type=executor_type,
        )
