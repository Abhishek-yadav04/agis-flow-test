"""Structured logging utilities for AgisFL.
Centralizes log_event to decouple modules from main.py.
"""
from __future__ import annotations
import json
import os
from datetime import datetime, timezone
import logging

APP_VERSION = os.getenv("APP_VERSION", "3.1.0")

_DEF_LEVEL_MAP = {
    "error": logging.error,
    "warning": logging.warning,
    "debug": logging.debug,
    "info": logging.info,
}

def log_event(level: str, event: str, **fields):
    rec = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "level": level,
        "event": event,
        "version": APP_VERSION,
    }
    rec.update(fields)
    line = json.dumps(rec, default=str)
    _DEF_LEVEL_MAP.get(level, logging.info)(line)
