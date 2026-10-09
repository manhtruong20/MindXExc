import argparse
import sys

from kb.factory import make_client
from kb.formatting import preview


def build_parser():
    parser = argparse.ArgumentParser(prog="kb")
    commands = parser.add_subparsers(dest="command", required=True)

    retrieve = commands.add_parser(
        "retrieve",
        help="show one document by id",
        description=(
            "Show one document: a small header, then a preview of its content "
            "(first 3 lines, wrapped at 80 characters). Use --full to print "
            "the whole content."
        ),
    )
    retrieve.add_argument("doc_id", help="id of the document, e.g. doc-001")
    retrieve.add_argument(
        "--full",
        action="store_true",
        help="print the whole content instead of a 3-line preview",
    )

    return parser


def retrieve_document(client, args):
    """Print one document: a small header, then its content.

    The content is a short preview by default, to keep terminal output
    readable. With --full the whole content is printed instead, so a template
    can be copied out in one piece.
    """
    doc = client.retrieve(args.doc_id)
    if doc is None:
        print(f"error: no document with id {args.doc_id}", file=sys.stderr)
        return 1
    print(f"{doc.id}  {doc.title}")
    print(f"node: {doc.node_path}")
    print(f"tags: {', '.join(doc.tags)}")
    print()
    print(doc.content if args.full else preview(doc.content))
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