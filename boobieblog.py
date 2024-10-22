import requests as req
import parsel
import json
import pathlib
import logging
from fake_useragent import FakeUserAgent
from typing import List, Dict
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configuração do logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("scraping.log"),
    ],
)

# Constantes
MODELS_URL = "https://www.boobieblog.com/model-directory/"
DATA_PATH = pathlib.Path("docs/data")
HEADERS = {"User-Agent": FakeUserAgent().chrome}
BATCH_SIZE = 100  # Número de modelos por lote

# Criando uma sessão global
session = req.Session()
session.headers.update(HEADERS)


def fetch_url(url: str) -> req.Response:
    """Função para obter uma URL, retornando a resposta."""
    try:
        logging.debug(f"Fetching URL: {url}")
        response = session.get(url)
        response.raise_for_status()
        return response
    except req.RequestException as e:
        logging.error(f"Error fetching {url}: {e}")
        return None


def get_model_links(url: str) -> List[Dict]:
    """Extrai os links e nomes dos modelos da página de diretório."""
    logging.info(f"Extracting model links from: {url}")
    response = fetch_url(url)
    if response is None:
        logging.warning(f"Failed to retrieve models from {url}")
        return []

    sel = parsel.Selector(response.text)
    article = sel.xpath('.//article[contains(@id, "post")]')

    models = [
        {
            "name": link.xpath("text()").get(),
            "link": link.attrib["href"],
            "content": [],
            "favorite": False,
        }
        for link in article.xpath(".//a")
        if not link.attrib["href"].startswith("#")
    ]
    logging.info(f"Found {len(models)} models on page")
    return models


def get_model_content(url: str) -> Dict:
    """Extrai o conteúdo (imagens e links) de uma página de modelo."""
    logging.debug(f"Extracting content from: {url}")
    response = fetch_url(url)
    if response is None:
        logging.warning(f"Failed to retrieve content from {url}")
        return {}

    sel = parsel.Selector(response.text)
    articles = sel.xpath('.//article[contains(@id, "post")]')

    model_content = {}
    for article in articles:
        title = article.xpath(".//h3/a/text()").get()
        link = article.xpath(".//h3/a/@href").get()
        org_images = article.xpath(
            './/div[contains(@class,"blog_post_content")]//a[contains(@target,"_blank")]/@href'
        ).getall()

        red_images = []
        for image in org_images:
            img_resp = fetch_url(image)
            if img_resp:
                img_sel = parsel.Selector(img_resp.text)
                red_images.append(img_sel.xpath(".//img/@src").get())

        model_content = {
            "title": title,
            "link": link,
            "contents": {"origin": org_images, "redirected": red_images},
        }

    return model_content


def get_model_data(model: Dict) -> Dict:
    """Extrai os dados completos de um modelo (nome, link, conteúdo)."""
    model_content = get_model_content(model["link"])
    if model_content:
        model["content"].append(model_content)
    return model


def save_to_json(data: List[Dict], filename: str) -> None:
    """Salva os dados em um arquivo JSON, anexando ao conteúdo existente."""
    # Carregar dados existentes
    if DATA_PATH.exists() and DATA_PATH.is_file():
        with open(filename, "r", encoding="utf-8") as file:
            existing_data = json.load(file)
    else:
        existing_data = []

    # Anexar novos dados
    existing_data.extend(data)

    # Salvar tudo no arquivo
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(existing_data, file, indent=4)


def scrape_models() -> None:
    """Função principal para extrair todos os modelos e seus conteúdos em lotes."""
    logging.info("Starting model scraping")

    models_data = get_model_links(MODELS_URL)
    if not models_data:
        logging.warning("No models found.")
        return []

    total_batches = (
        len(models_data) + BATCH_SIZE - 1
    ) // BATCH_SIZE  # Número total de batches

    # Barra de progresso geral para batches
    with tqdm(
        total=total_batches, desc="Overall Progress", unit="batch"
    ) as overall_progress:
        # Processamento em lotes
        for i in range(0, len(models_data), BATCH_SIZE):
            batch_models = models_data[i : i + BATCH_SIZE]
            logging.info(
                f"Processing batch {i // BATCH_SIZE + 1} with {len(batch_models)} models."
            )

            # Processamento paralelo para cada modelo
            data: List[Dict] = []
            with ThreadPoolExecutor(max_workers=10) as executor:
                futures = {
                    executor.submit(get_model_data, model): model
                    for model in batch_models
                }
                # Barra de progresso para cada batch
                for future in tqdm(
                    as_completed(futures),
                    total=len(futures),
                    desc="Processing models",
                    leave=False,
                ):
                    try:
                        model_data = future.result()
                        data.append(model_data)
                    except Exception as exc:
                        logging.error(f"Error processing model: {exc}")

            # Salvar os dados do lote
            save_to_json(data, DATA_PATH / "boobieblog_models.json")

            # Atualizar a barra de progresso geral
            overall_progress.update(1)

    logging.info("Scraping completed.")


def main():
    logging.info("Starting main execution")
    DATA_PATH.mkdir(exist_ok=True)

    # Extraindo os dados
    scrape_models()


if __name__ == "__main__":
    main()
