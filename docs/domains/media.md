# Media

> **Tier**: Tier 1 (REQUIRED) · **Version**: 1.0.0 · **Status**: Stable · **Source**: `src/python/ojs/models/media.py`

## Overview

Visual assets: images, videos, 360° spins, 3D models (glTF, USDZ), AR placement metadata. **STRONG conversion signal**: 5+ images, video, and 3D/AR all carry independent conversion lifts.

GMC enforces image quality: 500×500 px minimum from January 31, 2027. Sub-500 images currently warn; in 2027 they will block listing approval. AR vendor integration (Camweara, mirrAR, Trillion, Kivisense) requires the `ar_metadata` sub-object — without it, vendors can render the 3D model but cannot place it correctly on the user's body.

## When to populate

Always. `media` is a required module with at least one image. Recommended: 5+ images, 1 video, 1 3D model (GLB), AR metadata.

## Fields

| Field | Type | Required | Description |
|---|---|---|---|
| `images` | list[ImageAsset] | ✅ | ≥1 image |
| `videos` | list[VideoAsset] | ⚪ | — |
| `glb_url` | URL | ⚪ | glTF binary (preferred for web AR) |
| `usdz_url` | URL | ⚪ | Apple USDZ (iOS Quick Look) |
| `gltf_url` | URL | ⚪ | glTF JSON variant |
| `spin_360_url` | URL | ⚪ | 360° spin viewer URL |
| `ar_metadata` | ARMetadata | ⚪ | AR placement metadata |

### `ImageAsset` (per-entry fields)

| Field | Type | Required | Description |
|---|---|---|---|
| `url` | URL | ✅ | HTTPS image URL |
| `role` | ImageRole | ⚪ | primary/additional/lifestyle/macro/… |
| `width_px` | int >0 | ⚪ | — |
| `height_px` | int >0 | ⚪ | — |
| `alt_text` | string ≤500 | ⚪ | **Accessibility + SEO + AI signal** |
| `is_primary` | bool | ⚪ (default false) | Exactly one image should be true |
| `color_variant` | string ≤50 | ⚪ | If image is variant-specific |

### `role` (ImageRole enum)

`primary`, `additional`, `lifestyle` (worn/in-context), `macro` (close-up), `scale` (with reference object), `certificate` (photo of cert), `hallmark` (close-up of stamp), `packaging`, `video_thumbnail`, `infographic`, `other`.

For ACP and GMC, the `is_primary` image goes to `image_link`; the rest go to `additional_image_link` (up to 10 in GMC, 9 in ACP).

### `VideoAsset` (per-entry fields)

| Field | Type | Required | Description |
|---|---|---|---|
| `url` | URL | ✅ | YouTube/Vimeo embed or hosted MP4 |
| `thumbnail_url` | URL | ⚪ | — |
| `duration_seconds` | int >0 | ⚪ | — |
| `width_px` / `height_px` | int >0 | ⚪ | — |
| `description` | string ≤500 | ⚪ | — |

GMC introduced `video_link` in April 2026 — a single video can appear in Shopping listings. ACP supports `video_url`.

### `glb_url` / `usdz_url`

| Format | Use | Compatibility |
|---|---|---|
| GLB (glTF binary) | Web AR, Android | Universal — Chrome, Safari (model-viewer), Three.js |
| USDZ | iOS native | Apple Quick Look (iOS Safari, iMessage, Files) |
| glTF JSON | Web AR (split) | Same as GLB but with external textures |

Best practice: provide BOTH `glb_url` and `usdz_url` for full mobile coverage.

### `ARMetadata` (object)

The metadata AR vendors need to place the piece correctly on the user's body:

| Field | Type | Required | Description |
|---|---|---|---|
| `placement_anchor` | PlacementAnchor | ✅ | Body anchor point |
| `anchor_offset_mm` | [x, y, z] floats | ⚪ | Offset from anchor in mm |
| `default_rotation_degrees` | [x, y, z] floats | ⚪ | Euler rotation |
| `scale_reference` | string ≤50 | ⚪ | ring_size_iso / wrist_circumference / absolute_mm |
| `occlusion_priority` | "high" / "medium" / "low" | ⚪ | Z-ordering hint |
| `physics_enabled` | bool | ⚪ | Allow physics simulation |
| `lighting_preset` | "warm" / "cool" / "neutral" / "studio" | ⚪ | — |
| `fallback_2d_url` | URL | ⚪ | Static fallback |

`placement_anchor` enum: `ring_finger`, `any_finger`, `wrist`, `neck`, `ear_lobe`, `ear_helix`, `nose`, `navel`, `chest` (brooches), `head` (tiaras), `other`.

`scale_reference` examples:
- `"ring_size_iso"`: piece scales based on user's ISO ring size
- `"wrist_circumference"`: bracelet scales to wrist
- `"absolute_mm"`: piece always renders at physical size

## Validation rules

- `images` must have at least one entry.
- Exactly one image should have `is_primary=true` (warning if zero or multiple).
- `anchor_offset_mm` and `default_rotation_degrees` must be 3-element arrays if present.
- GMC compatibility: warn if any `width_px < 500` or `height_px < 500` (will block from 2027-01-31).

## Lessons learned & gotchas

- **alt_text is the cheapest AI-ranking win.** Most catalogs leave it blank; populating it improves both SEO and AI agent comprehension. Use product attributes: "Platinum solitaire engagement ring with 1.5ct round brilliant diamond, front view."
- **Don't enumerate `additional_image_link` past 10.** GMC truncates; ACP caps at 9. Pick the 10 strongest non-primary images.
- **Image hosting matters.** GMC and ACP fetch images. Cloudflare CDN, Imgix, Shopify CDN, AWS CloudFront all work. Hot-linking from Pinterest/Instagram does NOT work (rate-limited, often 403).
- **360° spin URLs**: usually a viewer page URL (e.g. `https://orbiter.example.com/spin/sku-001`), not a direct asset URL. Treat as a separate user experience.
- **GLB vs USDZ duplication**: yes, you need both. Apple's USDZ adoption blocked broader GLB support in iOS Safari until very recently. Convert with `usdzconvert` (Apple) or `xcrun usdz_converter`.
- **AR metadata schema is partially aspirational** — no AR vendor today consumes a unified schema. OJS captures it canonically; transformers map to vendor-specific JSON (Camweara, mirrAR formats).
- **Lighting preset** is rendering-engine-specific. "Warm" means warm color temp lighting (~3000K), used for yellow gold to look natural. "Cool" (~6500K) flatters platinum/white gold. Cross-vendor mapping is approximate.
- **`physics_enabled`** for pendants and earrings — they should swing realistically. For rings and brooches, leave false.

## References

- [Schema.org ImageObject / VideoObject](https://schema.org/ImageObject)
- [glTF 2.0 specification (Khronos)](https://www.khronos.org/gltf/)
- [Apple USDZ documentation](https://developer.apple.com/augmented-reality/quick-look/)
- [Google model-viewer](https://modelviewer.dev/)
- [GMC image quality requirements 2027](https://support.google.com/merchants/answer/6324350)
- [Camweara API documentation](https://camweara.com/)
- [mirrAR documentation](https://mirrar.com/)
