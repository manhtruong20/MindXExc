from kb.document import Document

def test_document_keeps_its_fields():
    doc = Document(
        id="doc-1",
        title="Welcome email",
        content="Hello and welcome!",
        node_path="/templates/email",
        tags=["email", "welcome"],
    )

    assert doc.id == "doc-1"
    assert doc.title == "Welcome email"
    assert doc.content == "Hello and welcome!"
    assert doc.node_path == "/templates/email"
    assert doc.tags == ["email", "welcome"]

def test_tags_default_to_empty_list():
    doc = Document(
        id="doc-1",
        title="Welcome email",
        content="Hello and welcome!",
        node_path="/templates/email",
    )

    assert doc.tags == []


def test_default_tags_are_not_shared():
    a = Document("1", "A", "x", "/p")
    b = Document("2", "B", "y", "/p")
    a.tags.append("only-a")
    assert b.tags == []