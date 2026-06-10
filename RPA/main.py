"""
SpaceIntel RPA — Orquestrador Principal
========================================
Pipeline de automação inteligente para monitoramento da Economia Espacial.

Fluxo:
  1. Coleta (Launch Library 2 API + yfinance)  →  dados brutos
  2. Limpeza (Pandas)                          →  DataFrames normalizados
  3. Análise IA (GPT-4o / fallback heurístico) →  insights estruturados
  4. Outputs (openpyxl + Markdown)             →  artefatos entregáveis

Execução:
  python main.py
"""

import asyncio
import sys
import time
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

# Adiciona raiz do projeto ao path
sys.path.insert(0, str(Path(__file__).parent))

from config.settings import OUTPUT_DIR
from output.logger import get_logger
from scraper.launches_scraper import collect_launches
from scraper.market_scraper import collect_market_data
from processor.cleaner import clean_launches, clean_market, summarize_for_ai
from processor.ai_analyzer import analyze
from output.report_generator import generate_excel, generate_markdown_report

logger  = get_logger("main")
console = Console()


def _print_banner() -> None:
    console.print(Panel.fit(
        "[bold cyan]🚀 SpaceIntel RPA[/bold cyan]\n"
        "[dim]Pipeline de Automação Inteligente — Economia Espacial[/dim]\n"
        "[dim]SpaceIntel RPA[/dim]",
        border_style="cyan",
    ))


def _print_summary(launches_df, market_df, insights: dict, elapsed: float) -> None:
    """Exibe resumo da execução no terminal com Rich."""
    table = Table(title="📊 Resumo da Execução", show_header=True, header_style="bold cyan")
    table.add_column("Métrica",  style="bold")
    table.add_column("Valor",    style="green")

    table.add_row("Lançamentos coletados",    str(len(launches_df)))
    table.add_row("Ativos de mercado",         str(len(market_df)))
    table.add_row("Índice de atividade",       insights.get("indice_atividade_espacial", "N/D"))
    table.add_row("Sentimento de mercado",     insights.get("sentimento_mercado", "N/D"))
    table.add_row("Fonte de IA",               insights.get("fonte_analise", "N/D"))
    table.add_row("Tempo de execução",         f"{elapsed:.1f}s")
    table.add_row("Outputs em",                str(OUTPUT_DIR))

    console.print(table)

    console.print(Panel(
        insights.get("resumo_executivo", "N/D"),
        title="🧠 Resumo Executivo (IA)",
        border_style="green",
    ))


async def run_pipeline() -> None:
    """Executa o pipeline completo de forma orquestrada."""
    start = time.time()
    _print_banner()

    # ── ETAPA 1: Coleta ───────────────────────────────────────────────────────
    logger.info("[bold]═══ ETAPA 1/4 — COLETA DE DADOS ═══[/bold]")

    launches_raw, market_raw = await asyncio.gather(
        asyncio.to_thread(collect_launches),
        asyncio.to_thread(collect_market_data),   # yfinance é síncrono — roda em thread
    )

    # ── ETAPA 2: Limpeza ──────────────────────────────────────────────────────
    logger.info("[bold]═══ ETAPA 2/4 — LIMPEZA E NORMALIZAÇÃO ═══[/bold]")

    launches_df = clean_launches(launches_raw)
    market_df   = clean_market(market_raw)
    summary     = summarize_for_ai(launches_df, market_df)

    # ── ETAPA 3: Análise de IA ────────────────────────────────────────────────
    logger.info("[bold]═══ ETAPA 3/4 — ANÁLISE INTELIGENTE (LLM) ═══[/bold]")

    insights = analyze(summary)

    # ── ETAPA 4: Geração de outputs ───────────────────────────────────────────
    logger.info("[bold]═══ ETAPA 4/4 — GERAÇÃO DE ARTEFATOS ═══[/bold]")

    excel_path = generate_excel(launches_df, market_df, insights)
    md_path    = generate_markdown_report(launches_df, market_df, insights)

    elapsed = time.time() - start

    # ── Resumo final ──────────────────────────────────────────────────────────
    _print_summary(launches_df, market_df, insights, elapsed)

    console.print(f"\n[bold green]✅ Pipeline concluído com sucesso![/bold green]")
    console.print(f"   📊 Excel:    [cyan]{excel_path}[/cyan]")
    console.print(f"   📝 Markdown: [cyan]{md_path}[/cyan]")
    console.print(f"   📋 Logs:     [cyan]logs/[/cyan]\n")


if __name__ == "__main__":
    asyncio.run(run_pipeline())
