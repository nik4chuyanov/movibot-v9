import json

from redis import Redis


class QueueService:
    def __init__(self, redis_client: Redis, queue_name: str = "movibot:queue") -> None:
        self.redis = redis_client
        self.queue_name = queue_name

    def enqueue(self, item: dict) -> None:
        self.redis.rpush(self.queue_name, json.dumps(item))

    def dequeue(self) -> dict | None:
        payload = self.redis.lpop(self.queue_name)
        if payload is None:
            return None
        return json.loads(payload)

    def size(self) -> int:
        return int(self.redis.llen(self.queue_name))
