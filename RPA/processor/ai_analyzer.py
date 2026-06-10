"""
Análise inteligente dos dados coletados via OpenAI API (GPT-4o).
Fallback: análise heurística se API indisponível.
"""

import json
import os
import re
from typing import Any

from openai import OpenAI
from dotenv import load_dotenv

from config.settings import OPENAI_MODEL
from output.logger import get_logger

load_dotenv()
logger = get_logger("ai_analyzer")

PROMPT_TEMPLATE = """Você é um analista especializado em economia espacial e mercados de insumos aeroespaciais.

Analise os dados abaixo e retorne SOMENTE um objeto JSON válido, sem markdown, sem explicações fora do JSON.

DADOS COLETADOS:
{data}

Retorne exatamente neste formato JSON:
{{
  "resumo_executivo": "string com 2-3 frases resumindo o cenário atual",
  "eventos_criticos": ["lista de missões ou eventos que merecem atenção"],
  "analise_mercado": "string analisando as cotações e tendências dos insumos",
  "riscos_identificados": ["lista de riscos observados nos dados"],
  "oportunidades": ["lista de oportunidades identificadas"],
  "recomendacoes": ["lista de ações recomendadas com base nos dados"],
  "indice_atividade_espacial": "Alto / Médio / Baixo",
  "sentimento_mercado": "Otimista / Neutro / Pessimista"
}}"""


def _call_openai(data_summary: dict[str, Any]) -> dict[str, Any]:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY não encontrada no .env")

    client = OpenAI(api_key=api_key)
    prompt = PROMPT_TEMPLATE.format(data=json.dumps(data_summary, ensure_ascii=False, indent=2))

    logger.info("[cyan]Enviando dados ao GPT-4o (OpenAI API)...[/cyan]")

    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1000,
        temperature=0.3,
    )

    raw_text = response.choices[0].message.content

    json_match = re.search(r"\{.*\}", raw_text, re.DOTALL)
    if not json_match:
        raise ValueError(f"GPT não retornou JSON válido. Resposta: {raw_text[:200]}")

    return json.loads(json_match.group())


def _heuristic_fallback(data_summary: dict[str, Any]) -> dict[str, Any]:
    logger.warning("[yellow]Usando análise heurística (API indisponível)[/yellow]")

    cotacoes    = data_summary.get("cotacoes_insumos", [])
    lancamentos = data_summary.get("proximos_lancamentos", [])

    altas  = [c for c in cotacoes if c.get("variacao_pct", 0) > 1]
    quedas = [c for c in cotacoes if c.get("variacao_pct", 0) < -1]

    sentimento = "Otimista" if len(altas) > len(quedas) else ("Pessimista" if len(quedas) > len(altas) else "Neutro")
    atividade  = "Alto" if len(lancamentos) >= 10 else ("Médio" if len(lancamentos) >= 5 else "Baixo")

    riscos = []
    if quedas:
        riscos.append(f"Queda em insumos críticos: {', '.join(c['ativo'] for c in quedas)}")

    return {
        "resumo_executivo": (
            f"Pipeline coletou {data_summary.get('total_lancamentos', 0)} lançamentos programados. "
            f"Mercado de insumos apresenta tendência {sentimento.lower()}. "
            f"Análise heurística gerada automaticamente pelo SpaceIntel RPA."
        ),
        "eventos_criticos": [l["missao"] for l in lancamentos[:5]],
        "analise_mercado": f"{len(altas)} ativo(s) em alta e {len(quedas)} em queda. Sentimento geral: {sentimento}.",
        "riscos_identificados": riscos if riscos else ["Nenhum risco crítico identificado nos dados atuais"],
        "oportunidades": [
            "Monitoramento contínuo de cotações permite antecipação de variações de custo",
            f"Volume de {len(lancamentos)} missões indica setor em expansão",
        ],
        "recomendacoes": [
            "Acompanhar variações semanais dos insumos identificados em queda",
            "Priorizar análise das missões marcadas como eventos críticos",
            "Executar pipeline diariamente para atualizar base de dados",
        ],
        "indice_atividade_espacial": atividade,
        "sentimento_mercado": sentimento,
    }


def analyze(data_summary: dict[str, Any]) -> dict[str, Any]:
    try:
        result = _call_openai(data_summary)
        logger.info(f"[green]✓ Análise de IA concluída via {OPENAI_MODEL} (OpenAI API)[/green]")
        result["fonte_analise"] = f"{OPENAI_MODEL} (OpenAI API)"
        return result
    except Exception as e:
        logger.warning(f"OpenAI API indisponível ({e}) — usando heurística")

    result = _heuristic_fallback(data_summary)
    result["fonte_analise"] = "Análise heurística (fallback)"
    return result
