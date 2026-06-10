"""
Configurações centrais do SpaceIntel RPA.
Todas as URLs, parâmetros e constantes ficam aqui — nunca hardcoded nos módulos.
"""

from pathlib import Path

# ── Diretórios ────────────────────────────────────────────────────────────────
BASE_DIR   = Path(__file__).resolve().parent.parent
CACHE_DIR  = BASE_DIR / "cache"
LOGS_DIR   = BASE_DIR / "logs"
OUTPUT_DIR = BASE_DIR / "output"

# ── Fontes de dados ───────────────────────────────────────────────────────────
SPACEFLIGHT_URL = "https://spaceflightnow.com/launch-schedule/"

# Tickers do Yahoo Finance (insumos aeroespaciais)
MARKET_TICKERS = {
    "Alumínio":   "ALI=F",
    "Petróleo":   "CL=F",
    "Titânio ETF":"REMX",    # ETF de metais raros como proxy de titânio
    "SpaceX/Priv":"ARKX",    # ETF de empresas aeroespaciais
}

# ── LLM (OpenAI) ─────────────────────────────────────────────────────────────
OPENAI_MODEL   = "gpt-4o"
OPENAI_TIMEOUT = 60           # segundos

# ── Web scraping ──────────────────────────────────────────────────────────────
REQUEST_TIMEOUT   = 30        # segundos por request
MAX_RETRIES       = 3
BACKOFF_BASE      = 2         # segundos (exponential backoff)
PLAYWRIGHT_TIMEOUT = 30_000   # ms

# ── Output ────────────────────────────────────────────────────────────────────
EXCEL_FILENAME    = "spaceintel_report.xlsx"
REPORT_FILENAME   = "spaceintel_analysis.md"
