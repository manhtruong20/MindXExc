# Ticket Manager

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