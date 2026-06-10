import { spawnSync } from "child_process";
import path from "path";

export default function(verb: string, args: string[], log: (s: string) => void) {
  const pythonPath = "python3";
  const scriptPath = path.join(__dirname, "breakpoint.py");

  const r = spawnSync(pythonPath, [scriptPath, verb, ...args], {
    encoding: "utf8",
  });

  if (r.status !== 0) {
    log(`Error: ${r.stderr || r.error?.message}`);
    return false;
  }

  log(r.stdout.trim());
  return true;
}
