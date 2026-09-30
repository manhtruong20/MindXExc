
import pytest

import ticket_manager.ticket as ticket_module
from ticket_manager.ticket import Ticket
from ticket_manager.ticket import _fnv1a_32


def test_can_create_ticket():
    ticket = Ticket(
        title="Printer broken",
        description="The office printer does not work",
        priority="High",
    )
    assert ticket is not None

#test if the FNV-1a hash function produces the expected output for a known input
def test_fnv1a_32_matches_known_vector():
    assert _fnv1a_32(b"hello") == 0x4F9F2CAB


def test_ticket_id_is_eight_lowercase_hex_characters():
    ticket = Ticket(
        title="Printer broken",
        description="The office printer does not work",
        priority="High",
    )

    assert len(ticket.id) == 8
    assert ticket.id == ticket.id.lower()
    int(ticket.id, 16)


def test_ticket_id_uses_timestamp(monkeypatch):
    ticket_arguments = {
        "title": "Printer broken",
        "description": "The office printer does not work",
        "priority": "High",
    }
    monkeypatch.setattr(ticket_module.time, "time_ns", lambda: 100)
    first_id = Ticket(**ticket_arguments).id
    expected_id = f"{_fnv1a_32(b'100:Printer broken:The office printer does not work:High'):08x}"

    monkeypatch.setattr(ticket_module.time, "time_ns", lambda: 101)
    second_id = Ticket(**ticket_arguments).id

    assert first_id == expected_id
    assert first_id != second_id

def test_ticket_attributes():
    ticket = Ticket(
        title="Printer broken",
        description="The office printer does not work",
        priority="High",
    )
    assert ticket.title == "Printer broken"
    assert ticket.description == "The office printer does not work"
    assert ticket.priority == "High"


def test_ticket_attributes_can_be_updated():
    ticket = Ticket(
        title="Printer broken",
        description="The office printer does not work",
        priority="High",
    )

    ticket.title = "Printer jammed"
    ticket.description = "The paper tray is jammed"
    ticket.priority = "Medium"

    assert ticket.title == "Printer jammed"
    assert ticket.description == "The paper tray is jammed"
    assert ticket.priority == "Medium"


def test_ticket_defaults_to_empty_tags():
    ticket = Ticket(
        title="Printer broken",
        description="The office printer does not work",
        priority="High",
    )

    assert ticket.tags == set()


def test_ticket_parses_whitespace_separated_tags_into_a_set():
    ticket = Ticket(
        title="Printer broken",
        description="The office printer does not work",
        priority="High",
        tags="tag1 tag2\ttag3 tag1",
    )

    assert ticket.tags == {"tag1", "tag2", "tag3"}


@pytest.mark.parametrize("field", ["title", "description"])
@pytest.mark.parametrize("invalid_value", ["", "   ", "\t\n"])
def test_ticket_rejects_empty_or_whitespace_text(field, invalid_value):
    attributes = {
        "title": "Printer broken",
        "description": "The office printer does not work",
        "priority": "High",
    }
    attributes[field] = invalid_value

    with pytest.raises(ValueError, match=f"{field.capitalize()} cannot be empty or whitespace"):
        Ticket(**attributes)


def test_ticket_title_is_truncated_to_100_characters():
    long_title = "T" * 101

    ticket = Ticket(
        title=long_title,
        description="The office printer does not work",
        priority="High",
    )

    assert ticket.title == long_title[:100]
    assert len(ticket.title) == 100


@pytest.mark.parametrize("field", ["title", "description"])
def test_ticket_rejects_empty_text_when_updated(field):
    ticket = Ticket(
        title="Printer broken",
        description="The office printer does not work",
        priority="High",
    )

    with pytest.raises(ValueError, match=f"{field.capitalize()} cannot be empty or whitespace"):
        setattr(ticket, field, "   ")

@pytest.mark.parametrize("valid_priority", ["Low", "Medium", "High"])
def test_ticket_enforces_priority_values(valid_priority):
    ticket = Ticket(
        title="Printer broken",
        description="The office printer does not work",
        priority=valid_priority,
    )
    assert ticket.priority == valid_priority

    with pytest.raises(ValueError, match="Priority must be one of: Low, Medium, High"):
        ticket.priority = "Some invalid priority"