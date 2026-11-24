// News 23 round 3 entry (Node 22, standard library only): the image is the
// entry.png beside this file, and the program copies it to /output/entry.png.
// The gate takes a whole PNG of at most 1 MiB and 1024 by 1024 pixels, and the
// judge sees exactly the bytes copied. Outside the grader's container,
// MAKEFUN_OUTPUT_DIR stands in for /output:
//   mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts

import { copyFileSync, existsSync, readFileSync } from 'node:fs';
import { join } from 'node:path';

// Exit codes: 1 if entry.png is missing beside main.ts, 1 if the copied
// bytes differ from the source, 0 on a byte-identical copy.
const src = new URL('./entry.png', import.meta.url);
const dst = join(process.env.MAKEFUN_OUTPUT_DIR ?? '/output', 'entry.png');

if (!existsSync(src)) {
  console.error('entry.png not found beside main.ts');
  process.exit(1);
}

copyFileSync(src, dst);

const a = readFileSync(src);
const b = readFileSync(dst);
if (!a.equals(b)) {
  console.error('byte verification failed: copied entry.png differs from the source');
  process.exit(1);
}
console.log(`copied entry.png (${a.length} bytes) to ${dst}`);
