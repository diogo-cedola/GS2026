"""
Scraper de mercado — cotações de insumos aeroespaciais via Yahoo Finance (yfinance).

yfinance faz requisições diretas à API do Yahoo Finance sem Playwright,
pois a API é estável e estruturada. Playwright é reservado para sites dinâmicos.
"""

import time
from typing import Any

import yfinance as yf
import pandas as pd

from config.settings import MARKET_TICKERS, MAX_RETRIES, BACKOFF_BASE
from output.logger import get_logger
from scraper.cache import save as cache_save, load as cache_load

logger = get_logger("market_scraper")
CACHE_KEY = "market"


def _fetch_ticker(symbol: str, name: str) -> dict[str, Any]:
    """Coleta dados de um ticker específico."""
    ticker = yf.Ticker(symbol)
    hist   = ticker.history(period="5d")

    if hist.empty:
        raise ValueError(f"Sem dados para {symbol}")

    latest     = hist.iloc[-1]
    prev        = hist.iloc[-2] if len(hist) >= 2 else latest
    variacao    = ((latest["Close"] - prev["Close"]) / prev["Close"]) * 100

    return {
        "ativo":        name,
        "ticker":       symbol,
        "preco_atual":  round(float(latest["Close"]), 2),
        "abertura":     round(float(latest["Open"]), 2),
        "maxima":       round(float(latest["High"]), 2),
        "minima":       round(float(latest["Low"]), 2),
        "variacao_pct": round(variacao, 2),
        "volume":       int(latest["Volume"]),
        "data":         str(latest.name.date()),
    }


def collect_market_data() -> list[dict[str, Any]]:
    """
    Coleta cotações para todos os tickers configurados.
    Retry individual por ticker; tickers com falha são pulados (não travam o pipeline).
    """
    results: list[dict[str, Any]] = []

    for name, symbol in MARKET_TICKERS.items():
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                logger.info(f"[cyan]Coletando {name} ({symbol}) — tentativa {attempt}[/cyan]")
                data = _fetch_ticker(symbol, name)
                results.append(data)
                logger.info(f"[green]✓ {name}: ${data['preco_atual']} ({data['variacao_pct']:+.2f}%)[/green]")
                break
            except Exception as e:
                wait = BACKOFF_BASE ** attempt
                logger.warning(f"{name} tentativa {attempt} falhou: {e}. Aguardando {wait}s...")
                if attempt == MAX_RETRIES:
                    logger.error(f"[red]Falha definitiva para {name} ({symbol}) — pulando[/red]")
                else:
                    time.sleep(wait)

    if results:
        cache_save(CACHE_KEY, results)
        return results

    # Fallback: cache local
    cached = cache_load(CACHE_KEY)
    if cached:
        logger.warning("[yellow]Usando cotações do cache local[/yellow]")
        return cached

    logger.error("[red]Falha total na coleta de mercado[/red]")
    return []
