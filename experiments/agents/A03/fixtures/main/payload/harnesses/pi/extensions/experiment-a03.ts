export default function (pi: any) {
  pi.registerTool({
    name: "experiment_a03", label: "experiment-a03",
    description: "Deterministic delegated agent probe.", parameters: { type: "object", properties: {} },
    async execute() { return { content: [{ type: "text", text: "AI_STP_A03" }], details: {} }; },
  });
}
