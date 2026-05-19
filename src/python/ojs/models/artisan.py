"""OJS v1.0 — Artisan domain (sub-vertical discriminator).

Activated when handmade / artist-attributed pieces. Edition info,
technique, time-to-create are signals for AI agents matching
'handmade', 'artisan', 'one-of-a-kind' queries.
"""
from __future__ import annotations

from enum import Enum
from typing import Annotated, Optional

from pydantic import Field

from ._common import OJSBaseModel


class ArtisanTechnique(str, Enum):
    """Traditional/artisan jewelry techniques."""

    LOST_WAX_CASTING = "lost_wax_casting"
    HAND_FORGED = "hand_forged"
    HAND_ENGRAVED = "hand_engraved"
    REPOUSSE = "repousse"  # raised relief from back
    CHASING = "chasing"  # detail from front
    GRANULATION = "granulation"  # tiny grains soldered to surface
    FILIGREE = "filigree"
    ENAMEL_CHAMPLEVE = "enamel_champleve"
    ENAMEL_CLOISONNE = "enamel_cloisonne"
    ENAMEL_PLIQUE_A_JOUR = "enamel_plique_a_jour"
    MOKUME_GANE = "mokume_gane"  # Japanese wood-grain metal
    DAMASCUS = "damascus"
    KEUM_BOO = "keum_boo"  # Korean gold-leaf fusion
    NIELLO = "niello"
    SOLDERED_CONSTRUCTION = "soldered_construction"
    FABRICATION = "fabrication"
    CAST_THEN_HAND_FINISHED = "cast_then_hand_finished"
    OTHER = "other"


class EditionType(str, Enum):
    """How the piece is published."""

    ONE_OF_A_KIND = "one_of_a_kind"  # unique
    LIMITED_EDITION = "limited_edition"  # numbered, fixed total
    OPEN_EDITION = "open_edition"  # made-to-order, unlimited
    PRODUCTION = "production"  # standard production line


class ArtisanModule(OJSBaseModel):
    """Artisan-attributed and handmade pieces."""

    techniques: list[ArtisanTechnique] = Field(
        default_factory=list, description="Techniques used"
    )
    edition_type: EditionType = Field(description="Edition classification")
    edition_size: Optional[Annotated[int, Field(ge=1)]] = Field(
        default=None, description="Total edition size if limited"
    )
    edition_number: Optional[Annotated[int, Field(ge=1)]] = Field(
        default=None, description="This piece's number within edition (e.g. 3 of 50)"
    )
    artist_name: Optional[Annotated[str, Field(max_length=200)]] = Field(
        default=None, description="Artist name if different from brand"
    )
    artist_bio_url: Optional[str] = None
    time_to_create_hours: Optional[Annotated[float, Field(gt=0)]] = Field(
        default=None, description="Approximate hours of artisan labor"
    )
    studio_country: Optional[Annotated[str, Field(max_length=100)]] = None
    studio_city: Optional[Annotated[str, Field(max_length=100)]] = None
    signed: Optional[bool] = Field(default=None, description="Artist signature present on piece")
    signature_location: Optional[Annotated[str, Field(max_length=100)]] = None
    certificate_of_authenticity_url: Optional[str] = None
