"""
Simple JSON-over-TCP RPC utilities.

Protocol (newline-delimited JSON):
  Request: {"id": <str>, "method": "process", "params": <PipelineMessage dict>}
  Response: {"id": <str>, "result": <PipelineMessage dict>} or {"id": <str>, "error": <message>}

This module provides a tiny server (`serve`) and a client helper (`rpc_call`).
"""
import json
import socket
import threading
from typing import Callable, Dict, Any, Optional
import socketserver


def _safe_json_dumps(obj: Any) -> str:
    return json.dumps(obj, default=str)


class _RPCHandler(socketserver.StreamRequestHandler):
    """Internal handler that delegates to a provided function."""

    def handle(self):
        # Read a single line (one JSON request) and respond with JSON line
        raw = self.rfile.readline()
        if not raw:
            return
        try:
            data = json.loads(raw.decode("utf-8"))
        except Exception as e:
            resp = {"id": None, "error": f"invalid_json: {e}"}
            self.wfile.write((_safe_json_dumps(resp) + "\n").encode("utf-8"))
            return

        # Delegate
        try:
            handler = self.server._handler  # type: ignore[attr-defined]
            result = handler(data.get("params"))
            resp = {"id": data.get("id"), "result": result}
        except Exception as e:
            resp = {"id": data.get("id"), "error": str(e)}

        self.wfile.write((_safe_json_dumps(resp) + "\n").encode("utf-8"))


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True


def serve(handler_func: Callable[[Dict[str, Any]], Dict[str, Any]], host: str = "0.0.0.0", port: int = 8000):
    """Start an RPC server that calls handler_func with params dict and returns dict result.

    This call blocks the current thread. It runs a threaded server to handle concurrent requests.
    """
    server = ThreadedTCPServer((host, port), _RPCHandler)
    # Attach handler to server instance for handler to use
    server._handler = handler_func

    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()
    return server


def rpc_call(host: str, port: int, params: Dict[str, Any], timeout: Optional[float] = 10.0) -> Dict[str, Any]:
    """Call a remote RPC server and return the parsed response dict.

    Raises an exception on error responses or socket issues.
    """
    req = {"id": "1", "method": "process", "params": params}
    payload = _safe_json_dumps(req) + "\n"
    with socket.create_connection((host, port), timeout=timeout) as sock:
        sock.sendall(payload.encode("utf-8"))
        # read until newline
        buf = b""
        while True:
            chunk = sock.recv(4096)
            if not chunk:
                break
            buf += chunk
            if b"\n" in buf:
                break
        if not buf:
            raise RuntimeError("no response from server")
        line, _sep, _rest = buf.partition(b"\n")
        resp = json.loads(line.decode("utf-8"))
        if resp.get("error"):
            raise RuntimeError(resp["error"])
        return resp.get("result")
