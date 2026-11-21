// The Poster for a Place That Isn't There — entrypoint (Node 22, stdlib only).
//
// The poster itself is entry.png, rendered by tools/render.py from a real
// Pexels file photo of a lone peak above a sea of clouds, typeset for the
// invented place Veldoria. This program's job is to prove that file is a
// whole PNG inside the competition's limits and to place it where the
// grader looks: /output/entry.png. It touches no network, reads no clock
// and writes nothing else, so repeated runs produce identical bytes.
//
// Local run (MAKEFUN_OUTPUT_DIR stands in for /output outside the grader):
//   mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts

import { existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const MAX_BYTES = 1_048_576;
const MAX_SIDE = 1024;
const EXPECTED_WIDTH = 768;
const EXPECTED_HEIGHT = 1024;

const PNG_MAGIC: readonly number[] = [0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a];
const PNG_TAIL: readonly number[] = [
  0x00, 0x00, 0x00, 0x00, 0x49, 0x45, 0x4e, 0x44, 0xae, 0x42, 0x60, 0x82,
];

function fail(reason: string): never {
  throw new Error(`entry.png rejected: ${reason}`);
}

function bytesEqual(a: Buffer, b: readonly number[]): boolean {
  return a.length === b.length && b.every((v, i) => a[i] === v);
}

/** Confirm the bytes are one whole PNG of the poster's size, in limits. */
function inspectPoster(png: Buffer): { width: number; height: number } {
  if (png.length > MAX_BYTES) {
    fail(`is ${png.length} bytes, over the ${MAX_BYTES} byte cap`);
  }
  if (png.length < 33 || !bytesEqual(png.subarray(0, 8), PNG_MAGIC)) {
    fail("does not start with the PNG signature");
  }
  const width = png.readUInt32BE(16);
  const height = png.readUInt32BE(20);
  if (width > MAX_SIDE || height > MAX_SIDE) {
    fail(`is ${width}x${height}, over the ${MAX_SIDE}x${MAX_SIDE} cap`);
  }
  if (width !== EXPECTED_WIDTH || height !== EXPECTED_HEIGHT) {
    fail(`is ${width}x${height}, expected ${EXPECTED_WIDTH}x${EXPECTED_HEIGHT}`);
  }
  if (!bytesEqual(png.subarray(png.length - 12), PNG_TAIL)) {
    fail("does not end with the IEND chunk: not a whole PNG");
  }
  return { width, height };
}

function main(): void {
  const root = dirname(fileURLToPath(import.meta.url));
  const posterPath = join(root, "entry.png");
  if (!existsSync(posterPath)) {
    fail("entry.png is missing from the repository");
  }
  const png = readFileSync(posterPath);
  const { width, height } = inspectPoster(png);

  const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";
  mkdirSync(outDir, { recursive: true });
  writeFileSync(join(outDir, "entry.png"), png);
  console.log(`wrote ${width}x${height} entry.png (${png.length} bytes) to ${outDir}`);
}

main();
