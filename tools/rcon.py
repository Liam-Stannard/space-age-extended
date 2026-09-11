#!/usr/bin/env python3
"""Minimal Source-RCON client, for driving a headless Factorio server.

Drives the headless rig. Two gotchas it exists to work around: the
server exits on stdin EOF, and with no client attached it free-runs, so
measure against game.tick deltas rather than wall-clock sleeps.
"""

import socket
import struct
import sys
import time

SERVERDATA_AUTH, SERVERDATA_EXECCOMMAND = 3, 2


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


if __name__ == "__main__":
    r = Rcon()
    for line in sys.argv[1:]:
        print(r.cmd(line))
