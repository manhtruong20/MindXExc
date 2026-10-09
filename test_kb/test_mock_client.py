from kb.mock_client import MockKBClient


def test_retrieve_returns_a_built_in_document(tmp_path):
    client = MockKBClient(tmp_path / "kb.json")

    doc = client.retrieve("doc-001")

    assert doc.id == "doc-001"
    assert doc.node_path == "/templates/email"


def test_retrieve_unknown_id_returns_none(tmp_path):
    client = MockKBClient(tmp_path / "kb.json")

    assert client.retrieve("doc-999") is None


def test_list_documents_returns_documents_at_exact_node(tmp_path):
    client = MockKBClient(tmp_path / "kb.json")

    docs = client.list_documents("/templates/email", limit=10)

    assert [doc.id for doc in docs] == ["doc-001", "doc-004"]