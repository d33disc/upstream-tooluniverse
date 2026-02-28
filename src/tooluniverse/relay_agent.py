"""Relay agent — bridges a local FastMCP server to the ToolUniverse relay.

Usage (standalone):
    python -m tooluniverse.relay_agent \\
        --service https://tooluniverse.example.com \\
        --api-key tu-sk-xxx \\
        --mcp-url http://localhost:8080 \\
        --name "My GPU"

Usage (from smcp_server.py --remote-relay flag):
    agent = RelayAgent(
        service_url="https://...",
        api_key="tu-sk-xxx",
        mcp_url="http://localhost:8080",
        name="My GPU",
    )
    agent.run_forever()  # blocks until SIGINT; use threading.Thread(target=..., daemon=True)
"""

from __future__ import annotations

import argparse
import json
import os
import signal
import sys
import threading
import time
from typing import Optional

import requests


class RelayAgent:
    """WebSocket relay agent that bridges a local FastMCP server to the ToolUniverse service.

    The agent:
      1. POSTs to /remote-servers to create (or reuse) a relay record and obtain a token
      2. Opens a WebSocket to /ws/agent?token=<token>
      3. Sends tools/list to the local FastMCP server, forwards the result as a register message
      4. Enters a ping/pong + mcp_request forwarding loop
      5. Reconnects with exponential backoff on disconnect
    """

    BACKOFF_BASE = 1.0
    BACKOFF_MAX = 60.0

    def __init__(
        self,
        service_url: str,
        api_key: str,
        mcp_url: str,
        name: str,
    ):
        self.service_url = service_url.rstrip("/")
        self.api_key = api_key
        self.mcp_url = mcp_url.rstrip("/")
        self.name = name
        self._stop_event = threading.Event()
        self._token: Optional[str] = None
        self._server_id: Optional[str] = None
        self._relay_url: Optional[str] = None
        self._share_code: Optional[str] = None

    # ── Setup ─────────────────────────────────────────────────────────────────

    def _register_server(self) -> str:
        """POST /remote-servers and return plaintext token."""
        resp = requests.post(
            f"{self.service_url}/remote-servers",
            json={"name": self.name},
            headers={"Authorization": f"Bearer {self.api_key}"},
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()
        self._server_id = data["id"]
        self._relay_url = data["relay_url"]
        token = data["token"]
        print(f"  Relay URL : {self.service_url}{self._relay_url}")
        expires = data.get("expires_at")
        call_limit = data.get("call_limit")
        plan_desc = (
            "Pro · unlimited"
            if not expires
            else f"Free · expires {expires} · {call_limit} calls"
        )
        print(f"  Plan      : {plan_desc}")
        return token

    def _fetch_tools(self) -> list:
        """Call tools/list on the local FastMCP server."""
        try:
            payload = {"jsonrpc": "2.0", "method": "tools/list", "id": 1, "params": {}}
            resp = requests.post(
                f"{self.mcp_url}/mcp",
                json=payload,
                timeout=10,
            )
            resp.raise_for_status()
            data = resp.json()
            tools = data.get("result", {}).get("tools", [])
            return tools
        except Exception as exc:
            print(
                f"  [relay_agent] Warning: could not fetch tools from {self.mcp_url}: {exc}"
            )
            return []

    def _forward_mcp(self, method: str, params: dict) -> dict:
        """Forward a JSON-RPC request to the local FastMCP server."""
        payload = {"jsonrpc": "2.0", "method": method, "id": 1, "params": params or {}}
        try:
            resp = requests.post(
                f"{self.mcp_url}/mcp",
                json=payload,
                timeout=60,
            )
            resp.raise_for_status()
            return resp.json()
        except Exception as exc:
            return {
                "jsonrpc": "2.0",
                "id": 1,
                "error": {"code": -32603, "message": str(exc)},
            }

    # ── WebSocket loop ─────────────────────────────────────────────────────────

    def _ws_loop(self, token: str) -> None:
        """Open WebSocket, register tools, and process messages until disconnect."""
        try:
            import websocket  # type: ignore[import]
        except ImportError:
            print(
                "  [relay_agent] websocket-client not installed. Run: pip install websocket-client"
            )
            raise

        ws_url = self.service_url.replace("http://", "ws://").replace(
            "https://", "wss://"
        )
        ws_url = f"{ws_url}/ws/agent?token={token}"

        ws = websocket.WebSocket()
        ws.connect(ws_url)

        # Send tool list
        tools = self._fetch_tools()
        ws.send(json.dumps({"type": "register", "tools": tools}))

        # Wait for registered confirmation
        raw = ws.recv()
        msg = json.loads(raw)
        if msg.get("type") == "registered":
            self._relay_url = msg.get("relay_url", self._relay_url)
            self._share_code = msg.get("share_code")
            if self._share_code:
                print(f"  Share code: {self._share_code}")
            print("  [relay_agent] Connected and registered.")

        # Message loop
        ws.settimeout(45)  # slightly > server ping interval (30s)
        while not self._stop_event.is_set():
            try:
                raw = ws.recv()
            except websocket.WebSocketTimeoutException:
                # Send a keepalive ping
                ws.send(json.dumps({"type": "pong"}))
                continue

            if not raw:
                break

            try:
                msg = json.loads(raw)
            except json.JSONDecodeError:
                continue

            msg_type = msg.get("type")

            if msg_type == "ping":
                ws.send(json.dumps({"type": "pong"}))

            elif msg_type == "mcp_request":
                req_id = msg.get("req_id", "")
                method = msg.get("method", "")
                params = msg.get("params", {})
                result = self._forward_mcp(method, params)
                ws.send(
                    json.dumps(
                        {
                            "type": "mcp_response",
                            "req_id": req_id,
                            "result": result,
                        }
                    )
                )

        ws.close()

    # ── Public API ─────────────────────────────────────────────────────────────

    def run_forever(self) -> None:
        """Run the relay agent with auto-reconnect. Blocks until stop() or SIGINT."""
        print(f"\n  [relay_agent] Registering server '{self.name}'...")
        try:
            token = self._register_server()
        except Exception as exc:
            print(f"  [relay_agent] Registration failed: {exc}")
            return

        backoff = self.BACKOFF_BASE
        while not self._stop_event.is_set():
            try:
                self._ws_loop(token)
            except Exception as exc:
                if self._stop_event.is_set():
                    break
                print(
                    f"  [relay_agent] Disconnected ({exc}), reconnecting in {backoff:.0f}s…"
                )
                time.sleep(backoff)
                backoff = min(backoff * 2, self.BACKOFF_MAX)
            else:
                if not self._stop_event.is_set():
                    print("  [relay_agent] Connection closed, reconnecting in 1s…")
                    time.sleep(1)
                    backoff = self.BACKOFF_BASE

        print("  [relay_agent] Stopped.")

    def stop(self) -> None:
        """Signal the agent to stop reconnecting."""
        self._stop_event.set()


# ── CLI entry point ────────────────────────────────────────────────────────────


def main() -> None:
    parser = argparse.ArgumentParser(
        description="ToolUniverse relay agent — bridge a local FastMCP server to the relay service",
    )
    parser.add_argument(
        "--service",
        required=True,
        help="ToolUniverse service base URL (e.g. https://tooluniverse.example.com)",
    )
    parser.add_argument(
        "--api-key",
        default=os.getenv("TOOLUNIVERSE_SERVICE_KEY", ""),
        help="ToolUniverse API key (or set TOOLUNIVERSE_SERVICE_KEY)",
    )
    parser.add_argument(
        "--mcp-url",
        default="http://localhost:8080",
        help="Local FastMCP server base URL (default: http://localhost:8080)",
    )
    parser.add_argument(
        "--name",
        default="Remote GPU Server",
        help="Display name for this server in the web UI",
    )
    args = parser.parse_args()

    if not args.api_key:
        print("Error: --api-key or TOOLUNIVERSE_SERVICE_KEY is required")
        sys.exit(1)

    agent = RelayAgent(
        service_url=args.service,
        api_key=args.api_key,
        mcp_url=args.mcp_url,
        name=args.name,
    )

    # Handle SIGINT gracefully
    def _handle_sigint(sig, frame):
        print("\n  [relay_agent] Interrupted — shutting down…")
        agent.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, _handle_sigint)

    print(f"Starting relay agent for '{args.name}'")
    print(f"  Service   : {args.service}")
    print(f"  Local MCP : {args.mcp_url}")
    agent.run_forever()


if __name__ == "__main__":
    main()
