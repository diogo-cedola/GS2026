"""
Cache local baseado em JSON.
Usado como fallback quando a fonte web está indisponível.
Garante que o pipeline nunca quebra por falha de rede.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from config.settings import CACHE_DIR
from output.logger import get_logger

logger = get_logger("cache")
CACHE_DIR.mkdir(parents=True, exist_ok=True)


def _path(key: str) -> Path:
    safe = key.replace("/", "_").replace(":", "_")
    return CACHE_DIR / f"{safe}.json"


def save(key: str, data: Any) -> None:
    payload = {"timestamp": datetime.now().isoformat(), "data": data}
    try:
        _path(key).write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        logger.debug(f"Cache salvo: {key}")
    except Exception as e:
        logger.warning(f"Falha ao salvar cache '{key}': {e}")


def load(key: str) -> Any | None:
    p = _path(key)
    if not p.exists():
        return None
    try:
        payload = json.loads(p.read_text(encoding="utf-8"))
        logger.info(f"[yellow]Usando cache local para '{key}' (gravado em {payload['timestamp']})[/yellow]")
        return payload["data"]
    except Exception as e:
        logger.warning(f"Cache corrompido para '{key}': {e}")
        return None
