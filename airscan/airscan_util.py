import json
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
    print("-" * 60)
    print(b_str)
    print("-" * 60)


