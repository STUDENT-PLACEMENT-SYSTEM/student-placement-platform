import redis.asyncio as aioredis
from typing import Optional, AsyncGenerator
import json
from backend.app.core.config import settings

redis_client: Optional[aioredis.Redis] = None

async def get_redis_client() -> aioredis.Redis:
    global redis_client
    if redis_client is None:
        redis_client = aioredis.from_url(
            settings.REDIS_URL,
            decode_responses=True,
            encoding="utf-8"
        )
    return redis_client

async def publish_event(channel: str, message: dict) -> int:
    client = await get_redis_client()
    return await client.publish(channel, json.dumps(message))

async def subscribe_channel(channel: str) -> AsyncGenerator[dict, None]:
    client = await get_redis_client()
    pubsub = client.pubsub()
    await pubsub.subscribe(channel)
    try:
        async for message in pubsub.listen():
            if message["type"] == "message":
                try:
                    data = json.loads(message["data"])
                    yield data
                except Exception:
                    yield {"raw": message["data"]}
    finally:
        await pubsub.unsubscribe(channel)
        await pubsub.close()
