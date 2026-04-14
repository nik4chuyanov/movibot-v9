from sqlalchemy.orm import Session

from app.db.models import MediaItem
from app.services.queue_service import QueueService


class ScannerService:
    def __init__(self, db: Session, queue_service: QueueService) -> None:
        self.db = db
        self.queue_service = queue_service

    def scan_sources(self, sources: list[str]) -> int:
        created = 0
        for source in sources:
            title = f"Discovered from {source}"
            payload = f"{{\"source\": \"{source}\", \"title\": \"{title}\"}}"
            item = MediaItem(source=source, title=title, payload=payload)
            self.db.add(item)
            self.db.flush()
            self.queue_service.enqueue({"id": item.id})
            created += 1

        self.db.commit()
        return created
