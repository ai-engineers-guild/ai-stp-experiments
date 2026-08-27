export default function (pi: any) {
  const marker = "AI_STP_H02_PRETOOLUSE";
  let fired = false;
  pi.on("tool_call", async (event: any) => { if (event.toolName === "ls") return; });
  pi.registerTool({
    name: "ai_stp_h02_probe", label: "experiment-h02", description: "Hook registration probe.",
    parameters: { type: "object", properties: {} },
    async execute() { return { content: [{ type: "text", text: fired ? `${marker}:FIRED` : marker }], details: { event: "tool_call" } }; },
  });
}
