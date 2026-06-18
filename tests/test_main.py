import datetime
import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from main import load_state, save_state, schedule_wakeup

def test_load_state_missing_file(tmp_path):
    state = load_state(tmp_path / "state.json", album_id="abc")
    assert state == {"album_id": "abc", "queue": []}

def test_load_state_existing_same_album(tmp_path):
    path = tmp_path / "state.json"
    path.write_text(json.dumps({"album_id": "abc", "queue": ["id1", "id2"]}))
    state = load_state(path, album_id="abc")
    assert state == {"album_id": "abc", "queue": ["id1", "id2"]}

def test_load_state_album_changed(tmp_path):
    path = tmp_path / "state.json"
    path.write_text(json.dumps({"album_id": "old", "queue": ["id1"]}))
    state = load_state(path, album_id="new")
    assert state == {"album_id": "new", "queue": []}

def test_save_state_roundtrip(tmp_path):
    path = tmp_path / "state.json"
    original = {"album_id": "abc", "queue": ["id1", "id2"]}
    save_state(path, original)
    loaded = json.loads(path.read_text())
    assert loaded == original

def test_load_state_corrupt_json(tmp_path):
    path = tmp_path / "state.json"
    path.write_text("{not valid json")
    state = load_state(path, album_id="abc")
    assert state == {"album_id": "abc", "queue": []}

def test_schedule_wakeup_sends_correct_commands():
    fixed_now = datetime.datetime(2026, 6, 17, 12, 0, 0)
    mock_socket = MagicMock()
    mock_socket.__enter__ = MagicMock(return_value=mock_socket)
    mock_socket.__exit__ = MagicMock(return_value=False)

    with patch("main.datetime") as mock_dt, \
         patch("main.socket.socket", return_value=mock_socket):
        mock_dt.datetime.now.return_value = fixed_now
        mock_dt.timedelta = datetime.timedelta
        schedule_wakeup(minutes=10)

    expected_time = "12:10:00"
    calls = [call.args[0] for call in mock_socket.sendall.call_args_list]
    assert f"set_alarm_time {expected_time}\n".encode() in calls
    assert b"set_alarm_enabled true\n" in calls
