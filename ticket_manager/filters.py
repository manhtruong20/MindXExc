def filter_tickets(tickets, status=None):
    return [t for t in tickets if status is None or t.status in status]