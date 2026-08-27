export default function (pi: any) {
  pi.registerTool({
    name: "experiment_a05", label: "experiment-a05",
    description: "Deterministic delegated agent probe.", parameters: { type: "object", properties: {} },
    async execute() { return { content: [{ type: "text", text: "AI_STP_A05" }], details: {} }; },
  });
}
