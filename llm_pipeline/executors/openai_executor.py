import os
from typing import Dict, Any, Optional, List
from openai import OpenAI

class OpenAIExecutor:
    def __init__(self, timeout: int = 60, max_output_tokens: int = 1024):
        self.timeout = timeout
        self.max_output_tokens = max_output_tokens
        
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OpenAI API key required. Set OPENAI_API_KEY environment variable")
        
        self.client = OpenAI(api_key=api_key, timeout=self.timeout)

    def generate(self, prompt: str, model: str, images: Optional[List[str]] = None) -> Dict[str, Any]:

        # Build messages array
        if images:
            content = [{"type": "text", "text": prompt}]
            for image_b64 in images:
                image_url = image_b64 if image_b64.startswith('data:') else f"data:image/jpeg;base64,{image_b64}"
                content.append({"type": "image_url", "image_url": {"url": image_url}})
            messages = [{"role": "user", "content": content}]
        else:
            messages = [{"role": "user", "content": prompt}]

        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=self.max_output_tokens,
            response_format={"type": "json_object"} if "json" in prompt.lower() else None
        )
        
        return {
            'output': response.choices[0].message.content,
            'usage': {
                'prompt_tokens': response.usage.prompt_tokens,
                'completion_tokens': response.usage.completion_tokens,
                'total_tokens': response.usage.total_tokens
            } if response.usage else {}
        }
