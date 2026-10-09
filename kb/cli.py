import argparse
import sys

from kb.factory import make_client


def build_parser():
    parser = argparse.ArgumentParser(prog="kb")
    commands = parser.add_subparsers(dest="command", required=True)

    retrieve = commands.add_parser("retrieve", help="show one document")
    retrieve.add_argument("doc_id")

    return parser


def retrieve_document(client, args):
    doc = client.retrieve(args.doc_id)
    if doc is None:
        print(f"error: no document with id {args.doc_id}", file=sys.stderr)
        return 1
    print(f"{doc.id}  {doc.title}")
    print(f"node: {doc.node_path}")
    print(f"tags: {', '.join(doc.tags)}")
    print()
    print(doc.content)
    return 0


def main(argv=None, environ=None):
    try:
        args = build_parser().parse_args(argv)
    except SystemExit as error:
        return error.code

    try:
        client = make_client(environ)
    except ValueError as error:
        print(f"error: {error}", file=sys.stderr)
        return 1

    if args.command == "retrieve":
        return retrieve_document(client, args)