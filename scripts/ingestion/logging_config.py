"""Consistent UTC stdout logging for local and container execution."""

from __future__ import annotations

import logging
import sys
import time


def configure_logging(level: str = "INFO") -> None:
    formatter = logging.Formatter(
        fmt="%(asctime)s %(levelname)s %(name)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S UTC",
    )
    formatter.converter = time.gmtime
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    logging.basicConfig(
        level=getattr(logging, level, logging.INFO),
        handlers=[handler],
        force=True,
    )
