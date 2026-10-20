// Exports each beat of the punch cut as its own clip, for cutting into a
// talking-head edit: ProRes 422 MOV on the paper background, no audio, plus
// the soundtrack as a separate WAV. Output: out/cutaways/
// Run: npm run punch:cutaways
import { execFileSync } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import { PUNCH_SCHEDULE } from "../src/punch/timeline";

const root = process.cwd();
const outDir = path.join(root, "out", "cutaways");
const bundleDir = path.join(root, "node_modules", ".cache", "stills-bundle");
fs.mkdirSync(outDir, { recursive: true });

const remotion = (...a: string[]) => execFileSync("npx", ["remotion", ...a], { stdio: ["ignore", "ignore", "inherit"], cwd: root });

console.log("Bundling…");
remotion("bundle", "--out-dir", bundleDir);

const lines: string[] = [];
PUNCH_SCHEDULE.forEach((s, i) => {
  const name = `${String(i + 1).padStart(2, "0")}-${s.id}.mov`;
  const range = `${s.from}-${s.from + s.duration - 1}`;
  console.log(`${name}  frames ${range}`);
  remotion(
    "render", bundleDir, "PalantirPunch-4x5", path.join(outDir, name),
    "--codec=prores", "--prores-profile=standard", `--frames=${range}`, "--muted", "--concurrency=5",
  );
  lines.push(`${name}\t${(s.duration / 30).toFixed(2)} s\tframes ${range} of the punch cut\t${s.label}`);
});
fs.copyFileSync(path.join(root, "public", "punch-audio.wav"), path.join(outDir, "punch-soundtrack.wav"));
lines.push("punch-soundtrack.wav\tfull-length soundtrack (pulse, printer ticks, stamp thuds), -16 LUFS");
fs.writeFileSync(path.join(outDir, "index.txt"), lines.join("\n") + "\n");
console.log(`Wrote ${PUNCH_SCHEDULE.length} clips and the soundtrack to out/cutaways/`);
