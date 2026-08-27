export default function (pi: any) {
  pi.registerTool({
    name: "ai_stp_p02_plugin", label: "ai-stp-p02-plugin",
    description: "Deterministic plugin probe.", parameters: { type: "object", properties: {} },
    async execute() { return { content: [{ type: "text", text: "AI_STP_P02_PLUGIN" }], details: {} }; },
  });
}
