#!/usr/bin/env python3
"""Execute Python code in Blender via the MCP socket server.

Usage:
    python scripts/blender_exec.py <script_file.py>
    python scripts/blender_exec.py -c "import bpy; print(bpy.app.version_string)"
"""

import socket
import json
import sys
import argparse


def execute_in_blender(code: str, host: str = "localhost", port: int = 9876, timeout: int = 170) -> dict:
    """Send code to Blender's MCP socket server and return the result."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    try:
        sock.connect((host, port))
        cmd = json.dumps({"type": "execute_code", "params": {"code": code}})
        sock.sendall(cmd.encode("utf-8") + b"\n")

        # Read response - may come in chunks
        chunks = []
        while True:
            try:
                chunk = sock.recv(65536)
                if not chunk:
                    break
                chunks.append(chunk.decode("utf-8"))
                # Try to parse what we have
                try:
                    json.loads("".join(chunks))
                    break  # Valid JSON, we're done
                except json.JSONDecodeError:
                    continue  # Need more data
            except socket.timeout:
                break

        response_text = "".join(chunks)
        return json.loads(response_text)
    finally:
        sock.close()


def main():
    parser = argparse.ArgumentParser(description="Execute Python code in Blender")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("script", nargs="?", help="Path to Python script file")
    group.add_argument("-c", "--code", help="Code string to execute")
    parser.add_argument("--timeout", type=int, default=300, help="Socket timeout in seconds")
    args = parser.parse_args()

    if args.code:
        code = args.code
    else:
        with open(args.script, "r") as f:
            code = f.read()

    result = execute_in_blender(code, timeout=args.timeout)

    if result.get("status") == "success":
        output = result.get("result", {}).get("result", "")
        if output:
            print(output)
    else:
        print(f"ERROR: {result.get('message', 'Unknown error')}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
