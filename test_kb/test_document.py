from kb.document import Document
import pytest

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


def test_empty_id_is_rejected():
    with pytest.raises(ValueError):
        Document(
            id="",
            title="Welcome email",
            content="Hello and welcome!",
            node_path="/templates/email",
        )


def test_to_dict_contains_every_field():
    doc = Document("doc-1", "Welcome", "Hello", "/templates/email", ["email"])

    assert doc.to_dict() == {
        "id": "doc-1",
        "title": "Welcome",
        "content": "Hello",
        "node_path": "/templates/email",
        "tags": ["email"],
    }


def test_from_dict_rebuilds_the_document():
    data = {
        "id": "doc-1",
        "title": "Welcome",
        "content": "Hello",
        "node_path": "/templates/email",
        "tags": ["email"],
    }

    assert Document.from_dict(data) == Document(
        "doc-1", "Welcome", "Hello", "/templates/email", ["email"]
    )


def test_dict_round_trip_gives_an_equal_document():
    doc = Document("doc-1", "Welcome", "Hello", "/templates/email", ["a", "b"])

    assert Document.from_dict(doc.to_dict()) == doc