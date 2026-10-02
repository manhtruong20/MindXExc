import pytest

import ticket_manager.ticket as ticket_module
from ticket_manager.ticket import Ticket
from ticket_manager.ticket import _fnv1a_32
from ticket_manager.ticket import VALID_PRIORITIES


@pytest.fixture
def ticket_arguments():
    return {
        "title": "Printer broken",
        "description": "The office printer does not work",
        "priority": "High",
    }


@pytest.fixture
def ticket(ticket_arguments):
    return Ticket(**ticket_arguments)


def test_can_create_ticket(ticket):
    assert ticket is not None

# test if the FNV-1a hash function produces the expected output for a known input
def test_fnv1a_32_matches_known_vector():
    assert _fnv1a_32(b"hello") == 0x4F9F2CAB


def test_ticket_id_is_eight_lowercase_hex_characters(ticket):
    assert len(ticket.id) == 8
    assert ticket.id == ticket.id.lower()
    int(ticket.id, 16)


def test_ticket_id_uses_timestamp(monkeypatch, ticket_arguments):
    monkeypatch.setattr(ticket_module.time, "time_ns", lambda: 100)
    first_id = Ticket(**ticket_arguments).id
    expected_id = f"{_fnv1a_32(b'100:Printer broken:The office printer does not work:High'):08x}"

    monkeypatch.setattr(ticket_module.time, "time_ns", lambda: 101)
    second_id = Ticket(**ticket_arguments).id

    assert first_id == expected_id
    assert first_id != second_id

def test_ticket_attributes(ticket):
    assert ticket.title == "Printer broken"
    assert ticket.description == "The office printer does not work"
    assert ticket.priority == "High"


def test_ticket_attributes_can_be_updated(ticket):
    ticket.title = "Printer jammed"
    ticket.description = "The paper tray is jammed"
    ticket.priority = "Medium"

    assert ticket.title == "Printer jammed"
    assert ticket.description == "The paper tray is jammed"
    assert ticket.priority == "Medium"


def test_ticket_status_defaults_to_open(ticket):
    assert ticket.status == "Open"


@pytest.mark.parametrize("status", ["Open", "Pending", "Waiting", "Resolved", "Closed"])
def test_ticket_accepts_valid_status_updates(ticket, status):
    ticket.status = status

    assert ticket.status == status


def test_ticket_rejects_invalid_status(ticket):
    expected_msg = "Status must be one of: " + ", ".join(sorted(ticket_module.VALID_STATUSES))
    with pytest.raises(ValueError, match=expected_msg):
        ticket.status = "An Invalid Status"


def test_ticket_status_should_not_be_set_in_constructor(ticket_arguments):
    with pytest.raises(TypeError):
        Ticket(**ticket_arguments, status="Pending")


def test_ticket_defaults_to_empty_tags(ticket):
    assert ticket.tags == set()


def test_ticket_parses_whitespace_separated_tags_into_a_set(ticket_arguments):
    ticket = Ticket(**ticket_arguments, tags="tag1 tag2\ttag3 tag1")

    assert ticket.tags == {"tag1", "tag2", "tag3"}


@pytest.mark.parametrize("field", ["title", "description"])
@pytest.mark.parametrize("invalid_value", ["", "   ", "\t\n"])
def test_ticket_rejects_empty_or_whitespace_text(ticket_arguments, field, invalid_value):
    ticket_arguments[field] = invalid_value

    with pytest.raises(ValueError, match=f"{field.capitalize()} cannot be empty or whitespace"):
        Ticket(**ticket_arguments)


def test_ticket_title_is_truncated_to_100_characters(ticket_arguments):
    long_title = "T" * 101
    ticket_arguments["title"] = long_title
    ticket = Ticket(**ticket_arguments)

    assert ticket.title == long_title[:100]
    assert len(ticket.title) == 100


@pytest.mark.parametrize("field", ["title", "description"])
def test_ticket_rejects_empty_text_when_updated(ticket, field):
    with pytest.raises(ValueError, match=f"{field.capitalize()} cannot be empty or whitespace"):
        setattr(ticket, field, "   ")

@pytest.mark.parametrize("valid_priority", ["Low", "Medium", "High"])
def test_ticket_enforces_priority_values(ticket_arguments, valid_priority):
    ticket_arguments["priority"] = valid_priority
    ticket = Ticket(**ticket_arguments)
    assert ticket.priority == valid_priority

    with pytest.raises(ValueError, match=f"Priority must be one of: {', '.join(sorted(VALID_PRIORITIES))}"):
        ticket.priority = "Some invalid priority"


@pytest.mark.parametrize("bad_tags", ["-urgent", "ok -urgent", "--x", "-"])
def test_ticket_rejects_tags_starting_with_dash(ticket_arguments, bad_tags):
    with pytest.raises(ValueError, match="Tags"):
        Ticket(**ticket_arguments, tags=bad_tags)


def test_ticket_tags_setter_rejects_tag_starting_with_dash(ticket):
    with pytest.raises(ValueError, match="Tags"):
        ticket.tags = "-urgent"


def test_ticket_allows_dash_inside_a_tag(ticket_arguments):
    ticket = Ticket(**ticket_arguments, tags="high-priority a-b-")

    assert ticket.tags == {"high-priority", "a-b-"}


def test_failed_tags_assignment_keeps_old_tags(ticket_arguments):
    ticket = Ticket(**ticket_arguments, tags="a b")

    with pytest.raises(ValueError):
        ticket.tags = "c -d"

    assert ticket.tags == {"a", "b"}