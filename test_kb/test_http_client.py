import socket

import pytest

from kb.errors import KBApiError
from kb.fake_server import make_server, serve_in_background
from kb.http_client import HTTPKBClient
from kb.mock_client import MockKBClient


def closed_port_url():
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    return f"http://127.0.0.1:{port}"


def test_an_unreachable_server_raises_api_error():
    client = HTTPKBClient(closed_port_url())

    with pytest.raises(KBApiError, match="cannot reach"):
        client.retrieve("doc-001")


def test_a_slow_server_times_out(tmp_path):
    server = make_server(MockKBClient(tmp_path / "kb.json"), latency=(0.5, 0.5))

    with serve_in_background(server) as url:
        client = HTTPKBClient(url, timeout=0.1)

        with pytest.raises(KBApiError, match="cannot reach"):
            client.retrieve("doc-001")


def test_an_error_from_the_server_is_raised_with_its_message(server_url):
    client = HTTPKBClient(server_url)

    with pytest.raises(KBApiError, match="topK"):
        client.search("x", top_k=0)


def test_search_hits_have_no_content_and_no_tags(server_url):
    client = HTTPKBClient(server_url)

    hit = client.search("deployment", top_k=5)[0].document

    assert hit.id == "doc-006"
    assert hit.title == "Deployment Guide"
    assert hit.content == ""
    assert hit.tags == []