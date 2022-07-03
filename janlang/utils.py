import json

class BasicEncoder(json.JSONEncoder):
    def default(self, o):
        d =  {'type': o.__class__.__name__}
        if o.__dict__:
            d['fields'] = o.__dict__    
        return d

def to_json(obj, **kw):
    return json.dumps(obj, cls=BasicEncoder, **kw)