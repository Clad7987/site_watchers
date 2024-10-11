import json

with open("data/fapdungeon.json", "r") as r:
    data = json.loads(r.read())

for item in data:
    item["favorite"] = False

with open("data/fapdungeon.json", "w") as w:
    json.dump(data, w)
