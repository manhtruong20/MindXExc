"""Contract tests: every KBClient implementation must pass all of these.

The `client` fixture (conftest.py) yields a fresh client of each kind,
holding the six sample documents doc-001 ... doc-006. To check a new kind of
client, add it to CLIENT_KINDS in conftest.py.
"""

from xml.dom.minidom import Document
from kb.search_result import SearchResult


def test_retrieve_returns_a_built_in_document(client):
    doc = client.retrieve("doc-001")

    assert doc.id == "doc-001"
    assert doc.node_path == "/templates/email"


def test_retrieve_unknown_id_returns_none(client):
    assert client.retrieve("doc-999") is None


def test_list_documents_returns_documents_at_exact_node(client):
    docs = client.list_documents("/templates/email", limit=10)

    assert [doc.id for doc in docs] == ["doc-001", "doc-004"]


def test_list_documents_respects_limit(client):
    docs = client.list_documents("/templates/email", limit=1)

    assert [doc.id for doc in docs] == ["doc-001"]


def test_search_matches_title_ignoring_case(client):
    results = client.search("DEPLOYMENT GUIDE", top_k=5)

    assert [r.document.id for r in results] == ["doc-006"]


def test_search_matches_content(client):
    results = client.search("staging", top_k=5)

    assert [r.document.id for r in results] == ["doc-006"]


def test_search_matches_tags(client):
    results = client.search("followup", top_k=5)

    assert [r.document.id for r in results] == ["doc-004"]


def test_search_results_are_marked_as_keyword_matches(client):
    results = client.search("staging", top_k=5)

    assert results[0].match_type == "keyword"


def test_search_respects_top_k(client):
    results = client.search("email", top_k=1)

    assert [r.document.id for r in results] == ["doc-001"]


def test_search_with_no_match_returns_empty_list(client):
    assert client.search("zzz-no-such-text", top_k=5) == []


# tests for add method
def test_add_returns_the_stored_document(client):
    doc = client.add("Welcome SMS", "Hi {name}!", "/templates/sms", ["sms"])

    assert doc.title == "Welcome SMS"
    assert doc.content == "Hi {name}!"
    assert doc.node_path == "/templates/sms"
    assert doc.tags == ["sms"]


def test_add_assigns_different_ids(client):
    first = client.add("A", "a", "/x", [])
    second = client.add("B", "b", "/x", [])

    assert first.id != second.id


def test_added_document_can_be_retrieved(client):
    doc = client.add("Welcome SMS", "Hi", "/templates/sms", ["sms"])

    assert client.retrieve(doc.id) == doc


def test_added_document_appears_in_its_node_listing(client):
    client.add("Welcome SMS", "Hi", "/templates/sms", ["sms"])
    docs = client.list_documents("/templates/sms", limit=10)

    assert [doc.title for doc in docs] == ["Welcome SMS"]


def test_added_document_can_be_found_by_search(client):
    client.add("Welcome SMS", "Hi", "/templates/sms", ["sms"])
    results = client.search("welcome sms", top_k=5)

    assert [r.document.title for r in results] == ["Welcome SMS"]


def test_added_document_survives_a_new_client(client):
    doc = client.add("Welcome SMS", "Hi", "/templates/sms", ["sms"])

    second_client = type(client)(client._path)

    assert second_client.retrieve(doc.id) == doc


#Contract tests
def test_retrieve_returns_a_document(client):
    assert isinstance(client.retrieve("doc-001"), Document)


def test_list_documents_returns_documents(client):
    docs = client.list_documents("/templates/email", limit=10)

    assert docs
    assert all(isinstance(doc, Document) for doc in docs)


def test_list_documents_of_an_empty_node_is_an_empty_list(client):
    assert client.list_documents("/nowhere", limit=10) == []


def test_search_returns_search_results(client):
    results = client.search("email", top_k=5)

    assert results
    assert all(isinstance(result, SearchResult) for result in results)
    assert all(isinstance(result.document, Document) for result in results)


def test_search_with_an_empty_query_matches_everything_up_to_top_k(client):
    results = client.search("", top_k=3)

    assert [r.document.id for r in results] == ["doc-001", "doc-002", "doc-003"]


def test_add_keeps_its_own_copy_of_the_tags(client):
    tags = ["sms"]
    doc = client.add("Welcome SMS", "Hi", "/templates/sms", tags)

    tags.append("changed-later")

    assert client.retrieve(doc.id).tags == ["sms"]