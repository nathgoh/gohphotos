import json
from main import load_state, save_state

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
