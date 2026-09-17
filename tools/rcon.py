#!/usr/bin/env python3
"""Minimal Source-RCON client, for driving a headless Factorio server.

Drives the headless rig. Two gotchas it exists to work around: the
server exits on stdin EOF, and with no client attached it free-runs, so
measure against game.tick deltas rather than wall-clock sleeps.
A third: the first Lua command a fresh server receives is swallowed by the
"using Lua console commands will disable achievements, repeat to proceed"
warning and returns an empty reply -- send a throwaway command first.
A fourth: a headless server auto-pauses while no player is connected, so
game.tick stands still and a test that waits for ticks waits forever --
the server settings have to say "auto_pause": false.

A Lua error is otherwise silent over RCON: the command fails, nothing is
printed, and the reply is the same empty string a successful command gives.
Use lua() -- or the --lua CLI flag -- to have failures come back as
"LUA ERROR: <message>" instead of as nothing at all.

  tools/rcon.py '/c rcon.print(1+1)'      # raw commands, unchanged
  tools/rcon.py --lua 'rcon.print(1+1)'   # chunks; exit 1 on any Lua error
"""

import socket
import struct
import sys
import time

SERVERDATA_AUTH, SERVERDATA_EXECCOMMAND = 3, 2

LUA_ERROR = "LUA ERROR: "

# A console command is one line, so anything that would break the Lua string
# literal the chunk is passed in -- a quote, a backslash, a newline -- is
# escaped rather than sent raw.
ESCAPES = {"\\": "\\\\", '"': '\\"', "\n": "\\n", "\r": "\\r", "\t": "\\t"}


class Rcon:
    def __init__(self, host="127.0.0.1", port=27016, password="x", timeout=20):
        self.sock = socket.create_connection((host, port), timeout=timeout)
        self.rid = 0
        self._send(SERVERDATA_AUTH, password)
        if self._recv()[0] == -1:
            raise SystemExit("rcon auth failed")

    def _send(self, kind, body):
        self.rid += 1
        payload = struct.pack("<ii", self.rid, kind) + body.encode() + b"\x00\x00"
        self.sock.sendall(struct.pack("<i", len(payload)) + payload)
        return self.rid

    def _read(self, n):
        buf = b""
        while len(buf) < n:
            chunk = self.sock.recv(n - len(buf))
            if not chunk:
                raise SystemExit("rcon connection closed")
            buf += chunk
        return buf

    def _recv(self):
        size = struct.unpack("<i", self._read(4))[0]
        data = self._read(size)
        rid, _ = struct.unpack("<ii", data[:8])
        return rid, data[8:-2].decode(errors="replace")

    def cmd(self, command):
        self._send(SERVERDATA_EXECCOMMAND, command)
        time.sleep(0.15)
        self.sock.settimeout(6)
        out = []
        try:
            while True:
                out.append(self._recv()[1])
        except (socket.timeout, SystemExit):
            pass
        return "".join(out).strip()

    def lua(self, src):
        """Run one Lua chunk, reporting a compile or runtime error.

        The chunk is compiled with load() and run under pcall() on the
        server, so neither a syntax error nor an error() at runtime can
        pass for a command that simply printed nothing.
        """
        literal = '"%s"' % "".join(ESCAPES.get(c, c) for c in src)
        return self.cmd(
            "/silent-command local f, err = load(%s, 'rcon') "
            "if not f then rcon.print('%s' .. err) return end "
            "local ok, res = pcall(f) "
            "if not ok then rcon.print('%s' .. tostring(res)) end"
            % (literal, LUA_ERROR, LUA_ERROR))


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if a != "--lua"]
    as_lua = len(args) != len(sys.argv) - 1
    r = Rcon()
    failed = False
    for line in args:
        reply = r.lua(line) if as_lua else r.cmd(line)
        print(reply)
        if reply.startswith(LUA_ERROR):
            failed = True
    sys.exit(1 if failed else 0)
