import os
from kb.http_client import HTTPKBClient
from kb.mock_client import MockKBClient

DEFAULT_MOCK_FILE = "kb.json"

def make_client(environ=None):
    environ = os.environ if environ is None else environ
    kind = environ.get("KB_CLIENT", "mock")
    if kind == "mock":
        return MockKBClient(environ.get("KB_MOCK_FILE", DEFAULT_MOCK_FILE))
    elif kind == "http":
        url = environ.get("KB_API_URL", "")
        if not url:
            raise ValueError("KB_API_URL must be set when KB_CLIENT=http")
        return HTTPKBClient(url)
    raise ValueError(f"unknown KB_CLIENT {kind!r}")