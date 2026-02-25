import json

def tokens_to_json(tokens):
    return json.dumps(tokens, indent=2)

def errors_to_json(errors):
    return json.dumps([e.to_dict() for e in errors], indent=2)
