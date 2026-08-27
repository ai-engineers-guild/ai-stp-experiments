export default function (pi: any) {
  pi.registerTool({
    name: "experiment_a04", label: "experiment-a04",
    description: "Deterministic delegated agent probe.", parameters: { type: "object", properties: {} },
    async execute() { return { content: [{ type: "text", text: "AI_STP_A04" }], details: {} }; },
  });
}
