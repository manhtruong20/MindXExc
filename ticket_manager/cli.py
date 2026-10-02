import argparse
import sys
from pathlib import Path

from ticket_manager.storage import StorageError, load_tickets, save_tickets
from ticket_manager.ticket import Ticket, VALID_STATUSES
from ticket_manager.filters import filter_tickets

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

    return parser


def ask(value, prompt):
    return value if value is not None else input(prompt)

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
    tags = ask(
        " ".join(args.tags) if args.tags is not None else None,
        "Tags (space separated, optional): ",
    )

    ticket = Ticket(title, description, priority, tags)
    manager.add(ticket)
    save_tickets(manager, args.file)

    print(ticket.id)
    return 0


def show_ticket(args):
    if not Path(args.file).exists():
        print(f"Ticket file {args.file} not found", file=sys.stderr)
        return 1

    manager = load_tickets(args.file)
    ticket = manager.get(args.id)
    if ticket is None:
        print(f"Ticket {args.id} not found", file=sys.stderr)
        return 1

    print(f"ID:          {ticket.id}")
    print(f"Title:       {ticket.title}")
    print(f"Description: {ticket.description}")
    print(f"Status:      {ticket.status}")
    print(f"Priority:    {ticket.priority}")
    print(f"Tags:        {', '.join(sorted(ticket.tags))}")
    return 0


def list_tickets(args):
    manager = load_tickets(args.file)
    for ticket in filter_tickets(manager, status=args.status):
        print(f"{ticket.id}  {ticket.status:<9} {ticket.priority:<6} {ticket.title}")
    return 0


COMMANDS = {
    "create": create_ticket,
    "show": show_ticket,
    "list": list_tickets,
}


def main(argv=None):
    args = build_parser().parse_args(argv)

    try:
        if args.command == "create":
            return create_ticket(args)
        return COMMANDS[args.command](args)
    except EOFError:
        print("Missing arguments and cannot ask for them: no input available", file=sys.stderr)
        return 1
    except StorageError as error:
        print(error, file=sys.stderr)
        return 1