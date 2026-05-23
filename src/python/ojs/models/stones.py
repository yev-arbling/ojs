"""OJS v1.0 — Stones domain.

Gemstone specifications: species, 4Cs (diamonds), cut, treatments, origin.
Maps to: Schema.org material + additionalProperty (PropertyValue array),
        GMC product_detail triples under section "Stone",
        ACP material (concatenated) + Custom_variant for stone axes,
        Shopify metafield ojs.stones (json list).

REFERENCES:
  - GIA 4Cs (Cut, Color, Clarity, Carat) — diamond grading standard
  - CIBJO Blue Book (Diamonds, Coloured Stones)
  - ISO 11210:2014 — Jewellery — Determination of platinum
  - FTC Jewelry Guides 16 CFR Part 23 — disclosure of treatments
  - AGS Laboratories CLOSED end-2022, merged into GIA — do not use as new grading lab

REQUIRED if stone-bearing: at least one Stone with species
RECOMMENDED for diamonds: full 4Cs; for colored stones: species + treatment
"""
from __future__ import annotations

from enum import Enum
from typing import Annotated, Optional

from pydantic import Field

from ._common import OJSBaseModel


class GemstoneSpecies(str, Enum):
    """Major gemstone species. Use 'other' + free-text for rare types."""

    # Precious
    DIAMOND = "diamond"
    RUBY = "ruby"
    SAPPHIRE = "sapphire"
    EMERALD = "emerald"

    # Beryl family
    AQUAMARINE = "aquamarine"
    MORGANITE = "morganite"

    # Quartz family
    AMETHYST = "amethyst"
    CITRINE = "citrine"
    SMOKY_QUARTZ = "smoky_quartz"
    ROSE_QUARTZ = "rose_quartz"

    # Other crystalline
    TANZANITE = "tanzanite"
    TOPAZ = "topaz"
    TOURMALINE = "tourmaline"
    GARNET = "garnet"
    PERIDOT = "peridot"
    SPINEL = "spinel"
    ZIRCON = "zircon"
    MOISSANITE = "moissanite"

    # Organics
    PEARL = "pearl"  # also detailed in PearlsModule
    AMBER = "amber"
    CORAL = "coral"
    JET = "jet"

    # Opaque / phenomenal
    OPAL = "opal"
    TURQUOISE = "turquoise"
    LAPIS_LAZULI = "lapis_lazuli"
    MALACHITE = "malachite"
    ONYX = "onyx"
    AGATE = "agate"
    JADE_JADEITE = "jade_jadeite"
    JADE_NEPHRITE = "jade_nephrite"

    # Additional quartz varieties
    PRASIOLITE = "prasiolite"  # green quartz (sometimes called green amethyst)
    QUARTZ = "quartz"  # generic quartz (when specific variety unknown)

    # Synthetic / lab-grown indicator — combine with `origin_type`
    OTHER = "other"


class StoneOrigin(str, Enum):
    """How the stone was created."""

    NATURAL = "natural"
    LAB_GROWN = "lab_grown"  # CVD or HPHT diamonds; flame-fusion sapphires; etc.
    SIMULANT = "simulant"  # e.g. cubic zirconia simulating diamond
    UNKNOWN = "unknown"


class StoneCut(str, Enum):
    """Common faceting shapes. Used for diamond 4Cs and colored stones."""

    ROUND_BRILLIANT = "round_brilliant"
    PRINCESS = "princess"
    CUSHION = "cushion"
    EMERALD_CUT = "emerald_cut"
    OVAL = "oval"
    PEAR = "pear"
    MARQUISE = "marquise"
    RADIANT = "radiant"
    ASSCHER = "asscher"
    HEART = "heart"
    BAGUETTE = "baguette"
    TAPERED_BAGUETTE = "tapered_baguette"
    TRILLION = "trillion"
    ROSE_CUT = "rose_cut"  # vintage style
    OLD_EUROPEAN = "old_european"  # antique cut
    OLD_MINE = "old_mine"  # antique cushion-ish
    CABOCHON = "cabochon"  # unfaceted, polished dome
    BRIOLETTE = "briolette"
    HEXAGON = "hexagon"
    KITE = "kite"
    PORTUGUESE = "portuguese"
    COFFIN = "coffin"
    FANCY = "fancy"
    OTHER = "other"


class GradingLab(str, Enum):
    """Accredited gemological laboratories.

    NOTE: AGS Laboratories closed end-2022 and merged into GIA.
    Do not assign new grading to AGS; legacy reports remain valid.
    """

    GIA = "gia"  # Gemological Institute of America
    AGS = "ags"  # AGS Laboratories — LEGACY ONLY (closed 2022)
    IGI = "igi"  # International Gemological Institute
    HRD = "hrd"  # HRD Antwerp
    GCAL = "gcal"  # Gem Certification & Assurance Lab
    EGL_USA = "egl_usa"  # EGL USA (note: EGL Intl. is separate)
    SSEF = "ssef"  # Swiss Gemmological Institute
    AGTA_GTC = "agta_gtc"
    GRS = "grs"  # GRS Gemresearch Swisslab (colored stones)
    LOTUS = "lotus"  # Lotus Gemology
    GSI = "gsi"  # Gemological Science International
    NGTC = "ngtc"  # National Gemstone Testing Centre (China)
    AGL = "agl"  # American Gemological Laboratories
    GRA = "gra"  # Gem Research Antwerp
    NONE = "none"  # Uncertified


class DiamondColorGrade(str, Enum):
    """GIA D-Z color scale + Fancy Color descriptors."""

    D = "D"
    E = "E"
    F = "F"
    G = "G"
    H = "H"
    I = "I"
    J = "J"
    K = "K"
    L = "L"
    M = "M"
    N = "N"
    O_P = "O-P"
    Q_R = "Q-R"
    S_T = "S-T"
    U_V = "U-V"
    W_X = "W-X"
    Y_Z = "Y-Z"
    FANCY_LIGHT = "fancy_light"
    FANCY = "fancy"
    FANCY_INTENSE = "fancy_intense"
    FANCY_VIVID = "fancy_vivid"
    FANCY_DEEP = "fancy_deep"
    FANCY_DARK = "fancy_dark"


class DiamondClarityGrade(str, Enum):
    """GIA clarity scale."""

    FL = "FL"  # Flawless
    IF = "IF"  # Internally Flawless
    VVS1 = "VVS1"
    VVS2 = "VVS2"
    VS1 = "VS1"
    VS2 = "VS2"
    SI1 = "SI1"
    SI2 = "SI2"
    SI3 = "SI3"  # non-GIA; used by EGL
    I1 = "I1"
    I2 = "I2"
    I3 = "I3"


class ColoredStoneClarityGrade(str, Enum):
    """GIA clarity system for colored stones.

    Distinct from the diamond FL-I3 scale. Used for sapphires, rubies,
    emeralds, and other colored species per GIA colored stone grading.
    """
    EYE_CLEAN = "eye_clean"               # no inclusions visible to unaided eye
    SLIGHTLY_INCLUDED = "slightly_included"
    MODERATELY_INCLUDED = "moderately_included"
    HEAVILY_INCLUDED = "heavily_included"  # affects brilliance/durability


class CutGrade(str, Enum):
    """GIA cut grade for round brilliant diamonds. Also polish/symmetry."""

    EXCELLENT = "excellent"
    VERY_GOOD = "very_good"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"


class FluorescenceIntensity(str, Enum):
    """GIA fluorescence intensity under longwave UV."""

    NONE = "none"
    FAINT = "faint"
    MEDIUM = "medium"
    STRONG = "strong"
    VERY_STRONG = "very_strong"


class TreatmentType(str, Enum):
    """Stone enhancement treatments. FTC requires disclosure (16 CFR §23.22)."""

    NONE = "none"
    HEAT = "heat"  # most rubies, sapphires
    IRRADIATION = "irradiation"
    LASER_DRILLING = "laser_drilling"  # diamonds
    FRACTURE_FILLING = "fracture_filling"  # diamonds, emeralds
    OILING = "oiling"  # emeralds (cedar oil)
    DYE = "dye"  # jade, pearls
    COATING = "coating"
    DIFFUSION = "diffusion"  # sapphires (Be diffusion)
    BLEACHING = "bleaching"  # pearls
    HPHT_TREATMENT = "hpht_treatment"  # post-growth diamond color modification
    OTHER = "other"


class Stone(OJSBaseModel):
    """A single stone in the piece. Multi-stone pieces use one Stone each."""

    species: GemstoneSpecies = Field(description="Stone species")
    species_other: Optional[Annotated[str, Field(max_length=100)]] = Field(
        default=None, description="Free-text species if 'other'"
    )
    origin_type: StoneOrigin = Field(description="Natural / lab-grown / simulant")
    origin_country: Optional[Annotated[str, Field(max_length=100)]] = Field(
        default=None,
        description="Geographic origin (e.g. 'Burma' for ruby, 'Colombia' for emerald)",
    )
    carat: Optional[Annotated[float, Field(gt=0)]] = Field(
        default=None,
        description="Weight in carats (1 ct = 200 mg, UN/CEFACT 'CTM')",
    )
    cut: Optional[StoneCut] = Field(default=None, description="Cut/shape")
    length_mm: Optional[Annotated[float, Field(gt=0)]] = None
    width_mm: Optional[Annotated[float, Field(gt=0)]] = None
    depth_mm: Optional[Annotated[float, Field(gt=0)]] = None
    color_grade: Optional[DiamondColorGrade] = Field(
        default=None, description="GIA D-Z scale (diamonds only)"
    )
    color_description: Optional[Annotated[str, Field(max_length=100)]] = Field(
        default=None,
        description="Free-text color (e.g. 'Pigeon Blood Red', 'Padparadscha')",
    )
    clarity_grade: Optional[DiamondClarityGrade] = Field(
        default=None, description="GIA clarity scale (diamonds only)"
    )
    colored_stone_clarity: Optional[ColoredStoneClarityGrade] = Field(
        default=None,
        description="GIA clarity grade for colored stones. Use instead of clarity_grade "
        "for non-diamond species (sapphire, ruby, emerald, etc.).",
    )
    cut_grade: Optional[CutGrade] = Field(
        default=None, description="GIA cut grade (round brilliants only)"
    )
    polish: Optional[CutGrade] = None
    symmetry: Optional[CutGrade] = None
    fluorescence: Optional[FluorescenceIntensity] = None
    treatments: list[TreatmentType] = Field(
        default_factory=list,
        description="Enhancements applied. Empty list means untreated/none disclosed.",
    )
    position: Optional[Annotated[str, Field(max_length=50)]] = Field(
        default=None,
        description="Position in piece (e.g. 'center', 'halo', 'side_1', 'shank')",
    )
    setting_style_id: Optional[Annotated[str, Field(max_length=50)]] = Field(
        default=None, description="Cross-ref to SettingModule for this stone"
    )


class StonesModule(OJSBaseModel):
    """All stones in the piece. Order matters: index 0 = center/primary stone."""

    stones: list[Stone] = Field(min_length=1, description="One entry per stone")
    total_carat_weight: Optional[Annotated[float, Field(gt=0)]] = Field(
        default=None, description="Sum of carat across all stones (TCW)"
    )
    center_stone_index: Optional[int] = Field(
        default=0,
        ge=0,
        description="Index of the center/primary stone (default 0)",
    )
