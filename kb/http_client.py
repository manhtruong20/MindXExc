import json
import urllib.error
import urllib.request

from kb.client import KBClient
from kb.document import Document
from kb.errors import KBApiError
from kb.search_result import SearchResult

DEFAULT_TIMEOUT = 5  #sec


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
                return None
            raise KBApiError(f"{path} failed: {error_message(error)}") from error
        except (urllib.error.URLError, TimeoutError) as error:
            reason = getattr(error, "reason", error)
            raise KBApiError(f"cannot reach {self._base_url}: {reason}") from error

    def search(self, query, top_k):
        data = self._post("/search", {"query": query, "topK": top_k})
        #The server's search hits carry no content or tags
        #so the documents inside the results are partial: content is "" and tags is [].
        return [
            SearchResult(
                Document(hit["id"], hit["title"], "", hit["nodePath"], []),
                hit["matchType"],
            )
            for hit in data["results"]
        ]

    def list_documents(self, node_path, limit):
        data = self._post("/list", {"nodePath": node_path, "limit": limit})
        return [document_from_json(item) for item in data["documents"]]

    def retrieve(self, doc_id):
        data = self._post("/retrieve", {"docId": doc_id}, none_on_404=True)
        if data is None:
            return None
        return document_from_json(data["document"])

    def add(self, title, content, node_path, tags):
        data = self._post(
            "/add",
            {"title": title, "content": content, "nodePath": node_path, "tags": list(tags)},
        )
        return document_from_json(data["document"])