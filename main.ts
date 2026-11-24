import * as fs from "node:fs";
import * as path from "node:path";

const outDir = process.env.MAKEFUN_OUTPUT_DIR || "/output";
const src = path.join(process.cwd(), "entry.png");
const dest = path.join(outDir, "entry.png");

if (!fs.existsSync(src)) {
  console.error("entry.png missing in repo root");
  process.exit(1);
}
fs.mkdirSync(outDir, { recursive: true });
fs.copyFileSync(src, dest);

const a = fs.readFileSync(src);
const b = fs.readFileSync(dest);
if (!a.equals(b)) {
  console.error("copy mismatch: entry.png differs after copy");
  process.exit(1);
}
console.log("entry.png copied to " + dest + " (" + a.length + " bytes, identical)");
