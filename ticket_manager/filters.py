def _matches(ticket, status):
    if status and ticket.status not in status:
        return False
    return True


def filter_tickets(tickets, status=None):
    return [t for t in tickets if _matches(t, status)]