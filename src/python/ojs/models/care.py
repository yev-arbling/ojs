"""OJS v1.0 — Care domain.

Care, cleaning, storage instructions. MEDIUM conversion impact:
AI agents directly answer 'Is this waterproof?', 'Can I shower with it?'
type questions. Absence of structured care data → AI says 'I don't know'
or recommends a competitor.
"""
from __future__ import annotations

from enum import Enum
from typing import Annotated, Optional

from pydantic import Field

from ._common import MultilingualString, OJSBaseModel


class CleaningMethod(str, Enum):
    """Recommended cleaning approach."""

    MILD_SOAP_WATER = "mild_soap_water"
    JEWELRY_CLEANER = "jewelry_cleaner"  # commercial cleaner
    ULTRASONIC_SAFE = "ultrasonic_safe"
    ULTRASONIC_AVOID = "ultrasonic_avoid"  # opal, pearl, emerald, kunzite
    STEAM_SAFE = "steam_safe"
    STEAM_AVOID = "steam_avoid"
    POLISHING_CLOTH_ONLY = "polishing_cloth_only"
    PROFESSIONAL_ONLY = "professional_only"  # delicate antique/heirloom
    AVOID_WATER = "avoid_water"  # pearl strings, vintage pieces with cement


class ActivitySafety(str, Enum):
    """Activities and exposures the piece can/cannot tolerate."""

    SHOWER_SAFE = "shower_safe"
    SWIMMING_SAFE = "swimming_safe"  # pool chlorine considered
    OCEAN_SAFE = "ocean_safe"  # salt water
    EXERCISE_SAFE = "exercise_safe"
    SLEEP_SAFE = "sleep_safe"
    AVOID_PERFUME = "avoid_perfume"
    AVOID_LOTION = "avoid_lotion"
    AVOID_HOUSEHOLD_CHEMICALS = "avoid_household_chemicals"
    AVOID_DIRECT_SUN = "avoid_direct_sun"  # color-sensitive (kunzite, amethyst)


class StorageRecommendation(str, Enum):
    """Recommended storage practice."""

    SOFT_POUCH = "soft_pouch"
    JEWELRY_BOX_DIVIDED = "jewelry_box_divided"  # avoid scratches
    AIRTIGHT_BAG = "airtight_bag"  # silver to slow tarnish
    DRY_ENVIRONMENT = "dry_environment"
    AVOID_HUMIDITY = "avoid_humidity"
    LAY_FLAT = "lay_flat"  # pearl strings to avoid string stretch


class CareModule(OJSBaseModel):
    """Care, cleaning, storage instructions for the piece."""

    cleaning_methods: list[CleaningMethod] = Field(
        default_factory=list, description="Recommended cleaning approaches"
    )
    activity_safety: list[ActivitySafety] = Field(
        default_factory=list, description="Safe and avoid-list activities"
    )
    storage: list[StorageRecommendation] = Field(
        default_factory=list, description="Storage recommendations"
    )
    professional_inspection_recommended_months: Optional[
        Annotated[int, Field(ge=1, le=120)]
    ] = Field(
        default=None,
        description="Months between recommended professional inspections (e.g. 6 for prong settings)",
    )
    care_instructions_text: Optional[Annotated[str, Field(max_length=2000)]] = Field(
        default=None, description="Free-text care instructions (English)"
    )
    care_instructions_localized: Optional[MultilingualString] = Field(
        default=None, description="Care instructions in additional languages"
    )
