import socket

import pytest

from kb.errors import KBApiError
from kb.fake_server import make_server, serve_in_background
from kb.http_client import HTTPKBClient
from kb.mock_client import MockKBClient
import json
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, HTTPServer

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


@contextmanager
def canned_server(status, body, content_type="application/json"):
    """A server that answers every POST with the same fixed reply."""

    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):
            self.rfile.read(int(self.headers.get("Content-Length", 0)))
            data = body.encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def log_message(self, format, *args):
            pass

    with serve_in_background(HTTPServer(("127.0.0.1", 0), Handler)) as url:
        yield url


CALLS = {
    "search": lambda client: client.search("x", 5),
    "list_documents": lambda client: client.list_documents("/x", 5),
    "retrieve": lambda client: client.retrieve("doc-001"),
    "add": lambda client: client.add("T", "C", "/x", []),
}

EMPTY_ID = {"id": "", "title": "t", "content": "c", "nodePath": "/x", "tags": []}

BAD_BODIES = [
    "this is not json",
    "",
    "null",
    "[]",
    "{}",
    json.dumps({"results": 5, "documents": 5, "document": 5}),
    json.dumps({"results": [5], "documents": [5], "document": {"id": "doc-1"}}),
    json.dumps({"results": [EMPTY_ID], "documents": [EMPTY_ID], "document": EMPTY_ID}),
]


@pytest.mark.parametrize("body", BAD_BODIES)
@pytest.mark.parametrize("name", list(CALLS))
def test_a_malformed_answer_raises_api_error(name, body):
    with canned_server(200, body) as url:
        with pytest.raises(KBApiError):
            CALLS[name](HTTPKBClient(url))


@pytest.mark.parametrize("name", list(CALLS))
def test_an_error_status_without_a_json_message_raises_api_error(name):
    with canned_server(500, "oops", "text/plain") as url:
        with pytest.raises(KBApiError, match="HTTP 500"):
            CALLS[name](HTTPKBClient(url))


def test_retrieve_treats_any_404_as_not_found():
    with canned_server(404, "<html>nope</html>", "text/html") as url:
        assert HTTPKBClient(url).retrieve("doc-001") is None