import asyncio
import json
import logging
import signal
import sys
from typing import Any, Dict

from arq.connections import RedisSettings
import redis.asyncio as aioredis

from config import settings
from tasks.resume_tasks import process_resume_task
from tasks.batch_csv_tasks import ingest_student_csv_task
from workflows.skill_gap_agent_graph import skill_gap_graph, SkillGapState

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("placement_worker")


# ============================================================================
# 1. ARQ Worker Settings
# ============================================================================

async def startup(ctx: Dict[Any, Any]):
    logger.info("Initializing Placement Worker services...")
    logger.info(f"Connected to Redis: {settings.REDIS_URL}")
    logger.info(f"Target Database: {settings.POSTGRES_DB} at {settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}")


async def shutdown(ctx: Dict[Any, Any]):
    logger.info("Shutting down Placement Worker cleanly.")


async def generate_skill_gap_roadmap_task(
    ctx: Any,
    student_id: str,
    target_drive_id: str = None,
    target_role: str = "Software Engineer"
) -> Dict[str, Any]:
    """Task to trigger the LangGraph skill gap roadmap generation."""
    logger.info(f"Generating skill gap roadmap for student={student_id}, role={target_role}")
    initial_state: SkillGapState = {
        "student_id": student_id,
        "target_drive_id": target_drive_id,
        "target_role": target_role,
        "student_skills": [],
        "target_jd_text": "",
        "missing_skills": [],
        "recommended_projects": [],
        "roadmap_weeks": [],
        "success": False,
        "error": None
    }
    result = await skill_gap_graph.ainvoke(initial_state)
    return {
        "student_id": student_id,
        "success": result.get("success", False),
        "missing_skills": result.get("missing_skills", []),
        "roadmap_weeks": result.get("roadmap_weeks", []),
        "error": result.get("error")
    }


class WorkerSettings:
    """ARQ Worker configuration class."""
    functions = [
        process_resume_task,
        ingest_student_csv_task,
        generate_skill_gap_roadmap_task
    ]
    on_startup = startup
    on_shutdown = shutdown
    redis_settings = RedisSettings.from_dsn(settings.REDIS_URL)
    max_jobs = 10
    job_timeout = 300


# ============================================================================
# 2. Standalone Polling & Event Listener Mode
# ============================================================================

async def run_standalone_listener():
    """Fallback queue runner listening to Redis task queues or pub/sub."""
    logger.info("Starting standalone task listener on Redis...")
    r = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
    stop_event = asyncio.Event()

    def handle_sig(*_):
        logger.info("Termination signal received. Exiting loop.")
        stop_event.set()

    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, handle_sig)
        except NotImplementedError:
            pass

    try:
        await r.ping()
        logger.info("Successfully connected to Redis!")
    except Exception as e:
        logger.warning(f"Could not connect to Redis ({e}). Running standby healthcheck loop.")

    # Main worker loop
    while not stop_event.is_set():
        try:
            # Check for queued resume parsing tasks in Redis list 'queue:resumes'
            item = await r.rpop("queue:resumes")
            if item:
                logger.info(f"Received resume task: {item}")
                data = json.loads(item)
                await process_resume_task(
                    student_id_or_s3_key=data.get("student_id"),
                    s3_key=data.get("s3_key")
                )
            else:
                await asyncio.sleep(1.0)
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.debug(f"Listener loop ping: {e}")
            await asyncio.sleep(2.0)

    await r.aclose()
    logger.info("Standalone listener closed.")


if __name__ == "__main__":
    logger.info("Starting Placement Analytics Worker...")
    try:
        from arq import run_worker
        run_worker(WorkerSettings)
    except Exception as e:
        logger.info(f"Running standalone listener due to: {e}")
        asyncio.run(run_standalone_listener())
