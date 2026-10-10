"""A stand-in for the real Knowledge Base server, used for tests and demos.

It speaks the JSON-over-HTTP API from the assignment (POST /search, /list,
/retrieve, /add) and keeps its data in a MockKBClient.
"""

import json
import random
import threading
import time
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, HTTPServer


def document_to_json(doc):
    return {
        "id": doc.id,
        "title": doc.title,
        "content": doc.content,
        "nodePath": doc.node_path,
        "tags": list(doc.tags),
    }


def require(body, name):
    if name not in body:
        raise ValueError(f"missing field {name!r}")
    return body[name]


def retrieve_route(client, body):
    doc_id = require(body, "docId")
    doc = client.retrieve(doc_id)
    if doc is None:
        return 404, {"error": f"no document with id {doc_id}"}
    return 200, {"document": document_to_json(doc)}


ROUTES = {
    "/retrieve": retrieve_route,
}


def make_server(client, host="127.0.0.1", port=0, latency=None, sleep=time.sleep):
    """Build the fake server (not started yet).

    latency: None for instant answers, or (min_seconds, max_seconds), for
    example (0.05, 0.15). Every response then waits a random time in that
    range, to imitate a real network. `sleep` can be replaced in tests.
    """

    def pause(arrived):
        if latency is None:
            return
        remaining = random.uniform(*latency) - (time.monotonic() - arrived)
        if remaining > 0:
            sleep(remaining)

    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):
            self.arrived = time.monotonic()
            route = ROUTES.get(self.path)
            if route is None:
                self.send_json(404, {"error": f"unknown path {self.path}"})
                return
            try:
                length = int(self.headers.get("Content-Length", 0))
                body = json.loads(self.rfile.read(length) or b"{}")
                if not isinstance(body, dict):
                    raise ValueError("the body must be a JSON object")
                status, payload = route(client, body)
            except ValueError as error:
                self.send_json(400, {"error": f"bad request: {error}"})
                return
            self.send_json(status, payload)

        def send_json(self, status, payload):
            pause(self.arrived)
            data = json.dumps(payload).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def log_message(self, format, *args):
            pass

    return HTTPServer((host, port), Handler)

@contextmanager
def serve_in_background(server):
    """Run `server` in a background thread; yield its base URL, stop it after."""
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        host, port = server.server_address
        yield f"http://{host}:{port}"
    finally:
        server.shutdown()
        server.server_close()
        thread.join()