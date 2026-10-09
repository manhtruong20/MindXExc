import os
from kb.mock_client import MockKBClient

DEFAULT_MOCK_FILE = "kb.json"

def make_client(environ=None):
    environ = os.environ if environ is None else environ
    kind = environ.get("KB_CLIENT", "mock")
    if kind == "mock":
        return MockKBClient(environ.get("KB_MOCK_FILE", DEFAULT_MOCK_FILE))
    raise ValueError(f"unknown KB_CLIENT {kind!r}")