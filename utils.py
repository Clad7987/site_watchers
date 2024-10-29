import json

def add_propierty(filename, propierty, value):
    with open(filename, "r") as r:
        data = json.loads(r.read())

    for item in data:
        item[propierty] = value

    with open(filename, "w") as w:
        json.dump(data, w)

add_propierty('docs/data/fapdungeon.json', 'like', 0)
add_propierty('docs/data/waifubitches.json', 'like', 0)