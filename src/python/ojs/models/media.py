"""OJS v1.0 — Media domain.

Visual assets: images, 360° spins, 3D models, AR metadata.
Maps to: Schema.org image / video / 3DModel,
        GMC image_link / additional_image_link / video_link (April 2026),
        ACP image_url / additional_image_urls / video_url / model_3d_url,
        Shopify media (images, videos, 3D models).

STRONG conversion signal: 5+ images, video, 3D/AR. Strict GMC rules:
500x500 px minimum from January 31, 2027.
"""
from __future__ import annotations

from enum import Enum
from typing import Annotated, Optional

from pydantic import Field

from ._common import OJSBaseModel


class ImageRole(str, Enum):
    """Role/category of image."""

    PRIMARY = "primary"  # main product image
    ADDITIONAL = "additional"
    LIFESTYLE = "lifestyle"  # worn/in-context
    MACRO = "macro"  # close-up
    SCALE = "scale"  # with reference object
    CERTIFICATE = "certificate"  # photo of cert document
    HALLMARK = "hallmark"  # close-up of stamp
    PACKAGING = "packaging"
    VIDEO_THUMBNAIL = "video_thumbnail"
    INFOGRAPHIC = "infographic"
    OTHER = "other"


class ImageAsset(OJSBaseModel):
    """A single image."""

    url: str = Field(description="HTTPS URL to image")
    role: ImageRole = Field(default=ImageRole.ADDITIONAL, description="Image role")
    width_px: Optional[Annotated[int, Field(gt=0)]] = None
    height_px: Optional[Annotated[int, Field(gt=0)]] = None
    alt_text: Optional[Annotated[str, Field(max_length=500)]] = Field(
        default=None, description="Accessibility alt text (also helps SEO/AI)"
    )
    is_primary: bool = Field(default=False, description="Exactly one image should have this true")
    color_variant: Optional[Annotated[str, Field(max_length=50)]] = Field(
        default=None,
        description="Variant axis value (e.g. 'rose_gold') if image is variant-specific",
    )


class VideoAsset(OJSBaseModel):
    """A single video."""

    url: str = Field(description="HTTPS URL (YouTube/Vimeo embed or hosted MP4)")
    thumbnail_url: Optional[str] = None
    duration_seconds: Optional[Annotated[int, Field(gt=0)]] = None
    width_px: Optional[Annotated[int, Field(gt=0)]] = None
    height_px: Optional[Annotated[int, Field(gt=0)]] = None
    description: Optional[Annotated[str, Field(max_length=500)]] = None


class PlacementAnchor(str, Enum):
    """Where AR-rendered piece attaches on the body."""

    RING_FINGER = "ring_finger"
    ANY_FINGER = "any_finger"
    WRIST = "wrist"
    NECK = "neck"
    EAR_LOBE = "ear_lobe"
    EAR_HELIX = "ear_helix"
    NOSE = "nose"
    NAVEL = "navel"
    CHEST = "chest"  # for brooches
    HEAD = "head"  # for tiaras
    OTHER = "other"


class ARMetadata(OJSBaseModel):
    """AR placement and rendering metadata.

    Consumed by Camweara, mirrAR, Trillion, Kivisense, Apple Quick Look.
    Without this metadata, AR vendors can render the 3D model but cannot
    place it correctly on the user's body.
    """

    placement_anchor: PlacementAnchor = Field(description="Body anchor point")
    anchor_offset_mm: Optional[list[float]] = Field(
        default=None,
        min_length=3,
        max_length=3,
        description="[x, y, z] offset from anchor in mm",
    )
    default_rotation_degrees: Optional[list[float]] = Field(
        default=None,
        min_length=3,
        max_length=3,
        description="[x, y, z] Euler rotation in degrees",
    )
    scale_reference: Optional[Annotated[str, Field(max_length=50)]] = Field(
        default=None,
        description="Scaling reference (e.g. 'ring_size_iso', 'wrist_circumference', 'absolute_mm')",
    )
    occlusion_priority: Optional[Annotated[str, Field(max_length=20)]] = Field(
        default=None,
        description="'high' (occludes hand), 'medium', 'low' (always on top)",
    )
    physics_enabled: Optional[bool] = Field(
        default=None,
        description="Allow physics simulation (e.g. swinging earrings, pendant sway)",
    )
    lighting_preset: Optional[Annotated[str, Field(max_length=20)]] = Field(
        default=None,
        description="Preferred lighting ('warm', 'cool', 'neutral', 'studio')",
    )
    fallback_2d_url: Optional[str] = Field(
        default=None,
        description="Static 2D fallback when AR unavailable",
    )


class MediaModule(OJSBaseModel):
    """All visual media assets."""

    images: list[ImageAsset] = Field(
        min_length=1, description="At least one image required for syndication"
    )
    videos: list[VideoAsset] = Field(default_factory=list)
    glb_url: Optional[str] = Field(
        default=None, description="glTF binary (preferred for web AR)"
    )
    usdz_url: Optional[str] = Field(
        default=None, description="Apple USDZ (preferred for iOS Quick Look)"
    )
    gltf_url: Optional[str] = Field(default=None, description="glTF JSON variant")
    spin_360_url: Optional[str] = Field(
        default=None, description="360° spin viewer URL"
    )
    ar_metadata: Optional[ARMetadata] = Field(
        default=None, description="AR placement metadata for vendor integration"
    )
