"""OJS v1.0 — Reviews domain.

Aggregate review data. STRONG conversion + AI ranking signal — every
primary-source AI commerce spec (ACP, GMC) supports aggregate rating.

NOTE on optimal rating band per Northwestern Spiegel Research Center 2017
(20M+ product pages with PowerReviews): purchase likelihood peaks at
4.0-4.7 stars; 5.0-star products underperform 4.75-4.99 due to
consumer suspicion. Authentic mid-band ratings outperform perfect ones.
"""
from __future__ import annotations

from datetime import date
from typing import Annotated, Optional

from pydantic import Field

from ._common import OJSBaseModel


class AggregateRating(OJSBaseModel):
    """Aggregate review summary.

    Maps to Schema.org AggregateRating. Required by GMC for review
    extensions to display in Shopping. ACP recommends `star_rating` +
    `review_count` at product level.
    """

    rating_value: Annotated[float, Field(ge=0, le=5)] = Field(
        description="Average rating on 0-5 scale"
    )
    review_count: Annotated[int, Field(ge=0)] = Field(
        description="Number of reviews"
    )
    best_rating: float = Field(default=5.0, description="Max possible rating (typically 5.0)")
    worst_rating: float = Field(default=1.0, description="Min possible rating")


class Review(OJSBaseModel):
    """A single review (optional; mostly used for syndication)."""

    rating: Annotated[float, Field(ge=0, le=5)] = Field(description="0-5 rating")
    author_name: Optional[Annotated[str, Field(max_length=100)]] = None
    verified_purchase: Optional[bool] = None
    title: Optional[Annotated[str, Field(max_length=200)]] = None
    body: Optional[Annotated[str, Field(max_length=5000)]] = None
    review_date: Optional[date] = None
    review_url: Optional[str] = None
    helpful_votes: Optional[Annotated[int, Field(ge=0)]] = None


class ReviewsModule(OJSBaseModel):
    """Reviews data — aggregate and (optionally) individual."""

    aggregate: Optional[AggregateRating] = Field(
        default=None, description="Summary stats (preferred over individual reviews)"
    )
    reviews: list[Review] = Field(
        default_factory=list,
        max_length=20,
        description="Optional individual reviews (cap at 20 for feed size)",
    )
    qa_questions: list[Annotated[str, Field(max_length=500)]] = Field(
        default_factory=list,
        description="Customer questions (for q_and_a feed in ACP)",
    )
    qa_answers: list[Annotated[str, Field(max_length=2000)]] = Field(
        default_factory=list,
        description="Corresponding answers — same index as qa_questions",
    )
