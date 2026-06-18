import datetime
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
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(state))
    tmp.replace(path)


def schedule_wakeup(minutes: int = WAKEUP_MINUTES) -> None:
    wake = datetime.datetime.now() + datetime.timedelta(minutes=minutes)
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(5)
            s.connect(("127.0.0.1", 8421))
            s.sendall(f"set_alarm_time {wake.strftime('%H:%M:%S')}\n".encode())
            s.sendall(b"set_alarm_enabled true\n")
        log.info("Wakeup scheduled for %s", wake.strftime("%H:%M:%S"))
    except OSError as e:
        log.warning("Could not reach PiSugar 3 server: %s", e)


def main() -> None:
    if ImmichClient is None or EpaperDisplay is None:
        raise RuntimeError(
            "Required modules unavailable — are you running on a Raspberry Pi?"
        )
    album_id = os.getenv("ALBUM_ID")
    if not album_id:
        raise ValueError("ALBUM_ID must be set in .env")

    state = load_state(STATE_PATH, album_id=album_id)

    with ImmichClient() as client:
        if not state["queue"]:
            log.info("Queue empty — fetching album %s", album_id)
            try:
                assets = client.get_album_assets(album_id)
            except Exception as e:
                log.error("Failed to fetch album %s: %s", album_id, e)
                schedule_wakeup()
                subprocess.run(["sudo", "shutdown", "-h", "now"], check=False)
                return
            if not assets:
                log.error("Album %s is empty — nothing to display", album_id)
                subprocess.run(["sudo", "shutdown", "-h", "now"], check=False)
                return
            ids = [a["id"] for a in assets]
            random.shuffle(ids)
            state["queue"] = ids
            log.info("Loaded %d assets into queue", len(ids))

        asset_id = state["queue"].pop(0)
        save_state(STATE_PATH, state)
        log.info("Displaying asset %s (%d remaining)", asset_id, len(state["queue"]))

        try:
            image_bytes = client.get_asset_thumbnail_bytes(asset_id, size="preview")
        except Exception as e:
            log.error("Failed to fetch asset %s: %s", asset_id, e)
            schedule_wakeup()
            subprocess.run(["sudo", "shutdown", "-h", "now"], check=False)
            return

    EpaperDisplay().show(image_bytes)
    schedule_wakeup()
    subprocess.run(["sudo", "shutdown", "-h", "now"], check=False)


if __name__ == "__main__":
    main()
