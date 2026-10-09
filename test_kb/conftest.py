import pytest

from kb.mock_client import MockKBClient


@pytest.fixture
def client(tmp_path):
    return MockKBClient(tmp_path / "kb.json")