The snapshot of progess for each week can be found in repo's tag
document of each week:
- _week1_excircise.md
- _week2_excircise.md
- _week3_excircise.md

# Week-2 tag: Ticket Manager

A simple command line tool for managing support tickets stored in a local JSON file. Create tickets, list them with filters and sorting, show one in detail with id, and update a ticket's status

Built test-first (TDD) with Python and pytest, using only standard libraries at run time

## Installation

Requires Python 3.10 or newer

```
python -m venv .venv

# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -e ".[dev]"
```

This installs the `tickets` command into the virtual environment and activate the it, additioning pytest for testing. Check it with:

```
tickets --help
```

You can also run it without the `tickets` command: `python -m ticket_manager <command>`.

## Configuration

There is one setting: where the tickets are stored.

- By default, tickets are stored in `tickets.json` in the same folder you run the command from
- `--file PATH` uses a different file. It goes **before** the command: `tickets --file work.json list`.
- `create` makes the file if it does not exist yet. Every other command reports an error for a missing file, so a mistyped path is not hidden by an empty result.
- The file is a JSON list of ticket records. It is safe to read and back up, but you should be extra careful editting it with hand: a file that fails validation is reported as corrupted and will never be overwritten, for safety reason

## Usage

### create

```
tickets create --title "Printer broken" --description "Office printer is down" --priority High --tags printer office
```

Prints the new ticket's id. Every ticket starts with status `Open`.

Any value you leave out is asked for interactively, and a value that is not valid is asked for again:

```
tickets create
Title: Printer broken
Description: Office printer is down
Priority (Low/Medium/High): Urgent
Invalid priority: Priority must be one of: Low, Medium, High
Priority (Low/Medium/High): High
Tags (space separated, optional): printer office
```

`--tags` on its own (with no words) means "no tags" and skips the question.

### list

```
tickets list
tickets list --status Open Pending
tickets list --priority High
tickets list --tags printer office
tickets list --status Open --priority High --tags printer
```

Filters combine with AND. Inside one filter:

| Option | Meaning |
|---|---|
| `--status A B` | status is A **or** B |
| `--priority A B` | priority is A **or** B |
| `--tags A B` | the ticket has **both** A and B |

Sorting:

```
tickets list --sort priority
tickets list --sort priority status
tickets list --sorttag printer office
tickets list --sort priority --sorttag printer
```

- `--sort priority` puts High first. `--sort status` follows the workflow order: Open, Pending, Waiting, Resolved, Closed.
- `--sorttag A B` puts tickets with the most matching tags first. Tag names are always read as tags, so a tag called `priority` is fine.
- Rules apply in the order given, and the first is the primary one. Each later rule only breaks ties. Tickets that still tie stay in the order they were created.
- Sorting happens after filtering.

Each line shows the id, status, priority and title. If nothing matches, it prints `No tickets found`.

### show

```
tickets show <id>
```

Prints every field of one ticket.

### update

```
tickets update <id> <status>
```

Changes a ticket's status to one of `Open`, `Pending`, `Waiting`, `Resolved`, `Closed`. Nothing else about the ticket changes.

## Ticket rules

| Field | Rule |
|---|---|
| id | 8 lowercase hex characters, generated on creation |
| title | required, cannot be blank, cut to 100 characters |
| description | required, cannot be blank |
| priority | `Low`, `Medium` or `High` |
| status | `Open`, `Pending`, `Waiting`, `Resolved` or `Closed` |
| tags | words without whitespace, not starting with `-`. Duplicates are merged |

Names of statuses and priorities are case-sensitive.

## Errors and exit codes

| Code | Meaning |
|---|---|
| 0 | Success (including a list with no matches) |
| 1 | A handled problem: ticket not found, missing file, corrupted file, no input available for a prompt |
| 2 | Bad command-line arguments, such as an unknown option or an invalid status |

Errors are printed to stderr without a traceback, and a failed command never writes the file. A corrupted file stays untouched so nothing is lost.

## Running the tests

```
pytest
```

The tests are in `tests/`, in two groups:

- **Unit tests:** ticket validation and updating, the manager, filtering and sorting, with no files involved.
- **Integration tests:** saving and loading real JSON files in temporary folders, and the CLI commands run through `main()` against temporary files, including missing, corrupted and invalid input cases.
- **End-to-end test** asks the operating system to actually launch the program, similar to typing down the command in a terminal, and then checks the output: exit code, what was printed, and data on the disk
## Project layout

```
ticket_manager/
    ticket.py      Ticket: fields, validation, atomic update, to/from dict
    manager.py     TicketManager: add, get, remove, update, iterate
    storage.py     save_tickets / load_tickets, StorageError
    filters.py     filter_tickets
    sorting.py     sort_groups, flatten, sort keys
    cli.py         argument parsing, command handlers, main()
    __main__.py    python -m ticket_manager
tests/             unit and integration tests
```

Dependencies point one way: `cli` uses `storage`, `manager`, `filters` and `sorting`, which use `ticket`. The ticket rules live in `Ticket` and nowhere else. Storage and the CLI never re-check them, they only report what `Ticket` rejects.

## Design notes

- **One command per process.** Every command loads the file, does its work and exits. Only commands that change something (`create`, `update`) save.
- **A corrupted file is an error, not an empty list.** Treating it as empty would let the next `create` overwrite everything.
- **Sorting uses tie groups.** Each sort rule splits groups of tied tickets into smaller groups, so a later rule can break ties without reordering anything the earlier rules decided.
- **Updates are all-or-nothing.** `Ticket.update` validates changes on a copy before touching the real ticket.

## Known limitations

- The entired file is read and rewritten on every command
- Not support multiple instance, the last one save the file overwrite everything
- A write that is interrupted halfway can leave a corrupted file, no temp file or back up, yet
- Only the status can be changed on an existing ticket from the command line, planning for `tickets edit` later
- A tag cannot start with `-`, because it would be mistaken for an option
- Design is primarily for the later idea of having a REPL handle the context, configs, easier to use command, command base on context (e.x. `update 2 Closed`), paging and ultilities.

# Week-3 tag: Knowledge Base CLI

A command line tool for working with a knowledge base (KB) of documents. Search it by keyword, list the documents under a node, retrieve one document by id, and add a new document from a text file.

The tool talks to the KB through one interface, `KBClient`. Two clients implement it: a **mock** client that keeps documents in a local JSON file, and an **HTTP** client that talks to a KB server. An environment variable picks which one is used. A small **fake server** is included, so the HTTP client can be tried and tested without a real KB.

## Installation

Requires Python 3.10 or newer

```
python -m venv .venv

# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -e ".[dev]"
```

This installs the `tickets` and `kb` commands into the virtual environment, plus pytest for testing. If you installed Week 2 before, run the command again so `kb` appears. Check it with:

```
kb --help
```

You can also run it without the `kb` command: `python -m kb <command>`.

## Configuration

Settings are read from environment variables. None of them is required. When you
run `kb` from a directory containing a `.env` file, its settings are loaded automatically. Variables already set in the shell take precedence over values in `.env`.

| Variable | Default | Meaning |
|---|---|---|
| `KB_CLIENT` | `mock` | `mock` or `http`. Anything else is an error |
| `KB_MOCK_FILE` | `kb.json` | File used by the mock client |
| `KB_API_URL` | (none) | Base URL of the KB server, for example `http://127.0.0.1:8080`. Required when `KB_CLIENT=http` |

Windows (PowerShell): `$env:KB_CLIENT = "http"`. macOS / Linux: `export KB_CLIENT=http`.
Alternatively, set `KB_CLIENT` and `KB_API_URL` in `.env` in the directory
where you run `kb`; use the fake server URL above to try HTTP mode.

- **Mock data file.** If the mock file does not exist, the client starts with six built-in documents (templates, team pages, guides). The file is created the first time `kb add` saves something, and it then holds all documents, built-in ones included.
- **Corrupted file.** If the mock file is not valid JSON, is not a list, or has a bad record, the command reports an error and the file is never overwritten.
- **HTTP timeout.** The HTTP client waits at most 5 seconds for an answer.

### Fake server

```
python -m kb.fake_server
python -m kb.fake_server --port 9000 --file my-kb.json --latency 50 150
```

| Option | Default | Meaning |
|---|---|---|
| `--host` | `127.0.0.1` | Address to listen on |
| `--port` | `8080` | Port to listen on. `0` picks a free port |
| `--file` | `kb-server.json` | Where the server keeps its documents (same format as the mock file) |
| `--latency MIN MAX` | off | Delay every answer by a random time between MIN and MAX **milliseconds** |

It prints `KB fake server listening on http://host:port (Ctrl+C to stop)` when it is ready. In a second terminal:

```
set KB_CLIENT=http
set KB_API_URL=http://127.0.0.1:8080
kb list --node /team/devops
```

## Usage

### retrieve

```
kb retrieve doc-002
kb retrieve doc-002 --full
```

Prints a small header (id and title, node, tags), a blank line, then the start of the content. By default only the first 3 lines are shown, and each line is wrapped at 80 characters, with `...` added when something was cut. `--full` prints the whole content.

### search

```
kb search deploy
kb search email --top-k 3
```

Finds documents whose title, content or tags contain the query (case-insensitive). Each line shows the id, title, node and how it matched, for example `doc-006  Deployment Guide  /docs/guides  [keyword]`. `--top-k` limits the number of results (default 5).

### list

```
kb list --node /templates/email
kb list --node /team/devops --limit 1
```

Lists the documents stored **exactly** at that node (sub-nodes are not included). Each line shows the id, title and tags. `--node` is required. `--limit` defaults to 10.

### add

```
kb add --file notes.txt --path /docs/guides --tags guide onboarding
```

Reads the content from a text file and prints `Added <id>  <title>  <node>`. The new id looks like `doc-1a2b3c4d`. The title is the file name without its extension (`welcome-sms.md` becomes `welcome-sms`).

Any value you leave out is asked for interactively, and a value that is not valid is asked for again:

```
kb add
File to add: missing.txt
Invalid file: cannot read missing.txt
File to add: notes.txt
Node path (e.g. /templates/sms):
Invalid node path: must not be blank
Node path (e.g. /templates/sms): /templates/sms
Tags (space separated, optional): sms short
```

Tags are optional: an empty answer means no tags. Tags given with `--tags` go through the same checks.

`--top-k` and `--limit` must be whole numbers of 1 or more. Anything else is a usage error.

## Document rules

| Field | Rule |
|---|---|
| id | not empty. Generated as `doc-` plus 8 hex characters on `add` |
| title | text, no extra rules |
| content | text, no extra rules |
| node_path | for `add`: cannot be blank. Any text is accepted when loading |
| tags | list of words without whitespace, not starting with `-`. Duplicates are merged, order is kept |

Names are case-sensitive, and the tool does not change what it receives (no trimming, no lowercasing) as long as it does not break searching.

## HTTP API

This is what the HTTP client expects from a server (and what the fake server provides). Every endpoint is a `POST` with a JSON body, and every answer is JSON.

| Path | Request body | Success | Failure |
|---|---|---|---|
| `/retrieve` | `{"docId"}` | 200 `{"document": {...}}` | 404 `{"error": "..."}` if unknown |
| `/search` | `{"query", "topK"}` | 200 `{"results": [{"id", "title", "nodePath", "matchType"}]}` | 400 bad request |
| `/list` | `{"nodePath", "limit"}` | 200 `{"documents": [...]}` | 400 bad request |
| `/add` | `{"title", "content", "nodePath", "tags"}` | 201 `{"document": {...}}` | 400 bad request |

- A document on the wire has `id`, `title`, `content`, `nodePath` and `tags`.
- Search results carry no content, so a result is a document with empty content and no tags.
- Unknown paths answer 404, and a body that is not a JSON object got a 400.
- Names are camelCase **only on the wire** (`nodePath`, `topK`, `docId`). Inside the code and in files they are `node_path`, `top_k`, `doc_id`.

## Errors and exit codes

| Code | Meaning |
|---|---|
| 0 | Success (including a search or list with no results) |
| 1 | A handled problem: unknown document id, bad `KB_CLIENT` or missing `KB_API_URL`, corrupted mock file, server unreachable or answered with an error, no input available for a prompt |
| 2 | Bad command-line arguments, such as an unknown option or `--top-k 0` |

Errors are printed to stderr without a traceback. A failed command never writes the mock file. Empty results print `No documents found.` and still exit with 0.

## Running the tests

```
pytest
```

This runs all `tests/` (Week 2) and `test_kb/` (Week 3). The Week 3 tests are in four groups:

- **Unit tests:** documents, search results, the `KBClient` interface, the factory and the text preview, with no network and no real files.
- **Contract tests:** one set of tests for what any client must do, run against **both** the mock client and the HTTP client (talking to a fake server in the same process). A new client kind only needs to be added to the `CLIENT_KINDS` list in `test_kb/conftest.py`.
- **Integration tests:** mock file storage and corruption, the fake server (endpoints, errors, latency), the HTTP client against broken servers (unreachable, too slow, malformed answers), and the CLI commands through `main()`.
- **End-to-end tests:** start `python -m kb` and `python -m kb.fake_server` as real processes, as typing in a terminal would, and check exit codes, output and data on disk, including a server restart.

## Project layout

```
kb/
    document.py      Document: fields, validation, to/from dict
    search_result.py SearchResult: a document plus how it matched
    client.py        KBClient: the interface (abstract methods)
    errors.py        KBStorageError, KBApiError
    mock_client.py   MockKBClient: JSON file, built-in documents
    http_client.py   HTTPKBClient: urllib, timeout, error handling
    factory.py       make_client: picks a client from the environment
    formatting.py    preview: wrapping and cutting long text
    prompts.py       asking again until a value is valid, input checks
    cli.py           argument parsing, command handlers, main()
    fake_server.py   test KB server and its command line
    __main__.py      python -m kb
test_kb/             unit, contract, integration and end-to-end tests
ticket_manager/      Week 2 (unchanged)
tests/               Week 2 tests (unchanged)
```

Dependencies point one way: `cli` uses `factory`, `prompts` and `formatting`. The factory is the only place that knows the concrete client classes, and the clients implement `KBClient` and use `Document` and `SearchResult`. The CLI only ever talks to the interface, so it does not know which client it has.

## Design notes

- **One command per process.** The client is created for each command and dies with it. That is why the mock keeps its documents in a file, so a document added by one command is found by the next.
- **One interface, two clients.** The same contract tests run on both, so they cannot drift apart.
- **The factory is the only switch.** Choosing a client is a decision about the environment, so it is made in one place, with an environment dict that tests can pass in.
- **A corrupted file is an error, not an empty list.** Prevent `add` from incorrectly overwrite data.
- **Wire names stay on the wire.** Conversion between `nodePath` and `node_path` happens in one function in the HTTP client and one in the fake server.
- **Malformed answers are one error.** Anything wrong with a server answer (not JSON, missing fields, wrong types, HTTP errors, timeouts) becomes `KBApiError`, which the CLI prints without a traceback.
- **A fake server instead of a real KB.** No credetial.
- **Latency simulating is counted from arrival.** The delay is a random time between MIN and MAX measured from when the request arrived, so slow handling is not delayed twice.
- **The server reads the whole request before answering**, even when it will answer with an error. Answering early can reset the connection and made one test flaky.

## Known limitations

- 404 from `/retrieve` means "document not found". A server with a wrong URL prefix would behave like an empty knowledge base for `retrieve`
- Search results from the HTTP API carry no content, so they not yet can be previewed without a follow up `retrieve`.
- The mock matching by plain substring on title, content, and tags, with no ranking. `match_type` is always `keyword`, could implememtn more matching method later
- The mock file is read and rewritten fully on every command, with no locking, so two instances at once can overwrite each other
- A write that is interrupted halfway can leave a corrupted mock file, no temp file or backup yet
- Built-in documents are shared between mock clients in the same process (not a problem for one command per process)
- The fake server handles one request at a time. It does not have a guard against a negative `Content-Length`, and unexpected errors inside it wont turn into a 500 answer.
- The HTTP client has a fixed 5 second timeout, with no retry and no authentication
- `kb list` needs `--node`, and sub-nodes are not included
- A tag cannot start with a dash `-`, since it would be mistaken for an option
- Haven't implement the sorting for tag system yet
- The project structure was built with the idea of having a REPL shell handling context, command generation and client life management later.
