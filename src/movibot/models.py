from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum


class AccessTier(str, Enum):
    FREE = "free"
    VIP = "vip"


@dataclass(slots=True)
class ContentItem:
    item_id: str
    title: str
    description: str
    genres: tuple[str, ...]
    release_year: int
    telegram_file_id: str
    price_usd: Decimal = Decimal("0")
    access_tier: AccessTier = AccessTier.FREE
    is_active: bool = True


@dataclass(slots=True)
class Bundle:
    bundle_id: str
    title: str
    item_ids: tuple[str, ...]
    price_usd: Decimal
    is_active: bool = True


@dataclass(slots=True)
class PurchaseRecord:
    user_id: str
    sku: str
    amount_usd: Decimal
    purchased_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(slots=True)
class UserProfile:
    user_id: str
    is_vip: bool = False
    favorite_item_ids: set[str] = field(default_factory=set)
    purchased_skus: set[str] = field(default_factory=set)
    purchased_item_ids: set[str] = field(default_factory=set)
