from datetime import datetime

from sqlalchemy.orm import Session

from app.db.models import ItemStatus, MediaItem
from app.services.queue_service import QueueService


class PublishService:
    def __init__(self, db: Session, queue_service: QueueService) -> None:
        self.db = db
        self.queue_service = queue_service

    def publish_next(self) -> int:
        message = self.queue_service.dequeue()
        if not message:
            return 0

        item = self.db.get(MediaItem, message["id"])
        if not item:
            return 0

        item.status = ItemStatus.published
        item.published_at = datetime.utcnow()
        self.db.add(item)
        self.db.commit()
        return 1
