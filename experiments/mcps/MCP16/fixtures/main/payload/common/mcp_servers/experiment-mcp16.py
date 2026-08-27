import json
import sys

MARKER = "AI_STP_MCP16"
for line in sys.stdin:
    r = json.loads(line)
    m = r.get("method")
    i = r.get("id")
    if i is None:
        continue
    if m == "initialize":
        v = {
            "protocolVersion": "2025-06-18",
            "capabilities": {"tools": {}},
            "serverInfo": {"name": MARKER, "version": "1"},
        }
    elif m == "tools/list":
        v = {
            "tools": [
                {
                    "name": "probe",
                    "description": MARKER,
                    "inputSchema": {"type": "object"},
                }
            ]
        }
    elif m == "tools/call":
        v = {"content": [{"type": "text", "text": MARKER}]}
    else:
        v = {}
    print(json.dumps({"jsonrpc": "2.0", "id": i, "result": v}), flush=True)
