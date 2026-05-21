#!/usr/bin/env node
'use strict';

const path = require('path');
const fs = require('fs');
const Ajv = require('ajv/dist/2020');
const addFormats = require('ajv-formats');

// ── Tier field definitions ───────────────────────────────────────────────────

function getPath(obj, dotPath) {
  const parts = dotPath.split('.');
  let cur = obj;
  for (const part of parts) {
    if (cur == null) return undefined;
    if (part.endsWith('[0]')) {
      const key = part.slice(0, -3);
      cur = cur[key];
      if (!Array.isArray(cur) || cur.length === 0) return undefined;
      cur = cur[0];
    } else {
      cur = cur[part];
    }
  }
  return cur;
}

function isPresent(val) {
  if (val == null) return false;
  if (Array.isArray(val)) return val.length > 0;
  if (typeof val === 'string') return val.length > 0;
  return true;
}

const REQUIRED_PATHS = [
  'product_type',
  'audit.ojs_version',
  'audit.created_at',
  'audit.source_system',
  'identity.sku',
  'identity.title',
  'identity.description',
  'identity.brand.name',
  'commerce.offers',
  'commerce.offers[0].price.amount',
  'commerce.offers[0].price.currency',
  'commerce.offers[0].availability',
  'commerce.offers[0].url',
  'commerce.offers[0].target_countries',
  'commerce.offers[0].seller_name',
  'commerce.offers[0].seller_url',
  'media.images',
  'media.images[0].url',
];

const RECOMMENDED_PATHS = [
  'identity.gtin',
  'identity.mpn',
  'identity.model',
  'identity.collection',
  'identity.designer',
  'identity.handle',
  'commerce.offers[0].condition',
  'commerce.offers[0].return_policy_url',
  'commerce.offers[0].bnpl_available',
  'commerce.offers[0].free_shipping',
  'commerce.offers[0].lifetime_warranty',
  'commerce.offers[0].accepted_payments',
  'media.images[0].role',
  'media.images[0].alt_text',
  'media.images[0].is_primary',
  'media.images[0].width_px',
  'media.images[0].height_px',
  'media.glb_url',
  'media.spin_360_url',
  'metals',
  'metals.compositions[0].type',
  'metals.compositions[0].color',
  'metals.compositions[0].finish',
  'metals.compositions[0].primary',
  'metals.nickel_free',
  'stones',
  'stones.stones[0].species',
  'stones.stones[0].origin_type',
  'stones.stones[0].carat',
  'stones.stones[0].cut',
  'stones.total_carat_weight',
  'setting',
  'setting.styles[0].style_id',
  'setting.styles[0].setting_type',
  'sizing',
  'sizing.ring_size',
  'sizing.ring_resizable',
  'style',
  'style.era',
  'style.design_styles',
  'style.motifs',
  'style.aesthetic_tags',
  'certification',
  'certification.certificates[0].lab',
  'certification.certificates[0].report_number',
  'ai_commerce',
  'ai_commerce.semantic_description',
  'ai_commerce.query_keywords',
  'ai_commerce.occasion_tags',
  'ai_commerce.audience_tags',
  'ai_commerce.price_tier',
  'care',
  'legal',
];

const CONDITIONAL_BY_TYPE = {
  pearl: ['pearls', 'pearls.pearl_type', 'pearls.nacre_thickness_mm', 'pearls.luster',
    'pearls.surface_quality', 'pearls.matching_grade', 'pearls.overtone', 'pearls.shape',
    'pearls.strand_count', 'pearls.strand_length_mm'],
  watch: ['watch', 'watch.movement_type', 'watch.case_material', 'watch.dial_color',
    'watch.water_resistance_m', 'watch.power_reserve_hours', 'watch.complications',
    'watch.bracelet_material', 'watch.case_diameter_mm', 'watch.crystal_material'],
  smart_wearable: ['smart', 'smart.platform', 'smart.sensors', 'smart.battery_life_hours',
    'smart.charging_type', 'smart.os_compatibility', 'smart.water_resistance_m',
    'smart.nfc', 'smart.gps', 'smart.health_features'],
  body: ['body', 'body.piercing_type', 'body.gauge_mm', 'body.biocompatibility_standard',
    'body.internally_threaded', 'body.implant_grade', 'body.total_length_mm',
    'body.ball_size_mm', 'body.jewelry_style', 'body.placement'],
  estate: ['estate', 'estate.circa_year', 'estate.provenance', 'estate.condition_grade',
    'estate.previous_owners', 'estate.authenticity_verified', 'estate.restoration_history',
    'estate.original_box', 'estate.appraisal_value', 'estate.appraised_by'],
};

const OPTIONAL_PATHS = [
  'identity.title_localized',
  'identity.description_localized',
  'identity.brand.legal_name',
  'identity.brand.website',
  'identity.brand.logo_url',
  'identity.brand.gln',
  'commerce.offers[0].sale_price',
  'commerce.offers[0].inventory_count',
  'commerce.offers[0].handling_time_days',
  'commerce.offers[0].free_engraving',
  'media.videos',
  'media.usdz_url',
  'media.gltf_url',
  'media.ar_metadata',
  'metals.compositions[0].purity_fineness',
  'metals.compositions[0].purity_karat',
  'metals.compositions[0].plating',
  'metals.compositions[0].weight_grams',
  'metals.compositions[0].hallmark',
  'metals.total_metal_weight_grams',
  'metals.conflict_free',
  'metals.recycled_content_percent',
  'stones.stones[0].color_grade',
  'stones.stones[0].clarity_grade',
  'stones.stones[0].cut_grade',
  'stones.stones[0].polish',
  'stones.stones[0].symmetry',
  'stones.stones[0].fluorescence',
  'stones.stones[0].treatments',
  'stones.stones[0].position',
  'stones.stones[0].origin_country',
  'stones.center_stone_index',
  'setting.styles[0].prong_count',
  'setting.styles[0].material',
  'setting.styles[0].head_height_mm',
  'setting.primary_style_id',
  'sizing.ring_width_mm',
  'sizing.length_mm',
  'sizing.chain_width_mm',
  'sizing.drop_length_mm',
  'sizing.closure',
  'sizing.total_weight_grams',
  'certification.certificates[0].report_url',
  'certification.certificates[0].issued_date',
  'certification.certificates[0].refers_to_stone_index',
  'ai_commerce.style_descriptors',
  'ai_commerce.confidence_scores',
  'sustainability',
  'relationships',
  'reviews',
  'artisan',
  'religious',
];

function scoreCompleteness(doc, productType) {
  const check = (paths) => {
    let present = 0;
    for (const p of paths) {
      if (isPresent(getPath(doc, p))) present++;
    }
    return { present, total: paths.length };
  };
  const req = check(REQUIRED_PATHS);
  const rec = check(RECOMMENDED_PATHS);
  const opt = check(OPTIONAL_PATHS);
  const condPaths = CONDITIONAL_BY_TYPE[productType] || [];
  const cond = condPaths.length > 0 ? check(condPaths) : { present: 0, total: 0 };
  return { req, rec, cond, opt };
}

// ── Module-level schema (default) ────────────────────────────────────────────

const DEFAULT_SCHEMA_PATH = path.resolve(__dirname, '../../../spec/v1/ojs-strict.json');

function loadSchema(schemaPath) {
  if (!fs.existsSync(schemaPath)) return null;
  try {
    return JSON.parse(fs.readFileSync(schemaPath, 'utf8'));
  } catch (_) {
    return null;
  }
}

const _defaultSchema = loadSchema(DEFAULT_SCHEMA_PATH);
const _defaultAjv = new Ajv({ allErrors: true, strict: false });
addFormats(_defaultAjv);
const _defaultValidate = _defaultSchema ? _defaultAjv.compile(_defaultSchema) : null;

// ── Programmatic API ─────────────────────────────────────────────────────────

function validateDoc(doc, options) {
  options = options || {};
  let validateFn = _defaultValidate;
  if (options.schema) {
    const customSchema = loadSchema(path.resolve(process.cwd(), options.schema));
    if (!customSchema) throw new Error(`Schema not found: ${options.schema}`);
    const customAjv = new Ajv({ allErrors: true, strict: false });
    addFormats(customAjv);
    validateFn = customAjv.compile(customSchema);
  }
  if (!validateFn) throw new Error(`Default schema not found at ${DEFAULT_SCHEMA_PATH}`);
  const docCopy = Object.assign({}, doc);
  delete docCopy.$schema;
  const valid = validateFn(docCopy);
  const score = scoreCompleteness(docCopy, doc.product_type || 'unknown');
  return {
    valid,
    errors: valid ? [] : (validateFn.errors || []),
    score,
  };
}

module.exports = { validateDoc };

// ── CLI (only runs when invoked directly) ────────────────────────────────────

if (require.main === module) {
  const args = process.argv.slice(2);
  let quiet = false;
  let strict = false;
  let schemaPathOverride = null;
  const files = [];

  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--quiet' || args[i] === '-q') {
      quiet = true;
    } else if (args[i] === '--strict') {
      strict = true;
    } else if (args[i] === '--schema' && args[i + 1]) {
      schemaPathOverride = args[++i];
    } else if (!args[i].startsWith('-')) {
      files.push(args[i]);
    }
  }

  if (files.length === 0) {
    process.stderr.write('Usage: ojs-validate [--quiet] [--strict] [--schema <path>] <file.json> [file2.json ...]\n');
    process.exit(2);
  }

  // Resolve schema for CLI use
  const cliSchemaPath = schemaPathOverride
    ? path.resolve(process.cwd(), schemaPathOverride)
    : DEFAULT_SCHEMA_PATH;

  if (!fs.existsSync(cliSchemaPath)) {
    process.stderr.write(`Schema not found: ${cliSchemaPath}\n`);
    process.stderr.write('Run from repo root, or pass --schema <path>\n');
    process.exit(2);
  }

  let cliSchema, cliAjv, cliValidate;
  try {
    cliSchema = JSON.parse(fs.readFileSync(cliSchemaPath, 'utf8'));
    cliAjv = schemaPathOverride ? new Ajv({ allErrors: true, strict: false }) : _defaultAjv;
    if (schemaPathOverride) addFormats(cliAjv);
    cliValidate = schemaPathOverride ? cliAjv.compile(cliSchema) : _defaultValidate;
  } catch (err) {
    process.stderr.write(`Failed to load schema: ${err.message}\n`);
    process.exit(2);
  }

  let anyInvalid = false;
  const results = [];

  for (const filePath of files) {
    const absPath = path.resolve(process.cwd(), filePath);
    if (!fs.existsSync(absPath)) {
      process.stderr.write(`File not found: ${filePath}\n`);
      anyInvalid = true;
      results.push({ file: filePath, valid: false, errors: ['File not found'] });
      continue;
    }

    let doc;
    try {
      const raw = fs.readFileSync(absPath, 'utf8');
      doc = JSON.parse(raw);
    } catch (err) {
      if (!quiet) process.stdout.write(`FAIL ${path.basename(filePath)} -- JSON parse error: ${err.message}\n`);
      anyInvalid = true;
      results.push({ file: filePath, valid: false, errors: [err.message] });
      continue;
    }

    const docForValidation = Object.assign({}, doc);
    delete docForValidation.$schema;

    const valid = cliValidate(docForValidation);
    const productType = doc.product_type || 'unknown';
    const score = scoreCompleteness(docForValidation, productType);

    if (valid) {
      const recPct = score.rec.total > 0 ? Math.round((score.rec.present / score.rec.total) * 100) : 100;
      const condPart = score.cond.total > 0 ? `, CONDITIONAL ${score.cond.present}/${score.cond.total}` : '';
      const summary = `REQUIRED ${score.req.present}/${score.req.total}, RECOMMENDED ${score.rec.present}/${score.rec.total} (${recPct}%)${condPart}, OPTIONAL ${score.opt.present}/${score.opt.total}`;
      if (!quiet) process.stdout.write(`PASS ${path.basename(filePath)} -- ${summary}\n`);
      results.push({ file: filePath, valid: true, score });

      if (strict && score.req.present < score.req.total) {
        if (!quiet) process.stdout.write(`  WARN strict: missing ${score.req.total - score.req.present} REQUIRED fields\n`);
        anyInvalid = true;
      }
    } else {
      anyInvalid = true;
      if (!quiet) {
        process.stdout.write(`FAIL ${path.basename(filePath)} -- ${cliValidate.errors.length} error(s)\n`);
        for (const err of cliValidate.errors) {
          process.stdout.write(`  * ${err.instancePath || '(root)'}: ${err.message}\n`);
          if (err.params && Object.keys(err.params).length > 0) {
            process.stdout.write(`    params: ${JSON.stringify(err.params)}\n`);
          }
        }
      }
      results.push({ file: filePath, valid: false, errors: cliValidate.errors });
    }
  }

  if (!quiet) {
    const passed = results.filter(r => r.valid).length;
    process.stdout.write(`\n${passed}/${results.length} valid\n`);
  }

  process.exit(anyInvalid ? 1 : 0);
}
