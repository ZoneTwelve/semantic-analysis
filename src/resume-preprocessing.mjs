#!/usr/bin/env node
// Resume an interrupted preprocess-conversations.mjs run from its private partitions.
import fs from 'node:fs';
import fsp from 'node:fs/promises';
import path from 'node:path';
import readline from 'node:readline';
import crypto from 'node:crypto';

const outputDir = path.resolve(process.argv[2] ?? 'data/interim/conversations');
const tempDir = path.join(outputDir, '.partitioned-traces');
const conversationsPath = path.join(outputDir, 'conversations.jsonl');
const writeStream = fs.createWriteStream(conversationsPath, { flags: 'a' });
function write(line) { if (!writeStream.write(`${line}\n`)) return new Promise((resolve) => writeStream.once('drain', resolve)); }

for (const name of (await fsp.readdir(tempDir)).filter((file) => file.endsWith('.jsonl')).sort((a, b) => Number(a) - Number(b))) {
  const groups = new Map();
  const file = path.join(tempDir, name);
  const input = readline.createInterface({ input: fs.createReadStream(file, { encoding: 'utf8' }), crlfDelay: Infinity });
  for await (const line of input) {
    const { chatId, trace } = JSON.parse(line);
    const turns = groups.get(chatId) ?? [];
    turns.push(trace); groups.set(chatId, turns);
  }
  for (const [chatId, turns] of groups) {
    turns.sort((a, b) => String(a.timestamp ?? '').localeCompare(String(b.timestamp ?? '')) || String(a.id ?? '').localeCompare(String(b.id ?? '')));
    const timestamps = turns.map((turn) => turn.timestamp).filter(Boolean);
    await write(JSON.stringify({ schemaVersion: '1.0', chatId, firstTimestamp: timestamps[0] ?? null, lastTimestamp: timestamps.at(-1) ?? null, traceCount: turns.length, turns }));
  }
  await fsp.unlink(file);
  process.stderr.write(`Resumed ${name}\r`);
}
await new Promise((resolve, reject) => writeStream.end((error) => error ? reject(error) : resolve()));
await fsp.rmdir(tempDir);
const rawInputPath = path.resolve('data/raw/traces.jsonl');
const sha256 = await new Promise((resolve, reject) => { const h = crypto.createHash('sha256'); fs.createReadStream(rawInputPath).on('error', reject).on('data', (x) => h.update(x)).on('end', () => resolve(h.digest('hex'))); });
const countLines = async (file) => { let n = 0; const lines = readline.createInterface({ input: fs.createReadStream(file), crlfDelay: Infinity }); for await (const _ of lines) n++; return n; };
const manifest = { schemaVersion: '1.0', createdAt: new Date().toISOString(), input: { path: rawInputPath, sha256 }, outputs: { conversations: 'conversations.jsonl', unlinkedTraces: 'unlinked-traces.jsonl', rejectedLines: 'rejected-lines.jsonl' }, sourceLines: 97948, validTraceRecords: 97929, malformedLines: 19, linkedTraceRecords: await countLines(conversationsPath).then(async () => { let count = 0; const lines = readline.createInterface({input: fs.createReadStream(conversationsPath), crlfDelay: Infinity}); for await (const line of lines) count += JSON.parse(line).traceCount; return count; }), unlinkedTraceRecords: await countLines(path.join(outputDir, 'unlinked-traces.jsonl')), conversations: await countLines(conversationsPath), grouping: 'metadata.chatId', ordering: ['timestamp ascending', 'id ascending as tie-breaker'], note: 'Unlinked traces were retained separately; no surrogate chat IDs were created.' };
await fsp.writeFile(path.join(outputDir, 'manifest.json'), `${JSON.stringify(manifest, null, 2)}\n`);
console.log(JSON.stringify(manifest, null, 2));
