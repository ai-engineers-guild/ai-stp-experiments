export default function (pi: any) {
  const marker = "AI_STP_H09_STOP";
  let fired = false;
  pi.on("input", async (event: any) => { if (event.text.includes("AI_STP_H09_TRIGGER")) return { action: "transform", text: `Reply with ${marker}` }; });
  pi.registerTool({
    name: "ai_stp_h09_probe", label: "experiment-h09", description: "Hook registration probe.",
    parameters: { type: "object", properties: {} },
    async execute() { return { content: [{ type: "text", text: fired ? `${marker}:FIRED` : marker }], details: { event: "input" } }; },
  });
}
