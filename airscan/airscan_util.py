import json
import click
from pygments import highlight, lexers, formatters


def cf_json(json_obj):
    """Return nicely formatted/colored json"""
    formatted_json = json.dumps(json_obj, sort_keys=True, indent=4)
    colorful_json = highlight(
        formatted_json, 
        lexers.JsonLexer(), 
        formatters.TerminalFormatter()
    )
    return colorful_json


def banner(b_str, color='green'):
    """Print a nice banner"""
    click.secho("-" * 60, fg=color)
    click.secho(b_str, fg=color)
    click.secho("-" * 60, fg=color)


