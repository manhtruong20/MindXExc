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