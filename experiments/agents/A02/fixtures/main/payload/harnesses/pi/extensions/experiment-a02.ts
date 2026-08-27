export default function (pi: any) {
  pi.registerTool({
    name: "experiment_a02", label: "experiment-a02",
    description: "Deterministic delegated agent probe.", parameters: { type: "object", properties: {} },
    async execute() { return { content: [{ type: "text", text: "AI_STP_A02" }], details: {} }; },
  });
}
