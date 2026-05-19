"""OJS v1.0 — Setting domain.

How stones are attached to the metal: prong, bezel, pavé, channel, etc.
Maps to: GMC product_detail under "Setting", Schema.org additionalProperty.

NOT activated when no stones present (pure-metal pieces).
"""
from __future__ import annotations

from enum import Enum
from typing import Annotated, Optional

from pydantic import Field

from ._common import OJSBaseModel


class SettingType(str, Enum):
    """How stone(s) are mounted to the metal."""

    PRONG = "prong"  # 4-prong, 6-prong (Tiffany)
    BEZEL = "bezel"  # encircling metal rim
    HALF_BEZEL = "half_bezel"
    TENSION = "tension"
    CHANNEL = "channel"  # row between two metal walls
    PAVE = "pave"  # tiny stones packed close
    MICRO_PAVE = "micro_pave"
    BAR = "bar"
    FLUSH = "flush"  # stone sunk flat into metal
    GYPSY = "gypsy"  # synonym for flush
    INVISIBLE = "invisible"  # no visible metal between stones
    CLUSTER = "cluster"
    HALO = "halo"  # ring of accent stones around center
    BURNISH = "burnish"
    ILLUSION = "illusion"  # metal extends stone visual size
    SUSPENSION = "suspension"  # drop/pendant style
    OTHER = "other"


class SettingMaterial(str, Enum):
    """Material the setting is made of."""

    SAME_AS_BAND = "same_as_band"
    GOLD = "gold"
    SILVER = "silver"
    PLATINUM = "platinum"
    PALLADIUM = "palladium"
    OTHER = "other"


class SettingStyle(OJSBaseModel):
    """A single setting style applied to one or more stones."""

    style_id: Annotated[str, Field(max_length=50)] = Field(
        description="Local ID used by Stones.setting_style_id to reference this setting"
    )
    setting_type: SettingType = Field(description="Type of setting")
    prong_count: Optional[Annotated[int, Field(ge=1, le=12)]] = Field(
        default=None, description="Number of prongs (only for prong/half-bezel settings)"
    )
    material: Optional[SettingMaterial] = Field(
        default=None, description="Metal used for this setting"
    )
    head_height_mm: Optional[Annotated[float, Field(gt=0)]] = Field(
        default=None, description="Vertical projection of setting above band (mm)"
    )
    gallery_present: Optional[bool] = Field(
        default=None,
        description="Whether decorative gallery (under-setting filigree) is present",
    )
    notes: Optional[Annotated[str, Field(max_length=500)]] = Field(
        default=None, description="Free-text notes (e.g. 'Tiffany-style 6-prong')"
    )


class SettingModule(OJSBaseModel):
    """All settings used in the piece. Most rings have 1; eternity bands many."""

    styles: list[SettingStyle] = Field(min_length=1, description="One per distinct setting")
    primary_style_id: Optional[Annotated[str, Field(max_length=50)]] = Field(
        default=None,
        description="ID of the main/center setting if multiple styles present",
    )
