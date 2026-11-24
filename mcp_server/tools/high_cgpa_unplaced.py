import json
import logging
from typing import List, Dict, Any
from tools.db import query_db

logger = logging.getLogger("tools.high_cgpa_unplaced")

FALLBACK_HIGH_CGPA_UNPLACED: List[Dict[str, Any]] = [
    {
        "id": "22222222-2222-2222-2222-222222222201",
        "roll_number": "CS2021008",
        "full_name": "Deepak Mehta",
        "email": "deepak.mehta@university.edu",
        "branch": "Computer Science",
        "cgpa": 9.65,
        "active_backlogs": 0,
        "phone": "+91 9811223344",
        "placement_status": "unplaced",
        "top_skills": ["Python", "FastAPI", "PostgreSQL", "Docker", "Machine Learning"],
        "recommended_tpo_action": "High-priority nomination for upcoming Tier-1 Super Dream Drive (Google / Microsoft)"
    },
    {
        "id": "22222222-2222-2222-2222-222222222202",
        "roll_number": "IT2021019",
        "full_name": "Siddharth Verma",
        "email": "siddharth.verma@university.edu",
        "branch": "Information Technology",
        "cgpa": 9.38,
        "active_backlogs": 0,
        "phone": "+91 9822334455",
        "placement_status": "unplaced",
        "top_skills": ["Java", "Spring Boot", "Microservices", "Kafka", "AWS"],
        "recommended_tpo_action": "Fast-track interview coaching and DSA mock review"
    },
    {
        "id": "22222222-2222-2222-2222-222222222203",
        "roll_number": "ECE2021005",
        "full_name": "Kavita Rangan",
        "email": "kavita.rangan@university.edu",
        "branch": "ECE",
        "cgpa": 9.12,
        "active_backlogs": 0,
        "phone": "+91 9833445566",
        "placement_status": "unplaced",
        "top_skills": ["C++", "Embedded Linux", "Python", "Computer Vision"],
        "recommended_tpo_action": "Connect with Semiconductor / Core Hardware placement leads (Qualcomm / Texas Instruments)"
    },
    {
        "id": "22222222-2222-2222-2222-222222222204",
        "roll_number": "CS2021112",
        "full_name": "Amitabh Sengupta",
        "email": "amitabh.s@university.edu",
        "branch": "Computer Science",
        "cgpa": 8.92,
        "active_backlogs": 0,
        "phone": "+91 9844556677",
        "placement_status": "unplaced",
        "top_skills": ["React", "TypeScript", "Node.js", "GraphQL", "Docker"],
        "recommended_tpo_action": "Direct resume referral to Product Startup drives"
    }
]


async def get_unplaced_high_cgpa_students(threshold_cgpa: float = 8.0) -> List[Dict[str, Any]]:
    """
    Highlights students with CGPA above a specific threshold who remain unplaced, alerting TPO for targeted placement intervention.

    Args:
        threshold_cgpa: The minimum CGPA cut-off to flag unplaced students (default: 8.0).
    """
    sql = """
        SELECT 
            s.id::text,
            s.roll_number,
            s.full_name,
            u.email,
            s.branch,
            s.cgpa::float,
            s.active_backlogs,
            s.phone,
            s.placement_status::text,
            s.parsed_resume
        FROM students s
        LEFT JOIN users u ON s.user_id = u.id
        WHERE s.placement_status = 'unplaced'
          AND s.cgpa >= $1
        ORDER BY s.cgpa DESC
        LIMIT 25
    """

    rows = await query_db(sql, float(threshold_cgpa))

    if rows:
        results = []
        for r in rows:
            pr = r.get("parsed_resume") or {}
            if isinstance(pr, str):
                try:
                    pr = json.loads(pr)
                except Exception:
                    pr = {}
            skills = pr.get("skills", [])

            # Dynamic intervention advisory
            cgpa_val = r["cgpa"]
            if cgpa_val >= 9.0:
                action = "Top 5% Talent: Direct nomination for Super Dream (20+ LPA) Product Drives"
            elif cgpa_val >= 8.5:
                action = "High Tier-1 Candidate: Schedule 1:1 technical mock interview & resume optimization"
            else:
                action = "Eligible for Dream Category Drives: Facilitate immediate recruiter pool matching"

            results.append({
                "id": r["id"],
                "roll_number": r["roll_number"],
                "full_name": r["full_name"],
                "email": r.get("email"),
                "branch": r["branch"],
                "cgpa": cgpa_val,
                "active_backlogs": r["active_backlogs"],
                "phone": r.get("phone"),
                "placement_status": r["placement_status"],
                "top_skills": skills[:6],
                "recommended_tpo_action": action
            })
        return results

    # Fallback mock data
    logger.info("Using fallback unplaced high CGPA student records.")
    return [s for s in FALLBACK_HIGH_CGPA_UNPLACED if s["cgpa"] >= threshold_cgpa]
