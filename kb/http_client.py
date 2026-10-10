import json
import urllib.error
import urllib.request

from kb.client import KBClient
from kb.document import Document
from kb.errors import KBApiError
from kb.search_result import SearchResult

DEFAULT_TIMEOUT = 5  #sec
_NOT_FOUND = object()  #server response 404 marker


def document_from_json(data):
    return Document(
        id=data["id"],
        title=data["title"],
        content=data["content"],
        node_path=data["nodePath"],
        tags=list(data["tags"]),
    )


def error_message(error):
    try:
        return json.load(error)["error"]
    except (ValueError, KeyError, TypeError):
        return f"HTTP {error.code}"

def parse_search(data):
    #The server's search hits carry no content or tags
    #so the documents inside the results are partial: content is "" and tags is [].
    return [
        SearchResult(
            Document(hit["id"], hit["title"], "", hit["nodePath"], []),
            hit["matchType"],
        )
        for hit in data["results"]
    ]

def parse_documents(data):
    return [document_from_json(item) for item in data["documents"]]


def parse_document(data):
    return document_from_json(data["document"])

class HTTPKBClient(KBClient):
    def __init__(self, base_url, timeout=DEFAULT_TIMEOUT):
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout

    def _post(self, path, payload, none_on_404=False):
        request = urllib.request.Request(
            self._base_url + path,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self._timeout) as response:
                return json.load(response)
        except urllib.error.HTTPError as error:
            if error.code == 404 and none_on_404:
                return _NOT_FOUND
            raise KBApiError(f"{path} failed: {error_message(error)}") from error
        except (urllib.error.URLError, TimeoutError) as error:
            reason = getattr(error, "reason", error)
            raise KBApiError(f"cannot reach {self._base_url}: {reason}") from error
        except ValueError as error:
            raise KBApiError(f"{path} returned an answer that is not JSON") from error

    def _request(self, path, payload, parse, none_on_404=False):
        data = self._post(path, payload, none_on_404)
        if data is _NOT_FOUND:
            return None
        try:
            return parse(data)
        except (KeyError, TypeError, ValueError) as error:
            raise KBApiError(
                f"{path} returned an unexpected answer: {error!r}"
            ) from error

    def search(self, query, top_k):
        return self._request("/search", {"query": query, "topK": top_k}, parse_search)

    def list_documents(self, node_path, limit):
        payload = {"nodePath": node_path, "limit": limit}
        return self._request("/list", payload, parse_documents)

    def retrieve(self, doc_id):
        return self._request(
            "/retrieve", {"docId": doc_id}, parse_document, none_on_404=True
        )

    def add(self, title, content, node_path, tags):
        payload = {
            "title": title,
            "content": content,
            "nodePath": node_path,
            "tags": list(tags),
        }
        return self._request("/add", payload, parse_document)