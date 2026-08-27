import { spawn } from "node:child_process";
import { existsSync, readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

type Server = { command: string; args?: string[]; env?: Record<string, string> };

function start(server: Server, cwd: string) {
  const child = spawn(server.command, server.args ?? [], { cwd, env: { ...process.env, ...(server.env ?? {}) }, stdio: ["pipe", "pipe", "ignore"], windowsHide: true });
  let buffer = "";
  let sequence = 0;
  const pending = new Map<number, (value: any) => void>();
  child.stdout.on("data", (chunk) => {
    buffer += chunk.toString();
    while (buffer.includes("\n")) {
      const end = buffer.indexOf("\n");
      const line = buffer.slice(0, end).trim();
      buffer = buffer.slice(end + 1);
      if (!line) continue;
      const message = JSON.parse(line);
      if (typeof message.id === "number") pending.get(message.id)?.(message.result);
      pending.delete(message.id);
    }
  });
  const request = (method: string, params?: object) => new Promise<any>((resolve) => {
    const id = ++sequence;
    pending.set(id, resolve);
    child.stdin.write(JSON.stringify({ jsonrpc: "2.0", id, method, params }) + "\n");
  });
  return { child, request };
}

export default async function (pi: any) {
  const extensionDir = dirname(fileURLToPath(import.meta.url));
  const configPath = join(extensionDir, ".mcp.json");
  if (!existsSync(configPath)) return;
  const config = JSON.parse(readFileSync(configPath, "utf8")) as { mcpServers?: Record<string, Server> };
  const clients = Object.entries(config.mcpServers ?? {}).map(([name, server]) => ({ name, ...start(server, extensionDir) }));
  for (const client of clients) {
    await client.request("initialize", { protocolVersion: "2025-06-18", capabilities: {}, clientInfo: { name: "pi-mcp-bridge", version: "1" } });
    client.child.stdin.write(JSON.stringify({ jsonrpc: "2.0", method: "notifications/initialized" }) + "\n");
    const listed = await client.request("tools/list");
    for (const tool of listed?.tools ?? []) {
      const name = `mcp_${client.name}_${tool.name}`.replace(/[^a-zA-Z0-9_]/g, "_");
      pi.registerTool({ name, label: name, description: tool.description ?? `MCP tool ${tool.name}`, parameters: tool.inputSchema ?? { type: "object", properties: {} }, async execute(_id: string, input: object) {
        const result = await client.request("tools/call", { name: tool.name, arguments: input });
        return { content: result?.content ?? [], details: { mcpServer: client.name, mcpTool: tool.name } };
      } });
    }
  }
  pi.on("session_shutdown", () => clients.forEach((client) => client.child.kill()));
}
