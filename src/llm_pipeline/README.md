# Configurable LLM Pipeline

A configurable pipeline that renders Jinja prompts and calls an LLM (Cerebras) selected by an external agent.

## Setup

- Python 3.10+
- `pip install -r requirements.txt`
- Set `CEREBRAS_API_KEY` in environment (or `.env`).
- Optionally set `CEREBRAS_API_URL` (defaults to `https://api.cerebras.ai/v1/completions`).

## Usage

```bash
python -m llm_pipeline.cli --config llm_pipeline/examples/config.json --input llm_pipeline/examples/input.json --templates templates
```

## Structure

- `llm_pipeline/` core package
- `templates/` versioned templates
- `examples/` sample input/config
