import pytest

from ticket_manager.ticket import VALID_PRIORITIES, VALID_STATUSES, Ticket

def test_ticket_can_be_converted_to_dict():
    ticket = Ticket(
        title="Printer broken",
        description="The office printer does not work",
        priority="High",
        tags="printer office",
    )

    data = ticket.to_dict()

    assert data["id"] == ticket.id
    assert data["title"] == ticket.title
    assert data["description"] == ticket.description
    assert data["status"] == "Open"
    assert data["priority"] == "High"
    assert set(data["tags"]) == {"printer", "office"}


def test_can_create_blank_ticket():
    ticket = Ticket.blank()

    assert isinstance(ticket, Ticket)


def test_ticket_can_be_created_from_dict():
    data = {
        "id": "a1b2c3d4",
        "title": "Printer broken",
        "description": "The office printer does not work",
        "status": "Pending",
        "priority": "High",
        "tags": ["printer", "office"],
    }

    ticket = Ticket.from_dict(data)

    assert ticket.id == "a1b2c3d4"
    assert ticket.title == "Printer broken"
    assert ticket.description == "The office printer does not work"
    assert ticket.status == "Pending"
    assert ticket.priority == "High"
    assert ticket.tags == {"printer", "office"}

@pytest.mark.parametrize(
    "field, invalid_value, expected_message",
    [
        (
            "priority",
            "Invalid",
            f"Priority must be one of: {', '.join(sorted(VALID_PRIORITIES))}",
        ),
        (
            "status",
            "Invalid",
            f"Status must be one of: {', '.join(sorted(VALID_STATUSES))}",
        ),
        (
            "title",
            "",
            "Title cannot be empty or whitespace",
        ),
        (
            "title",
            "   ",
            "Title cannot be empty or whitespace",
        ),
        (
            "title",
            "\t\n",
            "Title cannot be empty or whitespace",
        ),
        (
            "description",
            "",
            "Description cannot be empty or whitespace",
        ),
        (
            "description",
            "   ",
            "Description cannot be empty or whitespace",
        ),
        (
            "description",
            "\t\n",
            "Description cannot be empty or whitespace",
        ),
    ],
)
def test_from_dict_rejects_invalid_field(
    field,
    invalid_value,
    expected_message,
):
    data = {
        "id": "a1b2c3d4",
        "title": "Printer broken",
        "description": "The office printer does not work",
        "status": "Open",
        "priority": "High",
        "tags": [],
    }
    data[field] = invalid_value

    with pytest.raises(ValueError, match=expected_message):
        Ticket.from_dict(data)

@pytest.mark.parametrize(
    "missing_field",
    ["id", "title", "description", "status", "priority"],
)
def test_from_dict_rejects_missing_required_field(missing_field):
    data = {
        "id": "a1b2c3d4",
        "title": "Printer broken",
        "description": "The office printer does not work",
        "status": "Open",
        "priority": "High",
        "tags": [],
    }
    del data[missing_field]

    with pytest.raises(KeyError):
        Ticket.from_dict(data)


REQUIRED_FIELDS = ["id", "title", "description", "status", "priority"]


@pytest.mark.parametrize("field", REQUIRED_FIELDS)
def test_from_dict_rejects_missing_required_field(field):
    data = {
        "id": "a1b2c3d4",
        "title": "Printer broken",
        "description": "The office printer does not work",
        "status": "Open",
        "priority": "High",
        "tags": [],
    }
    del data[field]

    with pytest.raises(KeyError, match=field):
        Ticket.from_dict(data)


def test_from_dict_defaults_missing_tags_to_empty():
    data = {
        "id": "a1b2c3d4",
        "title": "Printer broken",
        "description": "The office printer does not work",
        "status": "Open",
        "priority": "High",
    }

    assert Ticket.from_dict(data).tags == set()


@pytest.mark.parametrize("bad_id", ["", "   ", 123, None])
def test_from_dict_rejects_invalid_id(bad_id):
    data = {
        "id": bad_id,
        "title": "Printer broken",
        "description": "The office printer does not work",
        "status": "Open",
        "priority": "High",
        "tags": [],
    }

    with pytest.raises(ValueError, match="Id"):
        Ticket.from_dict(data)


@pytest.mark.parametrize("bad_tags", ["ab", 5, None, [1, 2], "a b", "a\tb", "a\nb", " a", "", "   "])
def test_from_dict_rejects_invalid_tags(bad_tags):
    data = {
        "id": "a1b2c3d4", "title": "T", "description": "D",
        "status": "Open", "priority": "High", "tags": bad_tags,
    }

    with pytest.raises(ValueError, match="Tags"):
        Ticket.from_dict(data)