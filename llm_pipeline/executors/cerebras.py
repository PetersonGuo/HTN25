import os
import httpx
from typing import Dict, Any, Optional

# Default to the OpenAI-compatible completions endpoint. Can be overridden via env or constructor.
DEFAULT_CEREBRAS_API_URL = 'https://api.cerebras.ai/v1/completions'

class CerebrasExecutor:
    def __init__(self, timeout: int = 60, max_output_tokens: int = 1024, api_url: Optional[str] = None):
        self.timeout = timeout
        self.max_output_tokens = max_output_tokens
        # Prefer explicit arg, then environment, then sensible default
        self.api_url = api_url or os.getenv('CEREBRAS_API_URL') or DEFAULT_CEREBRAS_API_URL

    def generate(self, prompt: str, model: str) -> Dict[str, Any]:
        api_key = os.getenv('CEREBRAS_API_KEY')
        if not api_key:
            raise RuntimeError('CEREBRAS_API_KEY is not set')

        if not self.api_url:
            raise RuntimeError('CEREBRAS_API_URL is not set and no default is available')

        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }
        payload: Dict[str, Any] = {
            'model': model,
            'prompt': prompt,
            'max_tokens': self.max_output_tokens,
        }
        try:
            with httpx.Client(timeout=self.timeout) as client:
                resp = client.post(self.api_url, headers=headers, json=payload)
                resp.raise_for_status()
                data = resp.json()
        except httpx.HTTPStatusError as e:
            body = e.response.text if e.response is not None else ''
            raise RuntimeError(f'Cerebras API error {e.response.status_code if e.response else ""}: {body}') from e
        except httpx.HTTPError as e:
            raise RuntimeError(f'HTTP error calling Cerebras API: {e}') from e

        text = (
            (data.get('choices') or [{}])[0].get('text')
            or (data.get('choices') or [{}])[0].get('message', {}).get('content')
        )
        return {'output': text, 'usage': data.get('usage', {})}
