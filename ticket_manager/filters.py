def _matches(ticket, status, priority, tags):
    if status and ticket.status not in status:
        return False
    if priority and ticket.priority not in priority:
        return False
    if tags and not set(tags) <= ticket.tags:
        return False
    return True


def filter_tickets(tickets, status=None, priority=None, tags=None):
    return [t for t in tickets if _matches(t, status, priority, tags)]