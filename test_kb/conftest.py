import pytest

from kb.mock_client import MockKBClient

# Every kind of client the contract tests run against. "http" joins this list when HTTPKBClient exists.
CLIENT_KINDS = ["mock", "http"]

@pytest.fixture(params=CLIENT_KINDS)
def client(request, tmp_path):
    """A fresh client holding the six sample documents (doc-001 ... doc-006).

    Every client kind must start from this same data, because the contract
    tests rely on it. The "http" kind talks to a fake server over a real
    connection.
    """
    if request.param == "mock":
        yield MockKBClient(tmp_path / "kb.json")
    elif request.param == "http":
        from kb.fake_server import make_server, serve_in_background
        from kb.http_client import HTTPKBClient

        server = make_server(MockKBClient(tmp_path / "server-kb.json"))
        with serve_in_background(server) as url:
            yield HTTPKBClient(url)
    else:
        raise NotImplementedError(request.param)

import threading


@pytest.fixture
def server_url(tmp_path):
    """Run a fake KB server on a free port; yield its base URL."""
    from kb.fake_server import make_server

    server = make_server(MockKBClient(tmp_path / "server-kb.json"))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    host, port = server.server_address
    yield f"http://{host}:{port}"
    server.shutdown()
    server.server_close()
    thread.join()