def _matches(ticket, status, priority):
    if status and ticket.status not in status:
        return False
    if priority and ticket.priority not in priority:
        return False
    return True


def filter_tickets(tickets, status=None, priority=None):
    return [t for t in tickets if _matches(t, status, priority)]