import pytest, socket

from kb.mock_client import MockKBClient

# Every kind of client the contract tests run against. "http" joins this list when HTTPKBClient exists.
CLIENT_KINDS = ["mock", "http"]

@pytest.fixture(params=CLIENT_KINDS)
def connect(request, tmp_path):
    """Yield a function that opens a NEW client on the same backend each call.

    Each backend starts with the six sample documents (doc-001 ... doc-006).
    Calling connect() twice gives two separate client objects that share the
    same stored data, like two separate `kb` commands.
    """
    if request.param == "mock":
        path = tmp_path / "kb.json"
        yield lambda: MockKBClient(path)
    elif request.param == "http":
        from kb.fake_server import make_server, serve_in_background
        from kb.http_client import HTTPKBClient

        server = make_server(MockKBClient(tmp_path / "server-kb.json"))
        with serve_in_background(server) as url:
            yield lambda: HTTPKBClient(url)
    else:
        raise NotImplementedError(request.param)


@pytest.fixture
def client(connect):
    return connect()

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


@pytest.fixture
def dead_url():
    """A URL that nothing is listening on."""
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    return f"http://127.0.0.1:{port}"