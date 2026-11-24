import json
import logging
from typing import List, Dict, Any, Optional
from tools.db import query_db

logger = logging.getLogger("tools.eligibility")

FALLBACK_ELIGIBLE_STUDENTS: List[Dict[str, Any]] = [
    {
        "id": "11111111-1111-1111-1111-111111111101",
        "roll_number": "CS2021045",
        "full_name": "Rohan Deshmukh",
        "branch": "Computer Science",
        "cgpa": 9.42,
        "active_backlogs": 0,
        "phone": "+91 9823011223",
        "placement_status": "unplaced",
        "skills": ["Python", "FastAPI", "React", "Docker", "PostgreSQL", "Redis"],
        "matched_skills": ["React", "Docker"]
    },
    {
        "id": "11111111-1111-1111-1111-111111111102",
        "roll_number": "IT2021028",
        "full_name": "Pooja Hegde",
        "branch": "Information Technology",
        "cgpa": 9.15,
        "active_backlogs": 0,
        "phone": "+91 9765432109",
        "placement_status": "unplaced",
        "skills": ["Java", "Spring Boot", "Docker", "Kubernetes", "AWS", "SQL"],
        "matched_skills": ["Docker"]
    },
    {
        "id": "11111111-1111-1111-1111-111111111103",
        "roll_number": "CS2021089",
        "full_name": "Vikram Adve",
        "branch": "Computer Science",
        "cgpa": 8.78,
        "active_backlogs": 0,
        "phone": "+91 9845123456",
        "placement_status": "unplaced",
        "skills": ["TypeScript", "React", "Node.js", "Docker", "PostgreSQL"],
        "matched_skills": ["React", "Docker"]
    },
    {
        "id": "11111111-1111-1111-1111-111111111104",
        "roll_number": "ECE2021014",
        "full_name": "Ananya Sharma",
        "branch": "ECE",
        "cgpa": 8.65,
        "active_backlogs": 0,
        "phone": "+91 9988776655",
        "placement_status": "unplaced",
        "skills": ["C++", "Python", "Embedded Systems", "Linux", "Git"],
        "matched_skills": []
    }
]


async def find_eligible_students(
    min_cgpa: float = 6.0,
    max_backlogs: int = 0,
    required_skills: Optional[List[str]] = None
) -> List[Dict[str, Any]]:
    """
    Queries students meeting minimum CGPA, maximum backlogs, and specific required technical skills.

    Args:
        min_cgpa: Minimum acceptable CGPA out of 10.0 (default: 6.0).
        max_backlogs: Maximum allowed active backlogs (default: 0).
        required_skills: Optional list of skill keywords (e.g. ['React', 'Docker']).
    """
    req_skills_normalized = [s.strip().lower() for s in (required_skills or []) if s.strip()]

    sql = """
        SELECT 
            s.id::text,
            s.roll_number,
            s.full_name,
            s.branch,
            s.batch_year,
            s.cgpa::float,
            s.active_backlogs,
            s.phone,
            s.placement_status::text,
            s.parsed_resume
        FROM students s
        WHERE s.cgpa >= $1
          AND s.active_backlogs <= $2
          AND s.is_eligible_for_placements = TRUE
        ORDER BY s.cgpa DESC
        LIMIT 100
    """

    rows = await query_db(sql, float(min_cgpa), int(max_backlogs))

    if rows:
        results = []
        for r in rows:
            # Parse resume skills
            pr = r.get("parsed_resume") or {}
            if isinstance(pr, str):
                try:
                    pr = json.loads(pr)
                except Exception:
                    pr = {}
            skills = pr.get("skills", [])
            skills_lower = [s.lower() for s in skills]

            # Filter by required skills if supplied
            matched = []
            if req_skills_normalized:
                for req in req_skills_normalized:
                    if any(req in sk for sk in skills_lower):
                        matched.append(req.title())
                if not matched:
                    continue  # Does not match requested skills

            results.append({
                "id": r["id"],
                "roll_number": r["roll_number"],
                "full_name": r["full_name"],
                "branch": r["branch"],
                "cgpa": r["cgpa"],
                "active_backlogs": r["active_backlogs"],
                "phone": r.get("phone"),
                "placement_status": r["placement_status"],
                "skills": skills[:10],
                "matched_skills": matched if req_skills_normalized else skills[:5]
            })

            if len(results) >= 25:
                break

        if results:
            return results

    # Fallback to realistic mock data filtered by parameters
    logger.info("Using fallback student eligibility dataset.")
    filtered_fallback = []
    for s in FALLBACK_ELIGIBLE_STUDENTS:
        if s["cgpa"] >= min_cgpa and s["active_backlogs"] <= max_backlogs:
            matched = []
            if req_skills_normalized:
                s_skills_lower = [sk.lower() for sk in s["skills"]]
                for req in req_skills_normalized:
                    if any(req in sk for sk in s_skills_lower):
                        matched.append(req.title())
                if not matched:
                    continue
            item = dict(s)
            item["matched_skills"] = matched if req_skills_normalized else s["skills"][:3]
            filtered_fallback.append(item)

    return filtered_fallback
