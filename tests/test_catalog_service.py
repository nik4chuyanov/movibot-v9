from decimal import Decimal

from movibot.catalog_service import CatalogService, SearchQuery
from movibot.models import AccessTier, Bundle, ContentItem


def _item(item_id: str, **kwargs) -> ContentItem:
    defaults = {
        "title": f"Movie {item_id}",
        "description": "Action sci-fi thriller",
        "genres": ("Action",),
        "release_year": 2024,
        "telegram_file_id": f"file-{item_id}",
        "price_usd": Decimal("0"),
        "access_tier": AccessTier.FREE,
        "is_active": True,
    }
    defaults.update(kwargs)
    return ContentItem(item_id=item_id, **defaults)


def test_search_filters_and_sorting() -> None:
    service = CatalogService()
    service.add_content_item(_item("a", title="Alpha", release_year=2020, genres=("Drama",)))
    service.add_content_item(_item("b", title="Beta", release_year=2025, genres=("Action",)))
    service.add_content_item(_item("c", title="Gamma", description="Space opera", genres=("Sci-Fi",)))

    results = service.search(SearchQuery(text="a", genres=("action",)))

    assert [item.item_id for item in results] == ["b"]


def test_favorites_and_catalog_projection() -> None:
    service = CatalogService()
    service.add_content_item(_item("x"))
    service.add_favorite("u1", "x")

    favorites = service.list_favorites("u1")
    catalog = service.list_catalog_for_user("u1")

    assert favorites[0].item_id == "x"
    assert catalog[0]["is_favorite"] is True


def test_vip_and_paid_access_and_delivery() -> None:
    service = CatalogService()
    service.add_content_item(_item("vip", access_tier=AccessTier.VIP, telegram_file_id="vip-file"))
    service.add_content_item(_item("paid", price_usd=Decimal("4.99"), telegram_file_id="paid-file"))

    assert service.can_access("u2", "vip") is False
    service.grant_vip("u2")
    assert service.can_access("u2", "vip") is True
    assert service.resolve_delivery_file_id("u2", "vip") == "vip-file"

    assert service.can_access("u2", "paid") is False
    service.purchase_item("u2", "paid")
    assert service.resolve_delivery_file_id("u2", "paid") == "paid-file"


def test_bundle_purchase_unlocks_all_items() -> None:
    service = CatalogService()
    service.add_content_item(_item("i1", price_usd=Decimal("2.00")))
    service.add_content_item(_item("i2", price_usd=Decimal("3.00")))
    service.add_bundle(Bundle(bundle_id="b1", title="Starter", item_ids=("i1", "i2"), price_usd=Decimal("4.00")))

    service.purchase_bundle("u3", "b1")

    assert service.can_access("u3", "i1") is True
    assert service.can_access("u3", "i2") is True


def test_legacy_scheduler_and_admin_queue_compatibility() -> None:
    class Scheduler:
        def __init__(self):
            self.events = []

        def enqueue(self, kind: str, ref: str) -> None:
            self.events.append((kind, ref))

    class AdminQueue:
        def __init__(self):
            self.events = []

        def push(self, payload):
            self.events.append(payload)

    scheduler = Scheduler()
    admin_queue = AdminQueue()
    service = CatalogService(scheduler=scheduler, admin_queue=admin_queue)
    service.add_content_item(_item("legacy"))
    service.grant_vip("u4")

    assert scheduler.events == [("catalog_sync", "legacy")]
    assert admin_queue.events[-1] == {"event": "vip_granted", "ref_id": "u4"}
