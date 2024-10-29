import requests as req
import parsel as ps
import os


urls = [
    'https://packdenovinhas.com/cosplay/kenizinea-cosplay-e-nude-pack-erotico/',
    'https://packdenovinhas.com/cosplay/octokuro-nudes-e-cosplay/',
    'https://packdenovinhas.com/cosplay/danielle-vedovelli-cosplay-erotico-da-hinata/',
    'https://packdenovinhas.com/cosplay/hanna-bunny-rias-gremory/',
    'https://packdenovinhas.com/cosplay/katyuska-moonfox-nua-naughty-halloween/',
    'https://packdenovinhas.com/famosinhas/lena-the-plug-youtuber-que-virou-atriz-porno/',
    'https://packdenovinhas.com/famosinhas/kari-c-nudes-e-fotos-eroticas/',
    'https://packdenovinhas.com/famosinhas/anri-okita-asiatica-com-peitoes/',
    'https://packdenovinhas.com/famosinhas/nyvi-estephan-nua-na-playboy/',
    ]

data = []

for url in urls:
    page = ps.Selector(req.get(url).text)
    content = page.xpath('.//div[contains(@class, "entry-content")]')
    imgs = content.xpath('.//img/@src').getall()
    data.append({
        "name": os.path.basename(url[:-1] if url.endswith('/') else url),
        "link": url,
        "content": imgs,
        "favorite": False
    })

