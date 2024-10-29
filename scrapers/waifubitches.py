import requests as req
import parsel as ps
import json
import os

baseurl = 'https://waifubitches.com/'
urls = [
    'https://waifubitches.com/pt/model/Kenizinea',
    'https://waifubitches.com/pt/model/Mommy-Anna',
    'https://waifubitches.com/pt/model/Kaya-Huang',
    'https://waifubitches.com/pt/model/Punk-Macarroni',
    'https://waifubitches.com/pt/model/Kamelya-Chan',
    'https://waifubitches.com/pt/model/Uyuy',
    'https://waifubitches.com/pt/model/Hana-Bunny',
    'https://waifubitches.com/pt/model/Sunny-Ray',
    'https://waifubitches.com/pt/model/Evie-Lee-Mikomin',
    'https://waifubitches.com/pt/model/Mimsy',
    'https://waifubitches.com/pt/model/Juliette-Michele',
    'https://waifubitches.com/pt/model/Sweetie-Fox',
    'https://waifubitches.com/pt/model/Hane-Ame',
    'https://waifubitches.com/pt/model/Mad-Roxy',
    'https://waifubitches.com/pt/model/Maria-Desu',
    'https://waifubitches.com/pt/model/Mikomi-Hokina',
    'https://waifubitches.com/pt/model/Potato-Godzilla',
    'https://waifubitches.com/pt/model/Octokuro',
    'https://waifubitches.com/pt/model/Queenie',
    'https://waifubitches.com/pt/model/Queenie-Chuppy-',
    'https://waifubitches.com/pt/model/Alina-Becker',
    'https://waifubitches.com/pt/model/Byoru',
    'https://waifubitches.com/pt/model/Kalinka-Fox',
    'https://waifubitches.com/pt/model/Helly-von-Valentine',
    'https://waifubitches.com/pt/model/Anri-Okita',
    'https://waifubitches.com/pt/model/Hidori-Rose',
    'https://waifubitches.com/pt/model/Ana-Chuu',
    'https://waifubitches.com/pt/model/Angie-Griffin',
    'https://waifubitches.com/pt/model/Azami',
    'https://waifubitches.com/pt/model/Bunni-Lynn',
    'https://waifubitches.com/pt/model/Bunny-Ayumi',
    'https://waifubitches.com/pt/model/Chono-Black',
    'https://waifubitches.com/pt/model/Danielle-Vedovelli',
    'https://waifubitches.com/pt/model/Enafox',
    'https://waifubitches.com/pt/model/Enji-Night',
    'https://waifubitches.com/pt/model/Fe-Galvao',
    'https://waifubitches.com/pt/model/Giada-Robin',
    'https://waifubitches.com/pt/model/Giu-Hellsing',
    'https://waifubitches.com/pt/model/Jenna-Lynn-Meowri',
    'https://waifubitches.com/pt/model/Jessica-Nigri',
    'https://waifubitches.com/pt/model/Kaho',
    'https://waifubitches.com/pt/model/Lada-Lyumos',
    'https://waifubitches.com/pt/model/Lady-Melamori',
    'https://waifubitches.com/pt/model/Laura-Pyon',
    'https://waifubitches.com/pt/model/Lera-Himera',
    'https://waifubitches.com/pt/model/Lyvlas',
    'https://waifubitches.com/pt/model/Marina-Mui',
    'https://waifubitches.com/pt/model/Momokun',
    'https://waifubitches.com/model/OMGcosplay',
    'https://waifubitches.com/model/Pia',
    'https://waifubitches.com/model/Sara-Mei-Kasai',
    'https://waifubitches.com/model/Saya-The-Fox',
    'https://waifubitches.com/model/Serinide',
    'https://waifubitches.com/model/Tenleid',
    'https://waifubitches.com/model/Nico',
    'https://waifubitches.com/model/Uniquesora',
    'https://waifubitches.com/model/Usatame',
    'https://waifubitches.com/model/Velvet-Valerina',
    'https://waifubitches.com/model/Virtual-Geisha',
    'https://waifubitches.com/model/Waifu-Korra',
    'https://waifubitches.com/model/Yoshinobi',
    'https://waifubitches.com/model/Yureta',
    'https://waifubitches.com/model/Yuzu-Pyon',
]

data= []
for url in urls:
    page = req.get(url).text
    sel = ps.Selector(page)

    albums = sel.xpath('.//div[contains(@class, "grid-item")]/a')
    item = {
        "name": os.path.basename(url),
        "link": url,
        "content": [],
        "favorite": False,
        'like': 0
        }
    data.append(item)
    index = data.index(item)
    for album in albums:
        page = ps.Selector(req.get(baseurl + album.attrib['href']).text)
        data[index]['content'].extend(page.xpath('.//img/@src').getall())

with open('docs/data/waifubitches.json', 'w') as file:
    json.dump(data, file)