import argparse
import sys

from kb.factory import make_client
from kb.formatting import preview
from pathlib import Path

DEFAULT_TOP_K = 5
DEFAULT_LIMIT = 10

def positive_int(text):
    try:
        value = int(text)
    except ValueError:
        raise argparse.ArgumentTypeError(f"{text!r} is not a whole number")
    if value < 1:
        raise argparse.ArgumentTypeError("must be 1 or more")
    return value

def parse_tags(text):
    return [tag.strip() for tag in text.split(",") if tag.strip()]

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

    list_command = commands.add_parser(
        "list",
        help="list the documents in a node",
        description=(
            "List the documents stored directly in one node (folder), "
            "for example /templates/email. Child nodes are not included."
        ),
    )
    list_command.add_argument(
        "--node", required=True, help="node path, e.g. /templates/email"
    )
    list_command.add_argument(
        "--limit",
        type=positive_int,
        default=DEFAULT_LIMIT,
        help=f"maximum number of documents (default {DEFAULT_LIMIT})",
    )

    add = commands.add_parser(
        "add",
        help="add a text file as a document",
        description=(
            "Add a text file to the knowledge base. The document title is the "
            "file name without its extension. Tags are separated by commas."
        ),
    )
    add.add_argument("--file", required=True, help="path of the text file to add")
    add.add_argument(
        "--path",
        dest="node_path",
        required=True,
        help="node to store it in, e.g. /templates/sms",
    )
    add.add_argument("--tags", default="", help="comma-separated tags, e.g. sms,promo")

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

def list_node(client, args):
    docs = client.list_documents(args.node, args.limit)
    if not docs:
        print("No documents found.")
        return 0
    for doc in docs:
        print(f"{doc.id}  {doc.title}  [{', '.join(doc.tags)}]")
    return 0

def add_document(client, args):
    path = Path(args.file)
    try:
        content = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as error:
        print(f"error: cannot read {args.file}: {error}", file=sys.stderr)
        return 1
    doc = client.add(path.stem, content, args.node_path, parse_tags(args.tags))
    print(f"Added {doc.id}  {doc.title}  {doc.node_path}")
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
    elif args.command == "list":
        return list_node(client, args)
    elif args.command == "add":
        return add_document(client, args)