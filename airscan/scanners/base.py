import os
import json
from pygments import highlight, lexers, formatters


class BaseScanner(object):

    def _chunks(self, l, n):
        """Splits 'l' into a set of lists (max size 'n')"""
        chunks = []
        for i in range(0, len(l), n):
            chunks.append(l[i:i + n])
        return chunks

    def _get_json_url_or_file(self, url_file):
        url, file_path = url_file
        base_path = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(base_path, file_path)
        try:
            print("Loading Json from URL: %s" % url)
            json_def = requests.get(url).json()
        except:
            print("Request failed, loading default file: %s" % file_path)
            with open(file_path, "r") as jf:
                json_def = json.load(jf)
        print("Returning: %s" % json_def)
        return json_def

    def cf_json(self, json_obj):
        """Return nicely formatted/colored json"""
        formatted_json = json.dumps(json_obj, sort_keys=True, indent=4)
        colorful_json = highlight(
            formatted_json, 
            lexers.JsonLexer(), 
            formatters.TerminalFormatter()
        )
        return colorful_json


    def banner(self, b_str, color='green'):
        """Print a nice banner"""
        print("-" * 60)
        print(b_str)
        print("-" * 60)
