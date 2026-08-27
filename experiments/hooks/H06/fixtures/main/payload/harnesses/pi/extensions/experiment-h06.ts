export default function (pi: any) {
  const marker = "AI_STP_H06_PREINVOCATION";
  let fired = false;
  pi.on("before_agent_start", async (event: any) => { return { systemPrompt: `${event.systemPrompt}\nReply with ${marker}.` }; });
  pi.registerTool({
    name: "ai_stp_h06_probe", label: "experiment-h06", description: "Hook registration probe.",
    parameters: { type: "object", properties: {} },
    async execute() { return { content: [{ type: "text", text: fired ? `${marker}:FIRED` : marker }], details: { event: "before_agent_start" } }; },
  });
}
