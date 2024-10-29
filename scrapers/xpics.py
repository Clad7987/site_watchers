import parsel as ps
import requests as req
import pathlib
import logging
import os

from fake_useragent import FakeUserAgent

BASE_URL = 'https://www.xpics.me'
DATA_PATH = pathlib.Path('docs/data')
HEADERS = {'User-Agent': FakeUserAgent().chrome}

log_path = pathlib.Path('../logs')
log_path.mkdir(exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(str(log_path / "fapdungeon_scraping.log")),
    ],
)

specific_logger = logging.getLogger("specificLogger")
specific_logger.setLevel(logging.INFO)
file_handler = logging.FileHandler("specific.log")
file_handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)
specific_logger.addHandler(file_handler)

session = req.Session()
session.headers.update(HEADERS)

def fetch_url(url: str) -> req.Response:
    try:
        logging.debug('Fetching URL: {url}')
        response = session.get(url)
        response.raise_for_status()
        return response
    except req.RequestException as e:
        logging.error(f'Error fetching {url}: {e}')
        return None

def get_model(url) -> str:
    return os.path.basename(url)

def get_content(url: str) -> list[str]:
    response = fetch_url(url)

    sel = ps.Selector(response.text)
    data: str = sel.xpath('.//script[contains(text(), "NUXT")]')
    print(data.find('return'))
    print(data[443:])

get_content('https://www.xpics.me/@chaosbeans')
