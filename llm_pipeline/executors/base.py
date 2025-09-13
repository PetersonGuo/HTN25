from typing import Protocol, Dict, Any

class LLMExecutor(Protocol):
    def generate(self, prompt: str, model: str) -> Dict[str, Any]:
        ...
