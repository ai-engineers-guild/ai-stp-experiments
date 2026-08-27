export default function (pi: any) {
  pi.registerTool({
    name: "ai_stp_p04_plugin", label: "ai-stp-p04-plugin",
    description: "Deterministic plugin probe.", parameters: { type: "object", properties: {} },
    async execute() { return { content: [{ type: "text", text: "AI_STP_P04_PLUGIN" }], details: {} }; },
  });
}
