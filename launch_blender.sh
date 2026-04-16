#!/usr/bin/env bash
# Launch Blender with the MCP socket server running.
# Usage: ./launch_blender.sh [blender-file.blend]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MCP_SCRIPT="$SCRIPT_DIR/start_mcp_server.py"
BLENDER_PID=""

cleanup() {
    if [ -n "$BLENDER_PID" ] && kill -0 "$BLENDER_PID" 2>/dev/null; then
        echo "Cleaning up: stopping Blender (PID $BLENDER_PID)..."
        kill "$BLENDER_PID" 2>/dev/null || true
    fi
}

# Find Blender
if command -v blender &>/dev/null; then
    BLENDER=blender
elif [ -x "/Applications/Blender.app/Contents/MacOS/blender" ]; then
    BLENDER="/Applications/Blender.app/Contents/MacOS/blender"
else
    echo "Error: Blender not found. Install it from https://www.blender.org/download/"
    exit 1
fi

# Kill any existing Blender MCP instances to avoid port conflicts and zombie processes
EXISTING=$(pgrep -f "blender.*start_mcp_server" 2>/dev/null || true)
if [ -n "$EXISTING" ]; then
    echo "Killing existing Blender MCP instance(s): $EXISTING"
    kill $EXISTING 2>/dev/null || true
    sleep 1
fi

echo "Starting Blender with MCP server on port 9876..."
if [ $# -gt 0 ]; then
    "$BLENDER" "$1" --python "$MCP_SCRIPT" &
else
    "$BLENDER" --python "$MCP_SCRIPT" &
fi

BLENDER_PID=$!
trap cleanup EXIT

# Wait for the socket server to come up
for i in $(seq 1 10); do
    if python3 -c "import socket; s=socket.socket(); s.settimeout(1); s.connect(('localhost',9876)); s.close()" 2>/dev/null; then
        echo "MCP server is ready on port 9876."
        echo "Blender PID: $BLENDER_PID"
        echo ""
        echo "Next: open Claude Code in the blender-agent directory and run /mcp to connect."
        trap - EXIT  # Clear trap — Blender is healthy, don't kill on exit
        exit 0
    fi
    sleep 1
done

echo "Warning: MCP server did not start within 10 seconds. Check Blender's console for errors."
exit 1
