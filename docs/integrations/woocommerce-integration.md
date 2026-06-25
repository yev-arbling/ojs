# WooCommerce Integration Guide

> **Audience:** Retailers and WooCommerce developers adding OJS structured data to product pages. If you build a pipeline in Python or need deep validation, see [docs/domains/](../domains/README.md) instead.

This guide shows how to add Open Jewelry Schema v1.0 data to a WooCommerce store using product meta and PHP JSON-LD output. OJS data on product pages is readable by AI shopping agents (ChatGPT, Perplexity, Google AI Mode, Copilot), Google Rich Results, and any tool that understands JSON-LD.

> **WooCommerce vs. Shopify:** There is no native WooCommerce transformer in the OJS Python library (only Shopify has a round-trip transformer via `to_shopify_metafields()`). For WooCommerce, the recommended approach is to output JSON-LD directly via `to_schema_org()` from your pipeline, or use the PHP snippet below. For pipeline use see the `to_schema_org()` function in `src/python/ojs/transformers/schema_org.py`.

## Overview

OJS v1.0 data is stored as WooCommerce **product meta** with the `_ojs_` prefix. A PHP hook outputs a `<script type="application/ld+json">` tag on product pages using the v1.0 modular structure.

> **v1.0 field path changes from v0.1:**
> - `metal.type` → `metals.compositions[0].type`
> - `metal.purity` → `metals.compositions[0].purity_karat` (numeric) or `purity_fineness` (integer)
> - `stones[0].cut` → `stones.stones[0].cut`
> - `setting.type` → `setting.styles[0].setting_type`
> - `sizing.ring_size_us` → `sizing.ring_size.us_ca`
> - `offers[].price` + `priceCurrency` → `commerce.offers[0].price.amount` + `.currency`
> - `offers[].availability` (schema.org URL) → plain enum string (`in_stock`, `out_of_stock`, etc.)

## Step 1: Add custom fields via functions.php

Add this to your theme's `functions.php` or a site-specific plugin:

```php
/**
 * Add OJS v1.0 metabox to WooCommerce product edit screen.
 */
add_action('add_meta_boxes', function() {
    add_meta_box(
        'ojs_product_data',
        'Open Jewelry Schema v1.0 (OJS)',
        'ojs_render_metabox',
        'product',
        'normal',
        'default'
    );
});

function ojs_render_metabox($post) {
    $fields = [
        '_ojs_product_type'        => 'Product type (ring, earring, necklace, bracelet, pendant, watch...)',
        '_ojs_metal_type'          => 'Metal type (gold, silver, platinum...)',
        '_ojs_metal_purity_karat'  => 'Metal purity karat (10, 14, 18, 22, 24)',
        '_ojs_metal_color'         => 'Metal color (yellow, white, rose, natural...)',
        '_ojs_stone_species'       => 'Stone species (diamond, sapphire, emerald, ruby, onyx...)',
        '_ojs_stone_origin'        => 'Stone origin (natural, lab_grown, simulant)',
        '_ojs_stone_cut'           => 'Stone cut (round_brilliant, oval, cushion, pear, marquise...)',
        '_ojs_stone_carat'         => 'Stone carat weight (e.g. 1.02)',
        '_ojs_stone_clarity_grade' => 'Clarity grade (FL, IF, VVS1, VVS2, VS1, VS2, SI1, SI2, I1...)',
        '_ojs_stone_color_grade'   => 'Color grade (D, E, F, G, H, I, J...)',
        '_ojs_setting_type'        => 'Setting type (prong, bezel, pave, channel, halo...)',
        '_ojs_style_era'           => 'Style era (contemporary, art_deco, edwardian, art_nouveau...)',
        '_ojs_ring_size_us'        => 'Ring size US (e.g. 7.0)',
        '_ojs_ring_resizable'      => 'Ring resizable (1 = yes, 0 = no)',
    ];

    wp_nonce_field('ojs_save_meta', 'ojs_nonce');

    echo '<table class="form-table">';
    foreach ($fields as $key => $label) {
        $value = get_post_meta($post->ID, $key, true);
        echo "<tr><th><label for='{$key}'>{$label}</label></th>";
        echo "<td><input type='text' id='{$key}' name='{$key}' value='" . esc_attr($value) . "' class='regular-text' /></td></tr>";
    }
    echo '</table>';
}

add_action('save_post_product', function($post_id) {
    if (!isset($_POST['ojs_nonce']) || !wp_verify_nonce($_POST['ojs_nonce'], 'ojs_save_meta')) return;
    $keys = [
        '_ojs_product_type', '_ojs_metal_type', '_ojs_metal_purity_karat',
        '_ojs_metal_color', '_ojs_stone_species', '_ojs_stone_origin',
        '_ojs_stone_cut', '_ojs_stone_carat', '_ojs_stone_clarity_grade',
        '_ojs_stone_color_grade', '_ojs_setting_type', '_ojs_style_era',
        '_ojs_ring_size_us', '_ojs_ring_resizable',
    ];
    foreach ($keys as $key) {
        if (isset($_POST[$key])) {
            update_post_meta($post_id, $key, sanitize_text_field($_POST[$key]));
        }
    }
});
```

## Step 2: Output JSON-LD v1.0 on product pages

Add this to your theme's `functions.php`:

```php
add_action('woocommerce_after_single_product', 'ojs_output_jsonld_v1');

function ojs_output_jsonld_v1() {
    global $product;
    if (!$product) return;

    $id = $product->get_id();
    $product_type = get_post_meta($id, '_ojs_product_type', true);
    if (!$product_type) return; // only output if OJS data present

    $price = $product->get_price();
    $currency = get_woocommerce_currency();
    $product_url = get_permalink($id);
    $shop_name = get_bloginfo('name');
    $shop_url = home_url();
    $featured_image_url = wp_get_attachment_url($product->get_image_id());

    // Build images array
    $images = [];
    if ($featured_image_url) {
        $images[] = ['url' => $featured_image_url, 'role' => 'primary', 'is_primary' => true];
    }
    foreach ($product->get_gallery_image_ids() as $img_id) {
        $url = wp_get_attachment_url($img_id);
        if ($url) $images[] = ['url' => $url, 'role' => 'additional', 'is_primary' => false];
    }
    if (empty($images)) return;

    $data = [
        '@context'     => 'https://openjewelryschema.org/v1/context.jsonld',
        '@type'        => 'Product',
        'product_type' => $product_type,
        'audit'        => [
            'ojs_version'   => '1.0.1',
            'created_at'    => gmdate('Y-m-d\TH:i:s\Z'),
            'source_system' => 'other',
        ],
        'identity' => [
            'sku'         => $product->get_sku() ?: 'WC-' . $id,
            'title'       => $product->get_name(),
            'description' => wp_strip_all_tags($product->get_description()) ?: wp_strip_all_tags($product->get_short_description()),
            'brand'       => ['name' => $shop_name],
        ],
        'commerce' => [
            'offers' => [[
                'price'           => ['amount' => number_format((float)$price, 2, '.', ''), 'currency' => $currency],
                'availability'    => $product->is_in_stock() ? 'in_stock' : 'out_of_stock',
                'url'             => $product_url,
                'condition'       => 'new',
                'target_countries' => ['US'],
                'seller_name'     => $shop_name,
                'seller_url'      => $shop_url,
            ]],
            'primary_offer_index' => 0,
        ],
        'media' => ['images' => $images],
    ];

    // metals
    $metal_type = get_post_meta($id, '_ojs_metal_type', true);
    if ($metal_type) {
        $comp = ['type' => $metal_type, 'primary' => true];
        $purity = get_post_meta($id, '_ojs_metal_purity_karat', true);
        if ($purity) $comp['purity_karat'] = (float) $purity;
        $color = get_post_meta($id, '_ojs_metal_color', true);
        if ($color) $comp['color'] = $color;
        $data['metals'] = ['compositions' => [$comp]];
    }

    // stones
    $stone_species = get_post_meta($id, '_ojs_stone_species', true);
    if ($stone_species) {
        $stone = [
            'species'     => $stone_species,
            'origin_type' => get_post_meta($id, '_ojs_stone_origin', true) ?: 'natural',
        ];
        $cut = get_post_meta($id, '_ojs_stone_cut', true);
        if ($cut) $stone['cut'] = $cut;
        $carat = get_post_meta($id, '_ojs_stone_carat', true);
        if ($carat) $stone['carat'] = (float) $carat;
        $clarity = get_post_meta($id, '_ojs_stone_clarity_grade', true);
        if ($clarity) $stone['clarity_grade'] = $clarity;
        $color_grade = get_post_meta($id, '_ojs_stone_color_grade', true);
        if ($color_grade) $stone['color_description'] = $color_grade;
        $data['stones'] = ['stones' => [$stone], 'center_stone_index' => 0];
    }

    // setting
    $setting_type = get_post_meta($id, '_ojs_setting_type', true);
    if ($setting_type) {
        $data['setting'] = ['styles' => [['style_id' => 'main', 'setting_type' => $setting_type]]];
    }

    // sizing
    $ring_size = get_post_meta($id, '_ojs_ring_size_us', true);
    if ($ring_size) {
        $sizing = ['ring_size' => ['us_ca' => (float) $ring_size]];
        $resizable = get_post_meta($id, '_ojs_ring_resizable', true);
        if ($resizable !== '') $sizing['ring_resizable'] = (bool)(int)$resizable;
        $data['sizing'] = $sizing;
    }

    // style
    $style_era = get_post_meta($id, '_ojs_style_era', true);
    if ($style_era) {
        $data['style'] = [
            'era'           => $style_era,
            'design_styles' => [],
            'motifs'        => [],
            'aesthetic_tags' => [],
        ];
    }

    echo '<script type="application/ld+json">'
        . wp_json_encode($data, JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT)
        . '</script>' . "\n";
}
```

### Programmatic via Python (pipeline approach)

If you pre-generate OJS records in Python and push them to WooCommerce via REST API, use `to_schema_org()` to get a JSON-LD dict, then embed it as a product meta field:

```python
from ojs.models import JewelryProduct
from ojs.transformers.schema_org import to_schema_org

product = JewelryProduct.model_validate(data)
jsonld = to_schema_org(product)  # returns a dict with @context, @type, etc.

# Store as WooCommerce product meta via REST API:
import requests
requests.put(
    f"{woo_base}/wp-json/wc/v3/products/{product_id}",
    auth=(consumer_key, consumer_secret),
    json={"meta_data": [{"key": "_ojs_jsonld_v1", "value": json.dumps(jsonld)}]}
)
```

Then in PHP, decode and output the stored JSON-LD directly, bypassing the manual field mapping above.

## Step 3: Batch update via WooCommerce REST API

To populate OJS fields for existing products programmatically:

**Single product update:**
```bash
curl -X PUT \
  "https://YOUR-STORE.com/wp-json/wc/v3/products/PRODUCT_ID" \
  -u "${WC_CONSUMER_KEY}:${WC_CONSUMER_SECRET}" \
  -H "Content-Type: application/json" \
  -d '{
    "meta_data": [
      { "key": "_ojs_product_type", "value": "ring" },
      { "key": "_ojs_metal_type", "value": "gold" },
      { "key": "_ojs_metal_purity_karat", "value": "14" },
      { "key": "_ojs_stone_species", "value": "diamond" },
      { "key": "_ojs_stone_origin", "value": "natural" }
    ]
  }'
```

**Batch update (up to 100 products):**
```bash
curl -X POST \
  "https://YOUR-STORE.com/wp-json/wc/v3/products/batch" \
  -u "${WC_CONSUMER_KEY}:${WC_CONSUMER_SECRET}" \
  -H "Content-Type: application/json" \
  -d '{
    "update": [
      {
        "id": 123,
        "meta_data": [
          { "key": "_ojs_product_type", "value": "ring" },
          { "key": "_ojs_metal_type", "value": "gold" }
        ]
      },
      {
        "id": 456,
        "meta_data": [
          { "key": "_ojs_product_type", "value": "necklace" },
          { "key": "_ojs_metal_type", "value": "silver" }
        ]
      }
    ]
  }'
```

## Step 4: Validate

After adding the output hook, view source on any product page and find the JSON-LD `<script>` tag. Copy the JSON object and validate:

```bash
npm install -g @openjewelryschema/validate
# Save JSON object to a file, then:
ojs-validate product.json
```

The validator checks against `spec/v1/ojs-strict.json` — the same schema used by the Python reference implementation — and outputs a completeness score per tier (REQUIRED/RECOMMENDED/OPTIONAL).

## See also

- [Shopify integration guide](shopify-integration.md) — if you're on Shopify (has a native Python round-trip transformer)
- [to_schema_org() source](../../src/python/ojs/transformers/schema_org.py) — Python transformer to JSON-LD
- [Domain reference docs](../domains/README.md) — per-field documentation
- [Node.js CLI validator](../../tools/validate-node/)
