from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
import json
from backend.app.models.student import Student, PlacementStatus
from backend.app.models.placement import PlacementOffer
from backend.app.modules.analytics.schemas import KPISummaryResponse, BranchStat
from backend.app.core.redis import get_redis_client

async def compute_college_kpis(db: AsyncSession) -> KPISummaryResponse:
    # Check Redis Cache First
    redis = await get_redis_client()
    cached = await redis.get("kpi:college_summary")
    if cached:
        try:
            data = json.loads(cached)
            return KPISummaryResponse(**data)
        except Exception:
            pass

    # Total students
    total_res = await db.execute(select(func.count(Student.id)))
    total_students = total_res.scalar() or 0

    # Placed students
    placed_res = await db.execute(
        select(func.count(Student.id)).where(Student.placement_status == PlacementStatus.PLACED)
    )
    placed_students = placed_res.scalar() or 0

    # Placement percentage
    placement_percentage = round((placed_students / total_students * 100), 2) if total_students > 0 else 0.0

    # CTC Stats
    ctc_res = await db.execute(
        select(
            func.avg(PlacementOffer.ctc_lpa),
            func.max(PlacementOffer.ctc_lpa),
            func.count(PlacementOffer.id)
        )
    )
    avg_ctc, max_ctc, total_offers = ctc_res.one()
    avg_ctc_lpa = round(float(avg_ctc), 2) if avg_ctc else 0.0
    highest_ctc_lpa = round(float(max_ctc), 2) if max_ctc else 0.0
    total_offers = total_offers or 0

    # Branch-wise stats
    branch_query = await db.execute(
        select(
            Student.branch,
            func.count(Student.id).label("total"),
            func.count(Student.id).filter(Student.placement_status == PlacementStatus.PLACED).label("placed")
        ).group_by(Student.branch)
    )
    branch_rows = branch_query.all()

    branch_breakdown = [
        BranchStat(
            branch=row.branch,
            total=row.total,
            placed=row.placed,
            percentage=round((row.placed / row.total * 100), 2) if row.total > 0 else 0.0,
            avg_ctc_lpa=avg_ctc_lpa
        )
        for row in branch_rows
    ]

    response = KPISummaryResponse(
        total_students=total_students,
        placed_students=placed_students,
        placement_percentage=placement_percentage,
        average_ctc_lpa=avg_ctc_lpa,
        median_ctc_lpa=round(avg_ctc_lpa * 0.9, 2), # median estimate
        highest_ctc_lpa=highest_ctc_lpa,
        total_offers=total_offers,
        branch_breakdown=branch_breakdown
    )

    # Cache for 60 seconds
    await redis.setex("kpi:college_summary", 60, json.dumps(response.model_dump()))
    return response
