from typing import Any, Dict, Optional, List
import re
import json
from json import JSONDecodeError
from jsonschema import validate as jsonschema_validate
from jsonschema.exceptions import ValidationError as JSONSchemaValidationError
from .config.models import PipelineConfig, AgentDecision, ExecutorType
from .registry.template_registry import TemplateRegistry
from .executors.cerebras import CerebrasExecutor
from .executors.openai_executor import OpenAIExecutor

class Pipeline:
    def __init__(self, registry: TemplateRegistry, agent):
        self.registry = registry
        self.agent = agent
    
    def _get_executor(self, executor_type: ExecutorType, config: PipelineConfig):
        """Create an executor of the specified type."""
        if executor_type == ExecutorType.CEREBRAS:
            return CerebrasExecutor(timeout=config.timeout_seconds, max_output_tokens=config.max_output_tokens)
        elif executor_type == ExecutorType.OPENAI:
            return OpenAIExecutor(timeout=config.timeout_seconds, max_output_tokens=config.max_output_tokens)
        else:
            raise ValueError(f"Unsupported executor type: {executor_type}")

    def run(self, input_data: Dict[str, Any], config: PipelineConfig) -> Dict[str, Any]:
        decision: AgentDecision = self.agent.decide(input_data, config)
        template = self.registry.get_template(decision.template_name)
        base_prompt = template.render(input_data)
        
        # Use executor type from agent decision
        executor_type = decision.executor_type
        
        executor = self._get_executor(executor_type, config)
        
        # Get images from input_data
        images = input_data.get('images')
        
        # JSON mode: build instructions and validate with retries
        validation_report: Dict[str, Any] = {}
        instructions_parts: List[str] = [
            "You are a JSON-producing assistant.",
            "Return ONLY a JSON object with no extra text, code fences, or commentary.",
        ]
        instructions_parts.append(
            "The JSON MUST strictly conform to the following JSON Schema:"
        )
        instructions_parts.append(json.dumps(config.output_schema, indent=2))
        instructions_parts.append(
            "Do not include fields that are not in the schema. Use correct types."
        )
        instructions = "\n\n".join(instructions_parts)

        attempts = config.json_retry_attempts
        last_text_output: Optional[str] = None
        last_validation_errors: Optional[str] = None
        parsed_answer: Optional[Dict[str, Any]] = None
        result: Dict[str, Any] = {}
        for attempt_index in range(attempts):
            attempt_header = f"Attempt {attempt_index + 1} of {attempts}."
            retry_note = (
                f"Previous output failed schema validation with errors:\n{last_validation_errors}\nPlease correct the JSON to satisfy the schema."
                if last_validation_errors else ""
            )
            prompt = f"{instructions}\n\n{attempt_header}\n{retry_note}\n\n{base_prompt}"
            result = executor.generate(prompt=prompt, model=decision.model, images=images)
            last_text_output = result["output"]
            # Try to parse JSON
            try:
                parsed = json.loads(last_text_output) if isinstance(last_text_output, str) else last_text_output
            except JSONDecodeError:
                parsed = None

            # Fallback: attempt to extract JSON object from noisy output
            if parsed is None and isinstance(last_text_output, str):
                extracted = self._extract_json_from_text(last_text_output)
                parsed = extracted if extracted is not None else None

            # Always validate against required schema
            if parsed is not None:
                try:
                    jsonschema_validate(instance=parsed, schema=config.output_schema)
                    parsed_answer = parsed
                    validation_report = {"valid": True, "errors": []}
                    break
                except JSONSchemaValidationError as ve:
                    last_validation_errors = str(ve)
                    validation_report = {"valid": False, "errors": [last_validation_errors]}
                    continue
            else:
                last_validation_errors = "Model output was not valid JSON."
                validation_report = {"valid": False, "errors": [last_validation_errors]}
                continue

        # Fallback handling after attempts
        if parsed_answer is None:
            # As a last resort, wrap the raw text in an object to keep contract
            answer: Dict[str, Any] = {"text": last_text_output}
        else:
            answer = parsed_answer

        return {
            'answer': answer,
            'usage': result.get('usage', {}),
            'model': decision.model,
            'template': {'name': decision.template_name},
            'validation': validation_report,
        }

    def _extract_json_from_text(self, text: str) -> Optional[Dict[str, Any]]:
        """Attempt to extract a JSON object from noisy LLM output.

        Strategies:
        1) Look for fenced blocks ```json ... ``` or ``` ... ``` containing an object
        2) Scan for the first balanced { ... } object and parse it
        Returns the parsed object if successful, otherwise None.
        """
        # 1) Fenced code block with optional json hint
        fence_pattern = re.compile(r"```(?:json)?\s*([\s\S]*?)\s*```", re.IGNORECASE)
        for match in fence_pattern.finditer(text):
            block = match.group(1)
            obj = self._parse_first_balanced_object(block)
            if obj is not None:
                return obj

        # 2) Scan whole text
        return self._parse_first_balanced_object(text)

    def _parse_first_balanced_object(self, text: str) -> Optional[Dict[str, Any]]:
        in_string = False
        escape = False
        brace_stack = []
        start_index: Optional[int] = None
        for i, ch in enumerate(text):
            if in_string:
                if escape:
                    escape = False
                elif ch == "\\":
                    escape = True
                elif ch == '"':
                    in_string = False
                continue
            else:
                if ch == '"':
                    in_string = True
                    continue
                if ch == '{':
                    if start_index is None:
                        start_index = i
                    brace_stack.append('{')
                    continue
                if ch == '}':
                    if brace_stack:
                        brace_stack.pop()
                        if not brace_stack and start_index is not None:
                            candidate = text[start_index:i+1]
                            try:
                                parsed = json.loads(candidate)
                                if isinstance(parsed, dict):
                                    return parsed
                            except JSONDecodeError:
                                # keep searching for next candidate
                                pass
                            # reset to look for next object after this end
                            start_index = None
                    continue
        return None
