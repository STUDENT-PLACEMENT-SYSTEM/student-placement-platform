import asyncio
import json
from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.core.database import get_db, AsyncSessionLocal
from backend.app.modules.analytics.schemas import KPISummaryResponse
from backend.app.modules.analytics.service import compute_college_kpis
from backend.app.core.redis import subscribe_channel

router = APIRouter(prefix="/analytics", tags=["Analytics & Real-Time SSE"])

@router.get("/summary", response_model=KPISummaryResponse)
async def get_summary(db: AsyncSession = Depends(get_db)):
    return await compute_college_kpis(db)

@router.get("/live-kpis")
async def stream_live_kpis(request: Request):
    """
    Server-Sent Events (SSE) live streaming endpoint.
    Streams updated KPIs whenever an event is published to Redis channel 'tpo:live_analytics'.
    Also sends initial state upon connection and heartbeat every 15s.
    """
    async def event_generator():
        # Send initial snapshot immediately
        async with AsyncSessionLocal() as db:
            initial_kpis = await compute_college_kpis(db)
            yield f"event: kpi_update\ndata: {json.dumps(initial_kpis.model_dump())}\n\n"

        # Listen to Redis Pub/Sub
        pubsub_gen = subscribe_channel("tpo:live_analytics")
        try:
            async for event_payload in pubsub_gen:
                if await request.is_disconnected():
                    break
                
                # Re-compute and stream updated metrics
                async with AsyncSessionLocal() as db:
                    updated_kpis = await compute_college_kpis(db)
                    payload_dict = updated_kpis.model_dump()
                    payload_dict["recent_activity"] = event_payload
                    
                    yield f"event: kpi_update\ndata: {json.dumps(payload_dict)}\n\n"
        except asyncio.CancelledError:
            pass

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )
