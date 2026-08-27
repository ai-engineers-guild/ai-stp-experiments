export default function (pi: any) {
  const marker = "AI_STP_H08_POSTINVOCATION";
  let fired = false;
  pi.on("agent_settled", async (event: any) => { fired = true; });
  pi.registerTool({
    name: "ai_stp_h08_probe", label: "experiment-h08", description: "Hook registration probe.",
    parameters: { type: "object", properties: {} },
    async execute() { return { content: [{ type: "text", text: fired ? `${marker}:FIRED` : marker }], details: { event: "agent_settled" } }; },
  });
}
