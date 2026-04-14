from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from decimal import Decimal

from .models import AccessTier, Bundle, ContentItem, PurchaseRecord, UserProfile


@dataclass(slots=True)
class SearchQuery:
    text: str = ""
    genres: tuple[str, ...] = ()
    release_year: int | None = None
    include_inactive: bool = False


class CatalogService:
    """In-memory user-facing movie catalog with legacy integration hooks."""

    def __init__(self, scheduler: object | None = None, admin_queue: object | None = None) -> None:
        self._items: dict[str, ContentItem] = {}
        self._bundles: dict[str, Bundle] = {}
        self._users: dict[str, UserProfile] = {}
        self._purchases: list[PurchaseRecord] = []
        self._scheduler = scheduler
        self._admin_queue = admin_queue

    # ---- content items ----
    def add_content_item(self, item: ContentItem) -> None:
        self._items[item.item_id] = item
        self._notify_scheduler(item)

    def add_bundle(self, bundle: Bundle) -> None:
        missing = [item_id for item_id in bundle.item_ids if item_id not in self._items]
        if missing:
            raise ValueError(f"Bundle contains unknown items: {missing}")
        self._bundles[bundle.bundle_id] = bundle
        self._notify_admin_queue("bundle_created", bundle.bundle_id)

    # ---- search ----
    def search(self, query: SearchQuery) -> list[ContentItem]:
        needle = query.text.casefold().strip()
        genre_filter = {genre.casefold() for genre in query.genres}
        results: list[ContentItem] = []
        for item in self._items.values():
            if not query.include_inactive and not item.is_active:
                continue
            if query.release_year is not None and item.release_year != query.release_year:
                continue
            if genre_filter and not (genre_filter & {genre.casefold() for genre in item.genres}):
                continue
            if needle and needle not in item.title.casefold() and needle not in item.description.casefold():
                continue
            results.append(item)
        return sorted(results, key=lambda c: (c.release_year, c.title), reverse=True)

    # ---- favorites ----
    def add_favorite(self, user_id: str, item_id: str) -> None:
        self._validate_item_exists(item_id)
        self._user(user_id).favorite_item_ids.add(item_id)

    def remove_favorite(self, user_id: str, item_id: str) -> None:
        self._user(user_id).favorite_item_ids.discard(item_id)

    def list_favorites(self, user_id: str) -> list[ContentItem]:
        profile = self._user(user_id)
        return [self._items[item_id] for item_id in profile.favorite_item_ids if item_id in self._items]

    # ---- VIP ----
    def grant_vip(self, user_id: str) -> None:
        self._user(user_id).is_vip = True
        self._notify_admin_queue("vip_granted", user_id)

    def revoke_vip(self, user_id: str) -> None:
        self._user(user_id).is_vip = False
        self._notify_admin_queue("vip_revoked", user_id)

    # ---- purchases ----
    def purchase_item(self, user_id: str, item_id: str) -> PurchaseRecord:
        item = self._items.get(item_id)
        if item is None:
            raise KeyError(f"Unknown item {item_id}")

        record = PurchaseRecord(user_id=user_id, sku=item.item_id, amount_usd=item.price_usd)
        profile = self._user(user_id)
        profile.purchased_skus.add(item.item_id)
        profile.purchased_item_ids.add(item.item_id)
        self._purchases.append(record)
        self._notify_admin_queue("item_purchased", item.item_id)
        return record

    def purchase_bundle(self, user_id: str, bundle_id: str) -> PurchaseRecord:
        bundle = self._bundles.get(bundle_id)
        if bundle is None or not bundle.is_active:
            raise KeyError(f"Unknown bundle {bundle_id}")

        profile = self._user(user_id)
        for item_id in bundle.item_ids:
            profile.purchased_item_ids.add(item_id)
        profile.purchased_skus.add(bundle.bundle_id)

        record = PurchaseRecord(user_id=user_id, sku=bundle.bundle_id, amount_usd=bundle.price_usd)
        self._purchases.append(record)
        self._notify_admin_queue("bundle_purchased", bundle.bundle_id)
        return record

    # ---- access + delivery ----
    def can_access(self, user_id: str, item_id: str) -> bool:
        item = self._items.get(item_id)
        if item is None or not item.is_active:
            return False
        profile = self._user(user_id)
        if item.access_tier == AccessTier.VIP and not profile.is_vip:
            return item_id in profile.purchased_item_ids
        if item.price_usd > Decimal("0"):
            return item_id in profile.purchased_item_ids
        return True

    def resolve_delivery_file_id(self, user_id: str, item_id: str) -> str:
        if not self.can_access(user_id, item_id):
            raise PermissionError(f"User {user_id} does not have access to {item_id}")
        return self._items[item_id].telegram_file_id

    def list_catalog_for_user(self, user_id: str) -> list[dict[str, object]]:
        profile = self._user(user_id)
        response: list[dict[str, object]] = []
        for item in sorted(self._items.values(), key=lambda c: c.title):
            response.append(
                {
                    "item_id": item.item_id,
                    "title": item.title,
                    "description": item.description,
                    "genres": item.genres,
                    "release_year": item.release_year,
                    "is_favorite": item.item_id in profile.favorite_item_ids,
                    "is_accessible": self.can_access(user_id, item.item_id),
                    "access_tier": item.access_tier.value,
                    "price_usd": str(item.price_usd),
                }
            )
        return response

    def purchases_for_user(self, user_id: str) -> list[PurchaseRecord]:
        return [record for record in self._purchases if record.user_id == user_id]

    # ---- internal helpers ----
    def _validate_item_exists(self, item_id: str) -> None:
        if item_id not in self._items:
            raise KeyError(f"Unknown item {item_id}")

    def _user(self, user_id: str) -> UserProfile:
        if user_id not in self._users:
            self._users[user_id] = UserProfile(user_id=user_id)
        return self._users[user_id]

    def _notify_scheduler(self, item: ContentItem) -> None:
        if self._scheduler is None:
            return
        # legacy scheduler compatibility
        if hasattr(self._scheduler, "schedule_catalog_sync"):
            self._scheduler.schedule_catalog_sync(item.item_id)
        elif hasattr(self._scheduler, "enqueue"):
            self._scheduler.enqueue("catalog_sync", item.item_id)

    def _notify_admin_queue(self, event_type: str, ref_id: str) -> None:
        if self._admin_queue is None:
            return
        payload = {"event": event_type, "ref_id": ref_id}
        # legacy admin queue compatibility
        if hasattr(self._admin_queue, "publish"):
            self._admin_queue.publish(payload)
        elif hasattr(self._admin_queue, "push"):
            self._admin_queue.push(payload)


def build_catalog(service: CatalogService, items: Iterable[ContentItem], bundles: Iterable[Bundle] = ()) -> CatalogService:
    for item in items:
        service.add_content_item(item)
    for bundle in bundles:
        service.add_bundle(bundle)
    return service
