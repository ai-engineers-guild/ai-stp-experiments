export default function (pi: any) {
  const marker = "AI_STP_H03_POSTTOOLUSE";
  let fired = false;
  pi.on("tool_result", async (event: any) => { if (["bash", "powershell"].includes(event.toolName)) return { content: [...event.content, { type: "text", text: marker }] }; });
  pi.registerTool({
    name: "ai_stp_h03_probe", label: "experiment-h03", description: "Hook registration probe.",
    parameters: { type: "object", properties: {} },
    async execute() { return { content: [{ type: "text", text: fired ? `${marker}:FIRED` : marker }], details: { event: "tool_result" } }; },
  });
}
