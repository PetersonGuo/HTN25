import os
import httpx
from typing import Dict, Any, Optional, List


class CerebrasExecutor:
    def __init__(self, timeout: int = 60, max_output_tokens: int = 1024):
        self.timeout = timeout
        self.max_output_tokens = max_output_tokens
        self.api_url = os.getenv('CEREBRAS_API_URL')

    def generate(self, prompt: str, model: str, images: Optional[List[str]] = None) -> Dict[str, Any]:
        if images is not None:
            raise ValueError("The 'images' parameter is not supported for Cerebras API.")

        api_key = os.getenv('CEREBRAS_API_KEY')
        if not api_key:
            raise ValueError("Cerebras API key required. Set CEREBRAS_API_KEY environment variable")
        
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
        }
        payload = {
            'model': model,
            'prompt': prompt,
            'max_tokens': self.max_output_tokens,
        }
        
        with httpx.Client(timeout=self.timeout) as client:
            resp = client.post(self.api_url, headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()

        text = data['choices'][0].get('text') or data['choices'][0]['message']['content']
        return {'output': text, 'usage': data.get('usage', {})}
