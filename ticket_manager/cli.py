import argparse
import sys
from pathlib import Path

from ticket_manager.storage import StorageError, load_tickets, save_tickets
from ticket_manager.ticket import Ticket, VALID_STATUSES, VALID_PRIORITIES
from ticket_manager.filters import filter_tickets
from ticket_manager.sorting import flatten, priority_rank, sort_groups, status_rank, tag_match_count


SORT_RULES = {
    "priority": (priority_rank, True),
    "status": (status_rank, False),
}

def build_parser():
    parser = argparse.ArgumentParser(prog="tickets")
    parser.add_argument("--file", default="tickets.json")
    commands = parser.add_subparsers(dest="command", required=True)

    create = commands.add_parser("create")
    create.add_argument("--title")
    create.add_argument("--description")
    create.add_argument("--priority")
    create.add_argument("--tags", nargs="*")

    show = commands.add_parser("show")
    show.add_argument("id")

    list_command = commands.add_parser("list")
    list_command.add_argument("--status", nargs="+", choices=sorted(VALID_STATUSES))
    list_command.add_argument("--priority", nargs="+", choices=sorted(VALID_PRIORITIES))
    list_command.add_argument("--tags", nargs="+")
    list_command.add_argument(
        "--sort", nargs="+", choices=list(SORT_RULES),
        action=SortNamesAction, dest="sort",
    )
    list_command.add_argument(
        "--sorttag", nargs="+", metavar="TAG",
        action=SortTagsAction, dest="sort",
    )

    update = commands.add_parser("update")
    update.add_argument("id")
    update.add_argument("status", choices=VALID_STATUSES)

    return parser


def _check(field, value):
    Ticket("title", "description", "Low").update(**{field: value})


def ask_valid(field, value, prompt):
    while True:
        if value is None:
            value = input(prompt)
        try:
            _check(field, value)
            return value
        except ValueError as error:
            print(f"Invalid {field}: {error}", file=sys.stderr)
            value = None


def create_ticket(args):
    manager = load_tickets(args.file)

    title = ask_valid("title", args.title, "Title: ")
    description = ask_valid("description", args.description, "Description: ")
    priority = ask_valid("priority", args.priority, "Priority (Low/Medium/High): ")
    tags = ask_valid(
        "tags",
        " ".join(args.tags) if args.tags is not None else None,
        "Tags (space separated, optional): ",
    )

    ticket = Ticket(title, description, priority, tags)
    manager.add(ticket)
    save_tickets(manager, args.file)

    print(ticket.id)
    return 0


def format_ticket(ticket):
    return "\n".join([
        f"ID:          {ticket.id}",
        f"Title:       {ticket.title}",
        f"Description: {ticket.description}",
        f"Status:      {ticket.status}",
        f"Priority:    {ticket.priority}",
        f"Tags:        {', '.join(sorted(ticket.tags))}",
    ])


def show_ticket(args):
    manager = load_existing_tickets(args.file)

    ticket = manager.get(args.id)
    if ticket is None:
        print(f"Ticket {args.id} not found", file=sys.stderr)
        return 1

    print(format_ticket(ticket))
    return 0


def load_existing_tickets(path):
    if not Path(path).exists():
        raise StorageError(f"Ticket file {path} not found")
    return load_tickets(path)


def list_tickets(args):
    """Print the tickets in the file, filtered and sorted, one per line.

    Steps, in this order:
      1. Load the file. A missing or corrupted file raises StorageError,
         which main() turns into a message on stderr and exit code 1.
      2. Filter: keep tickets matching ALL the given filters.
         --status / --priority match ANY of their values,
         --tags requires ALL of its values. A filter left out is skipped.
      3. Sort: args.sort is a list of (key, reverse) rules built from
         --sort and --sorttag in command-line order. The first rule is
         the primary one, and each later rule only breaks ties.
      4. Print one line per ticket (id, status, priority, title),
         or "No tickets found" if nothing is left.

    Never writes the file. Returns 0, including when nothing matches.
    """
    manager = load_existing_tickets(args.file)
    tickets = filter_tickets(
        manager,
        status=args.status,
        priority=args.priority,
        tags=args.tags,
    )
    tickets = sort_tickets(tickets, args.sort)

    if not tickets:
        print("No tickets found")
        return 0

    for ticket in tickets:
        print(f"{ticket.id}  {ticket.status:<9} {ticket.priority:<6} {ticket.title}")
    return 0


def update_ticket(args):
    manager = load_existing_tickets(args.file)

    manager.update(args.id, status=args.status)
    save_tickets(manager, args.file)

    print(f"{args.id} status: {args.status}")
    return 0


COMMANDS = {
    "create": create_ticket,
    "show": show_ticket,
    "list": list_tickets,
    "update": update_ticket,
}

class SortNamesAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        rules = list(getattr(namespace, self.dest) or [])
        rules.extend(SORT_RULES[name] for name in values)
        setattr(namespace, self.dest, rules)


class SortTagsAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        rules = list(getattr(namespace, self.dest) or [])
        rules.append((tag_match_count(values), True))
        setattr(namespace, self.dest, rules)

def sort_tickets(tickets, rules):
    groups = [tickets]
    for key, reverse in rules or []:
        groups = sort_groups(groups, key=key, reverse=reverse)
    return flatten(groups)


def main(argv=None):
    args = build_parser().parse_args(argv)

    try:
        return COMMANDS[args.command](args)
    except EOFError:
        print("Missing arguments and cannot ask for them: no input available", file=sys.stderr)
        return 1
    except StorageError as error:
        print(error, file=sys.stderr)
        return 1