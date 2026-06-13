"""
log_config.py - Configuração centralizada de logging para MEF STRUCTURAL.

Uso:
    from log_config import get_logger
    logger = get_logger(__name__)
    logger.info("mensagem")
    logger.exception("erro com traceback")
"""

import logging
import sys
from pathlib import Path

_LOG_DIR = Path('logs')
_LOG_DIR.mkdir(exist_ok=True)

_FORMAT = '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s'
_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

_initialized = False


def setup_logging(level: int = logging.INFO) -> None:
    global _initialized
    if _initialized:
        return

    root = logging.getLogger()
    root.setLevel(level)

    # Console handler (sempre presente)
    console = logging.StreamHandler(sys.stdout)
    console.setLevel(level)
    console.setFormatter(logging.Formatter(_FORMAT, _DATE_FORMAT))
    root.addHandler(console)

    # File handler (rotação manual por dia)
    file_handler = logging.FileHandler(_LOG_DIR / 'engine.log', mode='a', encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(_FORMAT, _DATE_FORMAT))
    root.addHandler(file_handler)

    _initialized = True


def get_logger(name: str) -> logging.Logger:
    if not _initialized:
        setup_logging()
    return logging.getLogger(name)
