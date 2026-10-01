import json

import pytest

from ticket_manager.manager import TicketManager
from ticket_manager.storage import save_tickets, load_tickets, StorageError
from ticket_manager.ticket import Ticket


@pytest.fixture
def manager():
    m = TicketManager()
    m.add(Ticket.from_dict({
        "id": "a1b2c3d4", "title": "First", "description": "d1",
        "status": "Open", "priority": "High", "tags": ["a", "b"],
    }))
    m.add(Ticket.from_dict({
        "id": "deadbeef", "title": "Second", "description": "d2",
        "status": "Closed", "priority": "Low", "tags": [],
    }))
    return m


def test_saved_manager_can_be_loaded_back(manager, tmp_path):
    path = tmp_path / "tickets.json"

    save_tickets(manager, path)
    loaded = load_tickets(path)

    assert [t.to_dict() for t in loaded] == [t.to_dict() for t in manager]


def test_load_returns_empty_manager_when_file_does_not_exist(tmp_path):
    assert load_tickets(tmp_path / "missing.json").ids() == []


def test_load_rejects_duplicate_ids(tmp_path):
    path = tmp_path / "tickets.json"
    record = {"id": "a1b2c3d4", "title": "T", "description": "D",
              "status": "Open", "priority": "High", "tags": []}
    path.write_text(json.dumps([record, record]))

    with pytest.raises(ValueError, match="a1b2c3d4"):
        load_tickets(path)


def test_load_raises_storage_error_for_invalid_json(tmp_path):
    path = tmp_path / "tickets.json"
    path.write_text("{an invalid json")

    with pytest.raises(StorageError, match="corrupted"):
        load_tickets(path)


def test_load_rejects_file_that_is_not_a_list(tmp_path):
    path = tmp_path / "tickets.json"
    path.write_text("{}")

    with pytest.raises(StorageError, match="list"):
        load_tickets(path)


VALID_RECORD = {
    "id": "a1b2c3d4", "title": "Printer broken",
    "description": "The office printer does not work",
    "status": "Open", "priority": "High", "tags": ["printer"],
}


def write_records(tmp_path, records):
    path = tmp_path / "tickets.json"
    path.write_text(json.dumps(records))
    return path


def good_then(bad_record):
    return [{**VALID_RECORD, "id": "deadbeef"}, bad_record]


def test_load_wraps_error_for_record_that_is_not_an_object(tmp_path):
    path = write_records(tmp_path, good_then(1))

    with pytest.raises(StorageError, match="record 1"):
        load_tickets(path)


def test_load_wraps_error_for_missing_field(tmp_path):
    bad = {k: v for k, v in VALID_RECORD.items() if k != "title"}
    path = write_records(tmp_path, good_then(bad))

    with pytest.raises(StorageError, match="record 1.*title"):
        load_tickets(path)


def test_load_wraps_error_for_invalid_value(tmp_path):
    path = write_records(tmp_path, good_then({**VALID_RECORD, "priority": "Urgent"}))

    with pytest.raises(StorageError, match="record 1.*Priority"):
        load_tickets(path)