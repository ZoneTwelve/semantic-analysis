#!/usr/bin/env node
/**
 * Stream-group Langfuse-like trace records into one NDJSON record per chat.
 *
 * Usage:
 *   node preprocess-conversations.mjs [input] [output-directory]
 */
import crypto from 'node:crypto';
import fs from 'node:fs';
import fsp from 'node:fs/promises';
import path from 'node:path';
import readline from 'node:readline';

const inputPath = path.resolve(process.argv[2] ?? 'data/raw/traces.jsonl');
const outputDir = path.resolve(process.argv[3] ?? 'data/interim/conversations');
const partitions = 256;
const tempDir = path.join(outputDir, '.partitioned-traces');
const conversationsPath = path.join(outputDir, 'conversations.jsonl');
const unlinkedPath = path.join(outputDir, 'unlinked-traces.jsonl');
const rejectsPath = path.join(outputDir, 'rejected-lines.jsonl');

if (!fs.existsSync(inputPath)) throw new Error(`Input file not found: ${inputPath}`);
if (fs.existsSync(outputDir)) {
  const existing = (await fsp.readdir(outputDir)).filter((name) => name !== '.DS_Store');
  if (existing.length) throw new Error(`Output directory is not empty: ${outputDir}`);
}
await fsp.mkdir(tempDir, { recursive: true });

const writerCache = new Map();
function partitionFor(chatId) {
  const value = crypto.createHash('sha256').update(chatId).digest().readUInt16BE(0);
  return value % partitions;
}
function partitionWriter(index) {
  if (!writerCache.has(index)) {
    writerCache.set(index, fs.createWriteStream(path.join(tempDir, `${index}.jsonl`), { flags: 'a' }));
  }
  return writerCache.get(index);
}
function write(stream, line) {
  if (!stream.write(`${line}\n`)) return new Promise((resolve) => stream.once('drain', resolve));
}

const totals = { sourceLines: 0, validTraceRecords: 0, malformedLines: 0, linkedTraceRecords: 0, unlinkedTraceRecords: 0, conversations: 0 };
const rejectStream = fs.createWriteStream(rejectsPath, { flags: 'w' });
const unlinkedStream = fs.createWriteStream(unlinkedPath, { flags: 'w' });

const source = readline.createInterface({ input: fs.createReadStream(inputPath, { encoding: 'utf8' }), crlfDelay: Infinity });
for await (const line of source) {
  totals.sourceLines++;
  if (!line.trim()) continue;
  let trace;
  try {
    trace = JSON.parse(line);
  } catch (error) {
    totals.malformedLines++;
    await write(rejectStream, JSON.stringify({ lineNumber: totals.sourceLines, error: error.message, sha256: crypto.createHash('sha256').update(line).digest('hex'), byteLength: Buffer.byteLength(line) }));
    continue;
  }
  totals.validTraceRecords++;
  const chatId = typeof trace.metadata?.chatId === 'string' && trace.metadata.chatId ? trace.metadata.chatId : null;
  if (!chatId) {
    totals.unlinkedTraceRecords++;
    await write(unlinkedStream, JSON.stringify(trace));
    continue;
  }
  totals.linkedTraceRecords++;
  await write(partitionWriter(partitionFor(chatId)), JSON.stringify({ chatId, trace }));
}
await Promise.all([...writerCache.values(), rejectStream, unlinkedStream].map((stream) => new Promise((resolve, reject) => stream.end((error) => error ? reject(error) : resolve()))));

const conversationsStream = fs.createWriteStream(conversationsPath, { flags: 'w' });
for (let index = 0; index < partitions; index++) {
  const partitionPath = path.join(tempDir, `${index}.jsonl`);
  if (!fs.existsSync(partitionPath)) continue;
  const grouped = new Map();
  const lines = readline.createInterface({ input: fs.createReadStream(partitionPath, { encoding: 'utf8' }), crlfDelay: Infinity });
  for await (const line of lines) {
    const { chatId, trace } = JSON.parse(line);
    const group = grouped.get(chatId) ?? [];
    group.push(trace);
    grouped.set(chatId, group);
  }
  for (const [chatId, turns] of grouped) {
    turns.sort((a, b) => String(a.timestamp ?? '').localeCompare(String(b.timestamp ?? '')) || String(a.id ?? '').localeCompare(String(b.id ?? '')));
    const timestamps = turns.map((turn) => turn.timestamp).filter(Boolean);
    await write(conversationsStream, JSON.stringify({
      schemaVersion: '1.0',
      chatId,
      firstTimestamp: timestamps[0] ?? null,
      lastTimestamp: timestamps.at(-1) ?? null,
      traceCount: turns.length,
      turns,
    }));
    totals.conversations++;
  }
  await fsp.unlink(partitionPath);
  process.stderr.write(`Processed partition ${index + 1}/${partitions}\r`);
}
await new Promise((resolve, reject) => conversationsStream.end((error) => error ? reject(error) : resolve()));
await fsp.rmdir(tempDir);

const manifest = {
  schemaVersion: '1.0',
  createdAt: new Date().toISOString(),
  input: { path: inputPath, sha256: await digestFile(inputPath) },
  outputs: {
    conversations: path.basename(conversationsPath),
    unlinkedTraces: path.basename(unlinkedPath),
    rejectedLines: path.basename(rejectsPath),
  },
  ...totals,
  grouping: 'metadata.chatId',
  ordering: ['timestamp ascending', 'id ascending as tie-breaker'],
  note: 'Unlinked traces were retained separately; no surrogate chat IDs were created.',
};
await fsp.writeFile(path.join(outputDir, 'manifest.json'), `${JSON.stringify(manifest, null, 2)}\n`);
process.stderr.write('\n');
console.log(JSON.stringify(manifest, null, 2));

function digestFile(filePath) {
  return new Promise((resolve, reject) => {
    const hash = crypto.createHash('sha256');
    fs.createReadStream(filePath).on('error', reject).on('data', (chunk) => hash.update(chunk)).on('end', () => resolve(hash.digest('hex')));
  });
}
