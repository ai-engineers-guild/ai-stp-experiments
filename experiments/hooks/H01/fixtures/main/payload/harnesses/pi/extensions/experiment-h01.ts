export default function (pi: any) {
  pi.on("tool_call", async (event: any) => {
    if (["bash", "powershell"].includes(event.toolName) && /Get-ChildItem/.test(event.input.command ?? "")) {
      return { block: true, reason: "AI_STP_H01_DENY" };
    }
  });
}
