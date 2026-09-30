
def test_can_create_ticket():
    ticket = Ticket(
        title="Printer broken",
        description="The office printer does not work",
        priority="High",
    )
    assert ticket is not None