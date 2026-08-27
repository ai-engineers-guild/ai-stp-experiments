export default function (pi: any) {
  pi.registerTool({ name: "m01_agent_a", label: "m01_agent_a", description: "M01 agent A", parameters: { type: "object", properties: {} }, async execute() { return { content: [{ type: "text", text: "AI_STP_M01_AGENT_A" }] }; } });
}
