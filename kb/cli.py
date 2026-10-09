import argparse
import sys

from kb.factory import make_client
from kb.formatting import preview

DEFAULT_TOP_K = 5

def positive_int(text):
    try:
        value = int(text)
    except ValueError:
        raise argparse.ArgumentTypeError(f"{text!r} is not a whole number")
    if value < 1:
        raise argparse.ArgumentTypeError("must be 1 or more")
    return value

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

    search = commands.add_parser(
        "search",
        help="search documents by text",
        description=(
            "Search titles, content and tags (case-insensitive). "
            "Prints one line per match."
        ),
    )
    search.add_argument("query", help="text to look for")
    search.add_argument(
        "--top-k",
        type=positive_int,
        default=DEFAULT_TOP_K,
        help=f"maximum number of results (default {DEFAULT_TOP_K})",
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

def search_documents(client, args):
    results = client.search(args.query, args.top_k)
    if not results:
        print("No documents found.")
        return 0
    for result in results:
        doc = result.document
        print(f"{doc.id}  {doc.title}  {doc.node_path}  [{result.match_type}]")
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
    elif args.command == "search":
        return search_documents(client, args)