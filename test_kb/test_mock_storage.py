import json

import pytest

from kb.errors import KBStorageError
from kb.mock_client import MockKBClient

GOOD_RECORD = {
    "id": "doc-1",
    "title": "T",
    "content": "C",
    "node_path": "/x",
    "tags": [],
}


def write_file(tmp_path, text):
    path = tmp_path / "kb.json"
    path.write_text(text, encoding="utf-8")
    return path


def test_invalid_json_raises_storage_error(tmp_path):
    path = write_file(tmp_path, "{not json")

    with pytest.raises(KBStorageError):
        MockKBClient(path)


def test_json_that_is_not_a_list_raises_storage_error(tmp_path):
    path = write_file(tmp_path, json.dumps(GOOD_RECORD))

    with pytest.raises(KBStorageError):
        MockKBClient(path)


def test_record_missing_fields_raises_storage_error_naming_the_record(tmp_path):
    path = write_file(tmp_path, json.dumps([GOOD_RECORD, {"id": "doc-2"}]))

    with pytest.raises(KBStorageError, match="record 2"):
        MockKBClient(path)


def test_record_that_is_not_an_object_raises_storage_error(tmp_path):
    path = write_file(tmp_path, json.dumps([5]))

    with pytest.raises(KBStorageError):
        MockKBClient(path)


def test_record_with_empty_id_raises_storage_error(tmp_path):
    record = {**GOOD_RECORD, "id": ""}
    path = write_file(tmp_path, json.dumps([record]))

    with pytest.raises(KBStorageError):
        MockKBClient(path)