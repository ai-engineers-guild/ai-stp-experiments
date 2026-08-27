import json
import sys

for line in sys.stdin:
    request = json.loads(line)
    method = request.get("method")
    result = {"jsonrpc": "2.0", "id": request.get("id")}
    if method == "initialize":
        result["result"] = {"protocolVersion": "2024-11-05", "capabilities": {"tools": {}}, "serverInfo": {"name": "experiment-mcp01", "version": "1.0"}}
    elif method == "tools/list":
        result["result"] = {"tools": [{"name": "probe", "description": "probe", "inputSchema": {"type": "object", "properties": {}}}]}
    elif method == "tools/call":
        result["result"] = {"content": [{"type": "text", "text": "AI_STP_MCP01"}]}
    else:
        result["result"] = {}
    print(json.dumps(result), flush=True)
