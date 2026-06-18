import json
import logging
import os
import random
import socket
import subprocess
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except ModuleNotFoundError:
    pass

try:
    from epaper_display import EpaperDisplay
except ModuleNotFoundError:
    EpaperDisplay = None  # type: ignore[assignment,misc]

try:
    from immich_client import ImmichClient
except ModuleNotFoundError:
    ImmichClient = None  # type: ignore[assignment,misc]

STATE_PATH = Path(__file__).parent / "state.json"
WAKEUP_MINUTES = 10

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)


def load_state(path: Path, album_id: str) -> dict:
    if path.exists():
        try:
            data = json.loads(path.read_text())
            if data.get("album_id") == album_id:
                return data
        except json.JSONDecodeError:
            log.warning("state.json is corrupt — resetting queue")
    return {"album_id": album_id, "queue": []}


def save_state(path: Path, state: dict) -> None:
    path.write_text(json.dumps(state))
