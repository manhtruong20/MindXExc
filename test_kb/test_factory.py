import pytest

from kb.factory import make_client
from kb.http_client import HTTPKBClient
from kb.mock_client import MockKBClient


def test_kb_client_mock_gives_the_mock_client(tmp_path):
    env = {"KB_CLIENT": "mock", "KB_MOCK_FILE": str(tmp_path / "kb.json")}

    assert isinstance(make_client(env), MockKBClient)


def test_mock_is_the_default_when_kb_client_is_not_set(tmp_path):
    env = {"KB_MOCK_FILE": str(tmp_path / "kb.json")}

    assert isinstance(make_client(env), MockKBClient)


def test_mock_client_uses_the_file_from_kb_mock_file(tmp_path):
    path = tmp_path / "kb.json"
    client = make_client({"KB_MOCK_FILE": str(path)})

    client.add("Welcome SMS", "Hi", "/templates/sms", ["sms"])

    assert path.exists()


def test_unknown_kb_client_raises_value_error(tmp_path):
    env = {"KB_CLIENT": "carrier-pigeon"}

    with pytest.raises(ValueError, match="carrier-pigeon"):
        make_client(env)


def test_kb_client_http_gives_the_http_client():
    env = {"KB_CLIENT": "http", "KB_API_URL": "http://127.0.0.1:9"}

    assert isinstance(make_client(env), HTTPKBClient)


@pytest.mark.parametrize("env", [{"KB_CLIENT": "http"}, {"KB_CLIENT": "http", "KB_API_URL": ""}])
def test_http_needs_kb_api_url(env):
    with pytest.raises(ValueError, match="KB_API_URL"):
        make_client(env)


def test_http_client_talks_to_the_url_from_kb_api_url(server_url):
    client = make_client({"KB_CLIENT": "http", "KB_API_URL": server_url})

    assert client.retrieve("doc-001").id == "doc-001"