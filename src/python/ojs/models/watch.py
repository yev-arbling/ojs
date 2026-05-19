"""OJS v1.0 — Watch domain (sub-vertical discriminator).

Activated when product_type == "watch". Per Google Product Taxonomy,
watches sit under Jewelry > Watches (ID 201), NOT Electronics.

REFERENCES:
  - ISO 22810:2010 — Watches with diver functionality
  - ISO 6425:2018 — Diver's watches
  - ISO 1413:2016 — Shock resistance
  - COSC (Contrôle Officiel Suisse des Chronomètres) — chronometer certification
"""
from __future__ import annotations

from enum import Enum
from typing import Annotated, Optional

from pydantic import Field

from ._common import OJSBaseModel


class MovementType(str, Enum):
    """Watch movement technology."""

    AUTOMATIC = "automatic"  # self-winding mechanical
    MANUAL_WIND = "manual_wind"  # hand-wound mechanical
    QUARTZ = "quartz"  # battery-powered
    SOLAR_QUARTZ = "solar_quartz"  # Seiko/Citizen Eco-Drive
    KINETIC = "kinetic"  # Seiko kinetic
    SPRING_DRIVE = "spring_drive"  # Grand Seiko hybrid
    MECA_QUARTZ = "meca_quartz"  # mechanical chrono module + quartz base
    SMART = "smart"  # for smart watches (use SmartModule too)
    OTHER = "other"


class WatchComplication(str, Enum):
    """Watch complications (multi-valued)."""

    CHRONOGRAPH = "chronograph"
    DATE = "date"
    DAY_DATE = "day_date"
    GMT = "gmt"
    DUAL_TIME = "dual_time"
    MOONPHASE = "moonphase"
    PERPETUAL_CALENDAR = "perpetual_calendar"
    ANNUAL_CALENDAR = "annual_calendar"
    EQUATION_OF_TIME = "equation_of_time"
    TOURBILLON = "tourbillon"
    POWER_RESERVE_INDICATOR = "power_reserve_indicator"
    ALARM = "alarm"
    MINUTE_REPEATER = "minute_repeater"
    WORLD_TIME = "world_time"
    SECOND_TIME_ZONE = "second_time_zone"
    SMALL_SECONDS = "small_seconds"
    BIG_DATE = "big_date"
    REGULATEUR = "regulateur"
    CHIME = "chime"
    OTHER = "other"


class CrystalType(str, Enum):
    """Watch crystal/glass material."""

    SAPPHIRE = "sapphire"  # synthetic sapphire, most scratch-resistant
    MINERAL_GLASS = "mineral_glass"
    ACRYLIC = "acrylic"  # plastic — vintage / Speedmaster Moon
    HARDLEX = "hardlex"  # Seiko proprietary hardened mineral
    OTHER = "other"


class StrapType(str, Enum):
    """Strap/bracelet material."""

    LEATHER = "leather"
    METAL_BRACELET = "metal_bracelet"
    RUBBER = "rubber"
    SILICONE = "silicone"
    NATO = "nato"
    NYLON = "nylon"
    CANVAS = "canvas"
    FABRIC = "fabric"
    CERAMIC = "ceramic"
    OTHER = "other"


class CaseShape(str, Enum):
    """Watch case shape."""

    ROUND = "round"
    SQUARE = "square"
    RECTANGULAR = "rectangular"
    TONNEAU = "tonneau"
    CUSHION = "cushion"
    OVAL = "oval"
    OCTAGONAL = "octagonal"  # Royal Oak / Nautilus
    OTHER = "other"


class WaterResistanceRating(OJSBaseModel):
    """Water resistance per ISO 22810:2010."""

    atm: Optional[Annotated[float, Field(ge=0, le=200)]] = Field(
        default=None, description="Atmospheres (1 ATM = 10m static depth)"
    )
    meters: Optional[Annotated[int, Field(ge=0)]] = Field(
        default=None, description="Equivalent depth in meters"
    )
    iso_22810_compliant: Optional[bool] = None
    iso_6425_divers: Optional[bool] = Field(
        default=None, description="ISO 6425 divers' watch certified (≥100m + safety features)"
    )


class WatchModule(OJSBaseModel):
    """Watch-specific specifications. Required when product_type='watch'."""

    movement_type: MovementType = Field(description="Movement technology")
    caliber: Optional[Annotated[str, Field(max_length=50)]] = Field(
        default=None,
        description="Movement caliber name (e.g. 'ETA 2824-2', 'Rolex 3235', 'Omega 8800')",
    )
    cosc_chronometer: Optional[bool] = Field(
        default=None, description="COSC chronometer certified"
    )
    master_chronometer: Optional[bool] = Field(
        default=None, description="METAS Master Chronometer certified (Omega standard)"
    )
    complications: list[WatchComplication] = Field(
        default_factory=list, description="Watch complications"
    )
    power_reserve_hours: Optional[Annotated[float, Field(gt=0)]] = Field(
        default=None, description="Power reserve in hours"
    )
    frequency_hz: Optional[Annotated[float, Field(gt=0)]] = Field(
        default=None, description="Beat frequency in Hz (e.g. 4 = 28800 vph)"
    )
    jewel_count: Optional[Annotated[int, Field(ge=0, le=100)]] = None

    case_shape: Optional[CaseShape] = None
    case_diameter_mm: Optional[Annotated[float, Field(gt=0)]] = Field(
        default=None, description="Case diameter (mm) — primary size dimension"
    )
    case_thickness_mm: Optional[Annotated[float, Field(gt=0)]] = None
    case_lug_to_lug_mm: Optional[Annotated[float, Field(gt=0)]] = None
    case_lug_width_mm: Optional[Annotated[float, Field(gt=0)]] = None
    case_material: Optional[Annotated[str, Field(max_length=50)]] = Field(
        default=None, description="Case material (stainless steel, gold, titanium, ceramic)"
    )

    crystal_type: Optional[CrystalType] = None
    crystal_coating_ar: Optional[bool] = Field(
        default=None, description="Anti-reflective coating on crystal"
    )

    bezel_type: Optional[Annotated[str, Field(max_length=50)]] = Field(
        default=None,
        description="Bezel type (e.g. 'unidirectional_dive', 'tachymeter', 'gmt_24h')",
    )
    rotating_bezel: Optional[bool] = None

    water_resistance: Optional[WaterResistanceRating] = None
    shock_resistance_iso_1413: Optional[bool] = None
    magnetic_resistance_gauss: Optional[Annotated[int, Field(ge=0)]] = Field(
        default=None, description="Magnetic resistance in Gauss"
    )

    strap_type: Optional[StrapType] = None
    strap_material: Optional[Annotated[str, Field(max_length=50)]] = None
    bracelet_type: Optional[Annotated[str, Field(max_length=50)]] = Field(
        default=None,
        description="Bracelet type (e.g. 'oyster', 'jubilee', 'president', 'milanese')",
    )

    dial_color: Optional[Annotated[str, Field(max_length=50)]] = None
    lume_type: Optional[Annotated[str, Field(max_length=50)]] = Field(
        default=None, description="Luminescence (e.g. 'Super-LumiNova C3', 'Chromalight')"
    )

    box_papers_included: Optional[bool] = Field(
        default=None, description="Original box and papers included (collector signal)"
    )
    serviced_date: Optional[Annotated[str, Field(pattern=r"^\d{4}-\d{2}-\d{2}$")]] = Field(
        default=None, description="Last service date (ISO 8601) for pre-owned watches"
    )
