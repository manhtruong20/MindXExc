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