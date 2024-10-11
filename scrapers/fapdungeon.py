import requests as req
import parsel as ps
from fake_useragent import FakeUserAgent
import json
import pathlib
import logging
from typing import List, Dict
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
import os

# Configuração do logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/fapdungeon_scraping.log"),
    ],
)

BASE_URL = "https://www.fapdungeon.com/"
DATA_PATH = pathlib.Path("data/")
HEADERS = {"User-Agent": FakeUserAgent().chrome}

# Criando um novo logger
specific_logger = logging.getLogger("specificLogger")
specific_logger.setLevel(logging.INFO)
file_handler = logging.FileHandler("specific.log")
file_handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)
specific_logger.addHandler(file_handler)

# Criando uma sessão global para reutilização
session = req.Session()
session.headers.update(HEADERS)


def fetch_url(url: str) -> req.Response:
    try:
        logging.debug(f"Fetching URL: {url}")
        response = session.get(url)
        response.raise_for_status()
        return response
    except req.RequestException as e:
        logging.error(f"Error fetching {url}: {e}")
        return None


def get_pages_links(base_url: str) -> List[str]:
    logging.info(f"Getting page links from base URL: {base_url}")
    response = fetch_url(base_url)
    if response is None:
        logging.warning("No response received for base URL")
        return []

    sel = ps.Selector(response.text)
    last_page = sel.xpath('//a[contains(@aria-label, "Last Page")]/@href').get()
    if not last_page:
        logging.info("Only one page found")
        return [base_url]

    last_page_number = int(last_page.split("/")[-2])
    logging.info(f"Found {last_page_number} pages")
    return [f"{BASE_URL}page/{index+1}" for index in range(last_page_number)]


def get_models(url: str) -> List[Dict]:
    logging.info(f"Extracting models from URL: {url}")
    response = fetch_url(url)
    if response is None:
        logging.warning(f"Failed to retrieve models from {url}")
        return []

    sel = ps.Selector(response.text)
    posts = sel.xpath('//article[contains(@id, "post")]')
    models = []

    for post in posts:
        post_info = post.xpath(
            './/a[contains(@class, "clean-gallery-postbox-mask-rmore")]'
        )
        link = post_info.xpath("@href").get()
        name = post_info.xpath(
            './/span[contains(@class, "screen-reader-text")]/text()'
        ).get()

        if link and name:
            models.append({"name": name.strip(), "link": link.strip(), "content": []})

    logging.info(f"Found {len(models)} models on page")
    return models


def get_model_content(url: str) -> List[str]:
    logging.debug(f"Extracting content from model page: {url}")
    response = fetch_url(url)
    if response is None:
        logging.warning(f"Failed to retrieve content from {url}")
        return []

    sel = ps.Selector(response.text)
    content = sel.xpath(".//article[contains(@id, 'post')]")
    images = content.xpath(".//img/@src").getall()
    videos = content.xpath(".//source/@src").getall()

    logging.info(f"Found {len(images)} images and {len(videos)} videos on page")
    return images + videos


def get_model_content_pages(url: str) -> List[str]:
    logging.info(f"Getting content pages for model: {url}")
    response = fetch_url(url)
    if response is None:
        logging.warning(f"Failed to retrieve content pages for {url}")
        return [url]

    sel = ps.Selector(response.text)
    last_page = sel.xpath(
        '//div[contains(@class, "page-links")]/a[contains(@class, "post-page-numbers")]/@href'
    ).getall()

    if not last_page:
        return [url]

    last_page_url = last_page[-1]
    if last_page_url.endswith("/"):
        last_page_url = last_page_url[:-1]
    last_page_number = int(last_page_url.split("/")[-1])
    logging.info(f"Found {last_page_number} content pages for model")
    return [f"{url}/{index+1}" for index in range(last_page_number)]


def get_model_data(model: Dict) -> Dict:
    """Extrai os dados de um único modelo e suas páginas de conteúdo."""
    model_pages = get_model_content_pages(model["link"])
    for page in model_pages:
        model["content"].extend(get_model_content(page))
    model["favorite"] = False
    return model


def get_contents(urls: List[str]) -> List[Dict]:
    logging.info("Starting content extraction for all models")
    data: List[Dict] = []

    with ThreadPoolExecutor(max_workers=10) as executor:  # Limitar o número de threads
        futures = {executor.submit(get_models, url): url for url in urls}
        for future in tqdm(
            as_completed(futures), total=len(futures), desc="Processing URLs"
        ):
            url = futures[future]
            try:
                models = future.result()
                # Processar cada modelo em uma thread separada
                model_futures = {
                    executor.submit(get_model_data, model): model for model in models
                }
                for model_future in tqdm(
                    as_completed(model_futures),
                    total=len(model_futures),
                    desc=f"Processing models from {url}",
                    leave=False,
                    dynamic_ncols=True,
                ):
                    model = model_futures[model_future]
                    data.append(model)
                    logging.info(f"Extracted model and content from {url}")
            except Exception as exc:
                logging.error(f"Exception occurred while processing {url}: {exc}")

    logging.info(f"Extraction complete. {len(data)} models processed.")
    return data


def main() -> None:
    os.system("clear")
    logging.info("Starting main execution")
    DATA_PATH.mkdir(exist_ok=True)

    pages = get_pages_links(BASE_URL)
    if not pages:
        logging.warning("No pages found.")
        return

    content = get_contents(pages)
    output_file = DATA_PATH / "fapdungeon.json"

    if output_file.exists():
        with open(output_file, "r") as file:
            data = json.load(file)
        favorites = {
            item["name"]: item["favorite"] for item in data if item["favorite"]
        }
        for item in content:
            if item["name"] in favorites:
                item["favorite"] = True

    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(content, file, separators=(",", ":"))

    logging.info(f"Data saved to {output_file}")


if __name__ == "__main__":
    main()
