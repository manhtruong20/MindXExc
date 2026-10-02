def filter_tickets(tickets, status=None):
    return [t for t in tickets if not status or t.status in status]