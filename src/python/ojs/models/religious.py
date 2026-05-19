"""OJS v1.0 — Religious / ceremonial jewelry domain (sub-vertical).

Activated when piece has religious / spiritual / ceremonial significance.
Important for AI agents matching faith-specific queries
('cross necklace', 'evil eye', 'Star of David', 'hamsa').
"""
from __future__ import annotations

from enum import Enum
from typing import Annotated, Optional

from pydantic import Field

from ._common import MultilingualString, OJSBaseModel


class Religion(str, Enum):
    """Faith tradition."""

    CHRISTIAN = "christian"
    CATHOLIC = "catholic"
    ORTHODOX = "orthodox"
    PROTESTANT = "protestant"
    JEWISH = "jewish"
    MUSLIM = "muslim"
    HINDU = "hindu"
    BUDDHIST = "buddhist"
    SIKH = "sikh"
    PAGAN = "pagan"
    SHINTO = "shinto"
    INTERFAITH = "interfaith"
    SPIRITUAL_NON_RELIGIOUS = "spiritual_non_religious"  # crystals, energy, etc.
    OTHER = "other"


class CeremonyType(str, Enum):
    """Ceremony / ritual occasion."""

    WEDDING = "wedding"
    BAPTISM = "baptism"
    CONFIRMATION = "confirmation"
    BAR_BAT_MITZVAH = "bar_bat_mitzvah"
    FIRST_COMMUNION = "first_communion"
    HAJJ = "hajj"
    UMRAH = "umrah"
    DIWALI = "diwali"
    SHADI = "shadi"
    QUINCEANERA = "quinceanera"
    CORONATION = "coronation"
    OTHER = "other"


class ReligiousModule(OJSBaseModel):
    """Religious / ceremonial significance."""

    religion: Religion = Field(description="Faith tradition")
    religion_other: Optional[Annotated[str, Field(max_length=100)]] = None
    symbol_meaning: Optional[MultilingualString] = Field(
        default=None,
        description="Symbol meaning and significance (multilingual)",
    )
    symbol_name: Optional[Annotated[str, Field(max_length=100)]] = Field(
        default=None,
        description="Name of the symbol (e.g. 'Hamsa', 'Khamsa', 'Star of David', 'Crucifix')",
    )
    ceremony_types: list[CeremonyType] = Field(
        default_factory=list,
        description="Ceremonies/occasions this piece is associated with",
    )
    blessed: Optional[bool] = Field(
        default=None, description="Has the piece been blessed/consecrated"
    )
    blessing_authority: Optional[Annotated[str, Field(max_length=200)]] = Field(
        default=None, description="Who blessed it (priest, rabbi, imam, etc.)"
    )
    sacred_origin: Optional[Annotated[str, Field(max_length=200)]] = Field(
        default=None, description="Origin claim (e.g. 'Olive wood from Bethlehem')"
    )
    suitable_for_burial: Optional[bool] = Field(
        default=None, description="Compliant with religious burial customs"
    )
