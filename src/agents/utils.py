import os

from jinja2 import Environment, FileSystemLoader


def render_template(filename: str, variables: dict = None):
    template_dir = os.path.join(os.path.dirname(__file__), "prompts")
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template(filename)
    if variables:
        return template.render(variables)
    return template.render()
