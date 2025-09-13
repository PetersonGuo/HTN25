from jinja2 import Environment, FileSystemLoader, select_autoescape
from typing import Dict
import os

class TemplateRegistry:
    def __init__(self, base_dir: str):
        self.base_dir = base_dir
        self.env = Environment(
            loader=FileSystemLoader(self.base_dir),
            autoescape=select_autoescape(enabled_extensions=('j2',)),
            trim_blocks=True,
            lstrip_blocks=True,
        )

    def get_template(self, name: str):
        """Return a template if found; otherwise return None.

        Looks only for a file at "<name>.j2" under the base directory.
        """
        rel_path = f"{name}.j2"
        full_path = os.path.join(self.base_dir, rel_path)
        if os.path.exists(full_path):
            return self.env.get_template(rel_path)
        return None
