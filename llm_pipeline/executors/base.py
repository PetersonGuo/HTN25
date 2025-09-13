from typing import Protocol, Dict, Any, Optional, List

class LLMExecutor(Protocol):
    def generate(self, prompt: str, model: str, images: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Generate text using the LLM API.
        
        Args:
            prompt: Text prompt
            model: Model name/identifier
            images: Optional list of base64-encoded images
            
        Returns:
            Dict containing 'output' (generated text) and 'usage' (token usage stats)
        """
        ...
