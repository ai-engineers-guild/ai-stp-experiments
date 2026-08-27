export default function (pi: any) {
  pi.on("tool_result", async (event: any) => { if (["bash", "powershell", "ls"].includes(event.toolName)) return { content: [...event.content, { type: "text", text: "AI_STP_H09" }] }; });
  pi.registerTool({ name: "m05_hooks_probe", label: "M05-hooks", description: "Setup hook probe", parameters: { type: "object", properties: {} }, async execute() { return { content: [{ type: "text", text: "AI_STP_H09 AI_STP_H10" }], details: {} }; } });
}
