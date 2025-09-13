import json
import sys
import click
from dotenv import load_dotenv
from .registry.template_registry import TemplateRegistry
from .pipeline import Pipeline
from .config.models import PipelineConfig
from pydantic import ValidationError

@click.command()
@click.option('--input', 'input_json', type=click.File('r'), default='-')
@click.option('--config', 'config_json', type=click.File('r'), required=True)
@click.option('--templates', 'templates_dir', type=click.Path(exists=True), default='templates')
def main(input_json, config_json, templates_dir):
    load_dotenv()
    input_data = json.load(input_json)
    config_data = json.load(config_json)
    # Pre-check for required output_schema with friendly error
    if 'output_schema' not in config_data:
        raise click.ClickException("Config must include 'output_schema' (a JSON Schema object).")
    if not isinstance(config_data.get('output_schema'), dict):
        raise click.ClickException("'output_schema' must be a JSON object (dictionary).")
    try:
        cfg = PipelineConfig(**config_data)
    except ValidationError as ve:
        raise click.ClickException(f"Invalid configuration: {ve}")
    registry = TemplateRegistry(templates_dir)
    pipeline = Pipeline(registry)
    result = pipeline.run(input_data=input_data, config=cfg)
    json.dump(result, sys.stdout, indent=2)
    sys.stdout.write("\n")

if __name__ == '__main__':
    main()
