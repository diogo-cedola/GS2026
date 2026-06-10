"""
Logger centralizado do SpaceIntel RPA.
Grava em arquivo .log com timestamp e exibe no terminal via Rich.
"""

import logging
import sys
from datetime import datetime
from pathlib import Path

from rich.console import Console
from rich.logging import RichHandler

from config.settings import LOGS_DIR

LOGS_DIR.mkdir(parents=True, exist_ok=True)

_log_file = LOGS_DIR / f"spaceintel_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

# Handler de arquivo (plain text)
_file_handler = logging.FileHandler(_log_file, encoding="utf-8")
_file_handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s"))

# Handler de terminal (Rich — colorido e legível)
_rich_handler = RichHandler(
    console=Console(stderr=True),
    show_time=True,
    show_path=False,
    markup=True,
)

logging.basicConfig(
    level=logging.INFO,
    handlers=[_file_handler, _rich_handler],
)


def get_logger(name: str) -> logging.Logger:
    """Retorna logger nomeado por módulo."""
    return logging.getLogger(name)
