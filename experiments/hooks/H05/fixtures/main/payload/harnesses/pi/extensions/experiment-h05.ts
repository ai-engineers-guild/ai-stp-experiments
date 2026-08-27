export default function (pi: any) {
  const marker = "AI_STP_H05_PREINVOCATION";
  let fired = false;
  pi.on("before_agent_start", async (event: any) => { return { message: { customType: "ai-stp-hook", content: marker, display: true } }; });
  pi.registerTool({
    name: "ai_stp_h05_probe", label: "experiment-h05", description: "Hook registration probe.",
    parameters: { type: "object", properties: {} },
    async execute() { return { content: [{ type: "text", text: fired ? `${marker}:FIRED` : marker }], details: { event: "before_agent_start" } }; },
  });
}
