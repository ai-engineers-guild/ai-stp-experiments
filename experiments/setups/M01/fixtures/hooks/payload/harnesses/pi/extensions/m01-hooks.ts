export default function (pi: any) {
  pi.on("tool_call", async (event: any) => {
    const command = event.input.command ?? "";
    if (["bash", "powershell"].includes(event.toolName) && /Get-ChildItem/.test(command)) {
      return { block: true, reason: "AI_STP_H01_DENY" };
    }
    if (["bash", "powershell"].includes(event.toolName) && /AI_STP_H02_TRIGGER/.test(command)) {
      event.input.command += event.toolName === "powershell"
        ? "; Write-Output AI_STP_H02_ALLOW"
        : "; printf AI_STP_H02_ALLOW";
    }
  });
}
