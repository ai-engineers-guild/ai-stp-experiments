export default function (pi: any) {
  const marker = "AI_STP_H07_POSTINVOCATION";
  let fired = false;
  pi.on("agent_end", async (event: any) => { fired = true; });
  pi.registerTool({
    name: "ai_stp_h07_probe", label: "experiment-h07", description: "Hook registration probe.",
    parameters: { type: "object", properties: {} },
    async execute() { return { content: [{ type: "text", text: fired ? `${marker}:FIRED` : marker }], details: { event: "agent_end" } }; },
  });
}
