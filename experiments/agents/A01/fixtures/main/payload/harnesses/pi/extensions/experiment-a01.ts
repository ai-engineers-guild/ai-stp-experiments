export default function (pi: any) {
  pi.registerTool({
    name: "experiment_a01",
    label: "experiment-a01",
    description: "Delegated experiment agent. Returns its deterministic reply.",
    parameters: { type: "object", properties: {} },
    async execute() {
      return { content: [{ type: "text", text: "AI_STP_A01" }], details: {} };
    },
  });
}
