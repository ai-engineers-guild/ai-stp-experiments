export default function (pi: any) {
  pi.registerTool({
    name: "ai_stp_p01_plugin",
    label: "ai-stp-p01-plugin",
    description: "Deterministic plugin probe.",
    parameters: { type: "object", properties: {} },
    async execute() {
      return { content: [{ type: "text", text: "AI_STP_P01_PLUGIN" }], details: {} };
    },
  });
}
