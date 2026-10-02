import argparse
import sys
from pathlib import Path

from ticket_manager.storage import load_tickets, save_tickets
from ticket_manager.ticket import Ticket


def build_parser():
    parser = argparse.ArgumentParser(prog="tickets")
    parser.add_argument("--file", default="tickets.json")
    commands = parser.add_subparsers(dest="command", required=True)

    create = commands.add_parser("create")
    create.add_argument("--title", required=True)
    create.add_argument("--description", required=True)
    create.add_argument("--priority", required=True)

    show = commands.add_parser("show")
    show.add_argument("id")

    return parser


def create_ticket(args):
    manager = load_tickets(args.file)
    ticket = Ticket(args.title, args.description, args.priority)
    manager.add(ticket)
    save_tickets(manager, args.file)

    print(ticket.id)
    return 0


def show_ticket(args):
    if not Path(args.file).exists():
        print(f"Ticket file {args.file} not found", file=sys.stderr)
        return 1
    return 0


def main(argv=None):
    args = build_parser().parse_args(argv)

    if args.command == "create":
        return create_ticket(args)
    return show_ticket(args)