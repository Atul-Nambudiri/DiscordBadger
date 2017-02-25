import json

def parse_json(file):
    data = {}
    with open(file) as json_file:
        data = json.load(json_file)
    return data