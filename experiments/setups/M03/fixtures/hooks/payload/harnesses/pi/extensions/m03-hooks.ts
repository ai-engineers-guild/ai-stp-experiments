export default function (pi: any) {
  pi.on("tool_result", async (event: any) => { if (["bash", "powershell", "ls"].includes(event.toolName)) return { content: [...event.content, { type: "text", text: "AI_STP_H05" }] }; });
  pi.registerTool({ name: "m03_hooks_probe", label: "M03-hooks", description: "Setup hook probe", parameters: { type: "object", properties: {} }, async execute() { return { content: [{ type: "text", text: "AI_STP_H05 AI_STP_H06" }], details: {} }; } });
}
