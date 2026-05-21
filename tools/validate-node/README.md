# @openjewelryschema/validate

AJV-based CLI validator for [Open Jewelry Schema (OJS) v1.0](https://github.com/openjewelryschema/ojs) documents. Validates against the same `spec/v1/ojs-strict.json` schema that the Pydantic reference implementation uses.

## Installation

```bash
npm install -g @openjewelryschema/validate
```

Or use without installing:

```bash
npx @openjewelryschema/validate path/to/product.json
```

## CLI Usage

```bash
# Validate a single file
ojs-validate product.json

# Validate multiple files
ojs-validate examples/ring.json examples/necklace.json

# Validate a directory of files (shell glob expansion)
ojs-validate examples/*.json examples/contrib/*.json

# Options
ojs-validate product.json --quiet          # only print summary
ojs-validate product.json --strict         # fail if any REQUIRED fields missing
ojs-validate product.json --schema ./custom-schema.json  # override schema path
```

### Output

```
✅ engagement-ring.json — REQUIRED 18/18, RECOMMENDED 42/55 (76%), OPTIONAL 23/49
❌ bad-product.json — 2 error(s)
   • /commerce/offers/0/price/amount: must be >= 0
   • /media/images: must NOT have fewer than 1 items

2/3 valid
```

### Exit codes

| Code | Meaning |
|------|---------|
| `0` | All files valid |
| `1` | One or more files invalid |
| `2` | Schema or CLI error (file not found, bad JSON in schema, etc.) |

## Programmatic Usage

```javascript
const { validate } = require('@openjewelryschema/validate');

const product = JSON.parse(fs.readFileSync('product.json', 'utf8'));
const result = validate(product);

if (result.valid) {
  console.log('Valid!', result.score);
  // result.score = { req: { present: 18, total: 18 }, rec: { present: 42, total: 55 }, ... }
} else {
  console.error('Invalid:', result.errors);
}
```

## Schema path resolution

By default the validator looks for the schema at `../../spec/v1/ojs-strict.json` relative to the package (i.e., it expects to be run from within the OJS repository). Override with `--schema`:

```bash
ojs-validate product.json --schema /path/to/ojs-strict.json
```

## See also

- [OJS repository](https://github.com/openjewelryschema/ojs)
- [Python/Pydantic validator](../../src/python/ojs/models/) — source of truth
- [Integration guides](../../docs/integrations/)
