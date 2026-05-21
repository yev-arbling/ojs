'use strict';

const path = require('path');
const fs = require('fs');

const REPO_ROOT = path.resolve(__dirname, '../../../');
const { validateDoc: validate } = require('../bin/ojs-validate');

const EXAMPLES_DIR = path.join(REPO_ROOT, 'examples');
const CONTRIB_DIR = path.join(REPO_ROOT, 'examples', 'contrib');

function loadExamples(dir) {
  if (!fs.existsSync(dir)) return [];
  return fs.readdirSync(dir)
    .filter(f => f.endsWith('.json'))
    .map(f => path.join(dir, f));
}

const allFiles = [
  ...loadExamples(EXAMPLES_DIR),
  ...loadExamples(CONTRIB_DIR),
];

if (allFiles.length === 0) {
  console.error('No .json example files found');
  process.exit(1);
}

let passed = 0;
let failed = 0;
const failures = [];

for (const fp of allFiles) {
  const relPath = path.relative(REPO_ROOT, fp);
  let doc;
  try {
    doc = JSON.parse(fs.readFileSync(fp, 'utf8'));
  } catch (err) {
    console.error(`FAIL ${relPath} — JSON parse error: ${err.message}`);
    failed++;
    failures.push({ file: relPath, error: err.message });
    continue;
  }

  const result = validate(doc);
  if (result.valid) {
    const s = result.score;
    const recPct = s.rec.total > 0 ? Math.round((s.rec.present / s.rec.total) * 100) : 100;
    console.log(`PASS ${relPath} — REQUIRED ${s.req.present}/${s.req.total}, RECOMMENDED ${s.rec.present}/${s.rec.total} (${recPct}%)`);
    passed++;
  } else {
    console.error(`FAIL ${relPath} — ${result.errors.length} error(s)`);
    for (const e of result.errors.slice(0, 5)) {
      console.error(`     ${e.instancePath || '(root)'}: ${e.message}`);
    }
    failed++;
    failures.push({ file: relPath, errors: result.errors });
  }
}

console.log(`\n${passed}/${allFiles.length} passed`);

if (failed > 0) {
  console.error(`\n${failed} FAILED:`);
  for (const f of failures) {
    console.error(`  - ${f.file}`);
  }
  process.exit(1);
}
