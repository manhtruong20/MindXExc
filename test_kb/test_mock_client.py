from kb.mock_client import MockKBClient


def test_retrieve_returns_a_built_in_document(tmp_path):
    client = MockKBClient(tmp_path / "kb.json")

    doc = client.retrieve("doc-001")

    assert doc.id == "doc-001"
    assert doc.node_path == "/templates/email"