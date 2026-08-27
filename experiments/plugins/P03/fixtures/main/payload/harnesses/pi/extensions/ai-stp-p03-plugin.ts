export default function (pi: any) {
  pi.registerTool({
    name: "ai_stp_p03_plugin", label: "ai-stp-p03-plugin",
    description: "Deterministic plugin probe.", parameters: { type: "object", properties: {} },
    async execute() { return { content: [{ type: "text", text: "AI_STP_P03_PLUGIN" }], details: {} }; },
  });
}
