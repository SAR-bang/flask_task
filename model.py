import json


def load_json():
    with open("userclients.json") as f:
        return json.load(f)


def save_json():
    with open("userclients.json", "w") as f:
        return json.dump(db, f)


db = load_json()


def load_json2():
    with open("items.json") as f1:
        return json.load(f1)


def save_json2():
    with open("items.json", "w") as f1:
        return json.dump(db2, f1)


db2 = load_json2()
