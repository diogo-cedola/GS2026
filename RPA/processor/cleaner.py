"""
Limpeza e normalização dos dados coletados.
"""

import pandas as pd
from output.logger import get_logger

logger = get_logger("cleaner")


def clean_launches(raw: list[dict[str, str]]) -> pd.DataFrame:
    if not raw:
        logger.warning("Lista de lançamentos vazia — retornando DataFrame vazio")
        return pd.DataFrame(columns=["data", "missao", "veiculo", "local", "descricao"])

    df = pd.DataFrame(raw)

    # Remove duplicatas
    df.drop_duplicates(subset=["missao"], keep="first", inplace=True)

    # Limpeza de strings
    str_cols = df.select_dtypes(include="object").columns
    for col in str_cols:
        df[col] = df[col].str.strip().str.replace(r"\s+", " ", regex=True)

    # Trunca descrições longas
    if "descricao" in df.columns:
        df["descricao"] = df["descricao"].str[:250]

    # Remove apenas linhas completamente vazias (não filtra mais por N/D)
    df = df[df["missao"].str.len() > 0]

    df.reset_index(drop=True, inplace=True)
    logger.info(f"[green]✓ Lançamentos limpos: {len(df)} registros[/green]")
    return df


def clean_market(raw: list[dict]) -> pd.DataFrame:
    if not raw:
        logger.warning("Lista de cotações vazia — retornando DataFrame vazio")
        return pd.DataFrame()

    df = pd.DataFrame(raw)
    df.drop_duplicates(subset=["ticker"], keep="first", inplace=True)

    df["tendencia"] = df["variacao_pct"].apply(
        lambda x: "Alta ↑" if x > 0.5 else ("Queda ↓" if x < -0.5 else "Estável →")
    )

    df.reset_index(drop=True, inplace=True)
    logger.info(f"[green]✓ Cotações limpas: {len(df)} ativos[/green]")
    return df


def summarize_for_ai(launches_df: pd.DataFrame, market_df: pd.DataFrame) -> dict:
    launches_summary = launches_df.head(15).to_dict(orient="records") if not launches_df.empty else []
    market_summary = market_df[["ativo", "preco_atual", "variacao_pct", "tendencia"]].to_dict(orient="records") \
        if not market_df.empty else []

    return {
        "total_lancamentos": len(launches_df),
        "proximos_lancamentos": launches_summary,
        "cotacoes_insumos": market_summary,
    }
