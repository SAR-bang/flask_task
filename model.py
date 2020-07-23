import json

def load_json():
    with open("userclients.json") as f:
        return json.load(f)


def save_json():
    with open("userclients.json","w") as f:
        return json.dump(db,f)

db = load_json()