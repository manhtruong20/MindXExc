from kb.client import KBClient
from kb.document import Document

BUILT_IN_DOCUMENTS = [
    Document(
        "doc-001",
        "Customer Response Template",
        "Hi {name}, thanks for your message. Here is our response to your question.",
        "/templates/email",
        ["template", "email"],
    ),
    Document(
        "doc-002",
        "DevOps Team Members",
        "# DevOps team\n- Alice: team lead\n- Bob: infrastructure",
        "/team/devops",
        ["team", "devops"],
    ),
    Document(
        "doc-003",
        "Getting Started Guide",
        "# Getting started\n1. Install the tools\n2. Clone the repository",
        "/docs/guides",
        ["guide"],
    ),
    Document(
        "doc-004",
        "Follow-up Email Template",
        "Hi {name}, following up on our earlier conversation about your request.",
        "/templates/email",
        ["template", "email", "followup"],
    ),
    Document(
        "doc-005",
        "On-call Schedule",
        "# On-call\nWeek 1: Alice\nWeek 2: Bob",
        "/team/devops",
        ["team", "schedule"],
    ),
    Document(
        "doc-006",
        "Deployment Guide",
        "# Deployment\n1. Run the tests\n2. Deploy to staging\n3. Deploy to production",
        "/docs/guides",
        ["guide", "deployment"],
    ),
]


class MockKBClient(KBClient):
    def __init__(self, path):
        self._path = path
        self._documents = {doc.id: doc for doc in BUILT_IN_DOCUMENTS}

    def retrieve(self, doc_id):
        return self._documents.get(doc_id)

    def search(self, query, top_k):
        raise NotImplementedError

    def list_documents(self, node_path, limit):
        return [
            doc for doc in self._documents.values() if doc.node_path == node_path
        ]

    def add(self, title, content, node_path, tags):
        raise NotImplementedError