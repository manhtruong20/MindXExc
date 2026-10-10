import json
import urllib.error
import urllib.request


def post(base_url, path, body=None, raw=None):
    data = raw if raw is not None else json.dumps(body).encode("utf-8")
    request = urllib.request.Request(
        base_url + path,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request) as response:
            return response.status, json.load(response)
    except urllib.error.HTTPError as error:
        return error.code, json.load(error)


def test_retrieve_returns_the_document(server_url):
    status, body = post(server_url, "/retrieve", {"docId": "doc-001"})

    assert status == 200
    assert body["document"]["id"] == "doc-001"
    assert body["document"]["title"] == "Customer Response Template"
    assert body["document"]["nodePath"] == "/templates/email"
    assert body["document"]["tags"] == ["template", "email"]


def test_retrieve_of_an_unknown_id_is_404(server_url):
    status, body = post(server_url, "/retrieve", {"docId": "doc-999"})

    assert status == 404
    assert "doc-999" in body["error"]


def test_a_missing_field_is_400(server_url):
    status, body = post(server_url, "/retrieve", {})

    assert status == 400
    assert "docId" in body["error"]


def test_a_body_that_is_not_json_is_400(server_url):
    status, body = post(server_url, "/retrieve", raw=b"{not json")

    assert status == 400
    assert "error" in body


def test_an_unknown_path_is_404(server_url):
    status, body = post(server_url, "/nonsense", {})

    assert status == 404
    assert "error" in body

def test_an_unknown_path_with_a_large_body_is_still_404(server_url):
    for _ in range(20):
        status, body = post(server_url, "/nonsense", {"padding": "x" * 100_000})

        assert status == 404
        assert "error" in body

#fake server tests for latency simulation
def test_latency_waits_a_random_time_inside_the_range(tmp_path):
    from kb.fake_server import make_server, serve_in_background
    from kb.mock_client import MockKBClient

    waits = []
    server = make_server(
        MockKBClient(tmp_path / "kb.json"),
        latency=(0.05, 0.15),
        sleep=waits.append,
    )

    with serve_in_background(server) as url:
        for _ in range(5):
            post(url, "/retrieve", {"docId": "doc-001"})

    assert len(waits) == 5
    assert all(0 <= wait <= 0.15 for wait in waits)
    assert len(set(waits)) > 1


def test_there_is_no_delay_by_default(tmp_path):
    from kb.fake_server import make_server, serve_in_background
    from kb.mock_client import MockKBClient

    waits = []
    server = make_server(MockKBClient(tmp_path / "kb.json"), sleep=waits.append)

    with serve_in_background(server) as url:
        post(url, "/retrieve", {"docId": "doc-001"})

    assert waits == []


def test_search_returns_results_with_a_match_type(server_url):
    status, body = post(server_url, "/search", {"query": "deployment", "topK": 5})

    assert status == 200
    assert body["results"] == [
        {
            "id": "doc-006",
            "title": "Deployment Guide",
            "nodePath": "/docs/guides",
            "matchType": "keyword",
        }
    ]


def test_search_respects_top_k(server_url):
    status, body = post(server_url, "/search", {"query": "email", "topK": 1})

    assert [hit["id"] for hit in body["results"]] == ["doc-001"]


def test_search_needs_a_query_and_a_positive_top_k(server_url):
    assert post(server_url, "/search", {"topK": 5})[0] == 400
    assert post(server_url, "/search", {"query": "x"})[0] == 400
    assert post(server_url, "/search", {"query": "x", "topK": 0})[0] == 400
    assert post(server_url, "/search", {"query": "x", "topK": "5"})[0] == 400


def test_list_returns_the_documents_of_a_node(server_url):
    status, body = post(
        server_url, "/list", {"nodePath": "/templates/email", "limit": 10}
    )

    assert status == 200
    assert [doc["id"] for doc in body["documents"]] == ["doc-001", "doc-004"]
    assert body["documents"][0]["content"].startswith("Hi {name}")


def test_list_respects_limit_and_validates_its_input(server_url):
    _, body = post(server_url, "/list", {"nodePath": "/templates/email", "limit": 1})

    assert [doc["id"] for doc in body["documents"]] == ["doc-001"]
    assert post(server_url, "/list", {"limit": 1})[0] == 400
    assert post(server_url, "/list", {"nodePath": "/x"})[0] == 400
    assert post(server_url, "/list", {"nodePath": "/x", "limit": 0})[0] == 400


def test_add_stores_a_document_that_can_then_be_retrieved(server_url):
    new = {
        "title": "Welcome SMS",
        "content": "Hi!",
        "nodePath": "/templates/sms",
        "tags": ["sms"],
    }

    status, body = post(server_url, "/add", new)
    doc_id = body["document"]["id"]
    _, found = post(server_url, "/retrieve", {"docId": doc_id})

    assert status == 201
    assert doc_id.startswith("doc-")
    assert found["document"]["title"] == "Welcome SMS"
    assert found["document"]["tags"] == ["sms"]


def test_add_validates_its_input(server_url):
    good = {"title": "T", "content": "C", "nodePath": "/x", "tags": []}

    for missing in good:
        incomplete = {key: value for key, value in good.items() if key != missing}
        assert post(server_url, "/add", incomplete)[0] == 400
    assert post(server_url, "/add", {**good, "tags": "sms"})[0] == 400
    assert post(server_url, "/add", {**good, "title": 5})[0] == 400