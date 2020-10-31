import json
import astree as ast

def dumps(root):
    return json.dumps(
        root,
        default=lambda x: {'_type': x.__class__.__name__, **x.__dict__},
        indent=4,
    )