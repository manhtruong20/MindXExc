from ticket_manager.ticket import VALID_STATUSES


PRIORITY_RANK = {"Low": 0, "Medium": 1, "High": 2}

def tag_match_count(include):
    include = set(include)
    return lambda ticket: len(ticket.tags & include)

def priority_rank(ticket):
    return PRIORITY_RANK[ticket.priority]

def status_rank(ticket):
    return VALID_STATUSES.index(ticket.status)

def sort_groups(groups, key, reverse=False):
    result = []
    for group in groups:
        if not group:
            result.append(group)
            continue

        buckets = {}
        for ticket in group:
            buckets.setdefault(key(ticket), []).append(ticket)
        for bucket_key in sorted(buckets, reverse=reverse):
            result.append(buckets[bucket_key])
    return result

def flatten(groups):
       return [ticket for group in groups for ticket in group]