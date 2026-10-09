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


def test_list_documents_respects_limit(tmp_path):
    client = MockKBClient(tmp_path / "kb.json")

    docs = client.list_documents("/templates/email", limit=1)

    assert [doc.id for doc in docs] == ["doc-001"]


def test_search_matches_title_ignoring_case(tmp_path):
    client = MockKBClient(tmp_path / "kb.json")

    results = client.search("DEPLOYMENT GUIDE", top_k=5)

    assert [r.document.id for r in results] == ["doc-006"]


def test_search_matches_content(tmp_path):
    client = MockKBClient(tmp_path / "kb.json")

    results = client.search("staging", top_k=5)

    assert [r.document.id for r in results] == ["doc-006"]


def test_search_matches_tags(tmp_path):
    client = MockKBClient(tmp_path / "kb.json")

    results = client.search("followup", top_k=5)

    assert [r.document.id for r in results] == ["doc-004"]


def test_search_results_are_marked_as_keyword_matches(tmp_path):
    client = MockKBClient(tmp_path / "kb.json")

    results = client.search("staging", top_k=5)

    assert results[0].match_type == "keyword"


def test_search_respects_top_k(tmp_path):
    client = MockKBClient(tmp_path / "kb.json")

    results = client.search("email", top_k=1)

    assert [r.document.id for r in results] == ["doc-001"]


def test_search_with_no_match_returns_empty_list(tmp_path):
    client = MockKBClient(tmp_path / "kb.json")

    assert client.search("zzz-no-such-text", top_k=5) == []


#tests for add method
def test_add_returns_the_stored_document(tmp_path):
    client = MockKBClient(tmp_path / "kb.json")

    doc = client.add("Welcome SMS", "Hi {name}!", "/templates/sms", ["sms"])

    assert doc.title == "Welcome SMS"
    assert doc.content == "Hi {name}!"
    assert doc.node_path == "/templates/sms"
    assert doc.tags == ["sms"]


def test_add_assigns_different_ids(tmp_path):
    client = MockKBClient(tmp_path / "kb.json")

    first = client.add("A", "a", "/x", [])
    second = client.add("B", "b", "/x", [])

    assert first.id != second.id

def test_added_document_can_be_retrieved(tmp_path):
    client = MockKBClient(tmp_path / "kb.json")

    doc = client.add("Welcome SMS", "Hi", "/templates/sms", ["sms"])

    assert client.retrieve(doc.id) == doc


def test_added_document_appears_in_its_node_listing(tmp_path):
    client = MockKBClient(tmp_path / "kb.json")

    client.add("Welcome SMS", "Hi", "/templates/sms", ["sms"])
    docs = client.list_documents("/templates/sms", limit=10)

    assert [doc.title for doc in docs] == ["Welcome SMS"]


def test_added_document_can_be_found_by_search(tmp_path):
    client = MockKBClient(tmp_path / "kb.json")

    client.add("Welcome SMS", "Hi", "/templates/sms", ["sms"])
    results = client.search("welcome sms", top_k=5)

    assert [r.document.title for r in results] == ["Welcome SMS"]