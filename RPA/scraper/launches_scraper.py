"""
Scraper de lançamentos espaciais — Launch Library 2 (ll.thespacedevs.com)
API pública e gratuita, sem necessidade de autenticação para uso básico.
Usa requests simples (sem Playwright) pois é uma API REST JSON.

O market_scraper usa yfinance para cotações via API REST do Yahoo Finance.
Ambos os scrapers utilizam requests HTTP diretos, com retry e cache local.
"""

import time
import requests

from config.settings import MAX_RETRIES, BACKOFF_BASE, REQUEST_TIMEOUT
from output.logger import get_logger
from scraper.cache import save as cache_save, load as cache_load

logger = get_logger("launches_scraper")
CACHE_KEY = "launches"

API_URL = "https://ll.thespacedevs.com/2.2.0/launch/upcoming/"
PARAMS  = {
    "limit":  20,
    "offset": 0,
    "format": "json",
}


def _fetch_launches() -> list[dict]:
    response = requests.get(API_URL, params=PARAMS, timeout=REQUEST_TIMEOUT, headers={
        "User-Agent": "SpaceIntelRPA/1.0"
    })
    response.raise_for_status()
    data = response.json()

    launches = []
    for item in data.get("results", []):
        launches.append({
            "data":      item.get("net", "A definir")[:19].replace("T", " "),
            "missao":    item.get("name", "Missão sem nome"),
            "veiculo":   item.get("rocket", {}).get("configuration", {}).get("full_name", "N/D"),
            "local":     item.get("pad", {}).get("location", {}).get("name", "N/D"),
            "descricao": (item.get("mission", {}) or {}).get("description", "")[:300],
            "status":    item.get("status", {}).get("name", "N/D"),
            "agencia":   item.get("launch_service_provider", {}).get("name", "N/D"),
        })

    return launches


def collect_launches() -> list[dict]:
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            logger.info(f"[cyan]Coletando lançamentos via Launch Library 2 — tentativa {attempt}/{MAX_RETRIES}[/cyan]")
            launches = _fetch_launches()

            if not launches:
                raise ValueError("Nenhum lançamento retornado pela API")

            logger.info(f"[green]✓ {len(launches)} lançamentos coletados[/green]")
            cache_save(CACHE_KEY, launches)
            return launches

        except Exception as e:
            wait = BACKOFF_BASE ** attempt
            logger.warning(f"Tentativa {attempt} falhou: {e}. Aguardando {wait}s...")
            if attempt < MAX_RETRIES:
                time.sleep(wait)

    cached = cache_load(CACHE_KEY)
    if cached:
        logger.warning("[yellow]Usando dados de lançamentos do cache local[/yellow]")
        return cached

    logger.error("[red]Falha total na coleta de lançamentos[/red]")
    return []
