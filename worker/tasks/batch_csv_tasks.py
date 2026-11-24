import csv
import io
import re
import uuid
import logging
from typing import Optional, Dict, Any, List, Union
import asyncpg
from config import settings, get_asyncpg_dsn

logger = logging.getLogger(__name__)

# Default hashed password for bulk created student accounts (e.g., student123 bcrypt placeholder)
DEFAULT_PASSWORD_HASH = "$2b$12$e80g6aQzQ2GvV0jY7rXqAe1V0kU5qS8U.oQjT8ZcE6eP1I4JvWqCe"


def validate_email(email: str) -> bool:
    return bool(re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", email))


async def ingest_student_csv_task(
    ctx_or_content: Any,
    csv_content: Optional[Union[str, bytes]] = None,
    default_batch_year: int = 2025
) -> Dict[str, Any]:
    """
    Task to validate and ingest student bulk records from a CSV file.
    Creates corresponding user accounts with role 'student' and upserts student profiles.
    """
    # Flexibility for ARQ context or direct invocation
    if isinstance(ctx_or_content, dict) or hasattr(ctx_or_content, "redis"):
        raw_data = csv_content
    else:
        raw_data = ctx_or_content or csv_content

    if isinstance(raw_data, bytes):
        raw_data = raw_data.decode("utf-8-sig", errors="replace")

    if not raw_data:
        return {"success": False, "error": "No CSV content provided", "total_rows": 0}

    reader = csv.DictReader(io.StringIO(raw_data.strip()))
    
    # Normalize header names (lowercase and strip whitespace)
    if not reader.fieldnames:
        return {"success": False, "error": "CSV contains no header row", "total_rows": 0}

    rows = list(reader)
    total_rows = len(rows)
    inserted = 0
    updated = 0
    errors: List[Dict[str, Any]] = []

    dsn = get_asyncpg_dsn()
    try:
        conn = await asyncpg.connect(dsn, timeout=10.0)
        try:
            async with conn.transaction():
                for idx, row in enumerate(rows, start=2): # 1-indexed, line 2 after header
                    # Clean dictionary keys
                    clean_row = {k.strip().lower(): (v.strip() if v else "") for k, v in row.items() if k}

                    roll_number = clean_row.get("roll_number") or clean_row.get("roll_no") or clean_row.get("rollno")
                    full_name = clean_row.get("full_name") or clean_row.get("name")
                    email = clean_row.get("email")
                    branch = clean_row.get("branch") or clean_row.get("department") or "Computer Science"
                    
                    # Validation of core fields
                    if not roll_number or not full_name or not email:
                        errors.append({
                            "line": idx,
                            "error": "Missing required fields (roll_number, full_name, or email)",
                            "data": clean_row
                        })
                        continue

                    if not validate_email(email):
                        errors.append({
                            "line": idx,
                            "error": f"Invalid email format: {email}",
                            "roll_number": roll_number
                        })
                        continue

                    # Batch year
                    batch_year = default_batch_year
                    if clean_row.get("batch_year"):
                        try:
                            batch_year = int(clean_row["batch_year"])
                        except ValueError:
                            pass

                    # CGPA validation
                    cgpa = 0.0
                    raw_cgpa = clean_row.get("cgpa") or clean_row.get("gpa")
                    if raw_cgpa:
                        try:
                            val = float(raw_cgpa)
                            if val > 10.0 and val <= 100.0:
                                val = round(val / 10.0, 2)
                            if 0.0 <= val <= 10.0:
                                cgpa = val
                            else:
                                errors.append({"line": idx, "error": f"CGPA out of range (0-10): {val}", "roll_number": roll_number})
                                continue
                        except ValueError:
                            errors.append({"line": idx, "error": f"Invalid CGPA float: {raw_cgpa}", "roll_number": roll_number})
                            continue

                    # Backlogs
                    active_backlogs = 0
                    if clean_row.get("active_backlogs"):
                        try:
                            active_backlogs = max(0, int(clean_row["active_backlogs"]))
                        except ValueError:
                            pass

                    history_of_backlogs = active_backlogs
                    if clean_row.get("history_of_backlogs"):
                        try:
                            history_of_backlogs = max(active_backlogs, int(clean_row["history_of_backlogs"]))
                        except ValueError:
                            pass

                    phone = clean_row.get("phone") or clean_row.get("mobile")
                    linkedin_url = clean_row.get("linkedin_url") or clean_row.get("linkedin")
                    github_url = clean_row.get("github_url") or clean_row.get("github")

                    # 1. Upsert User
                    user_row = await conn.fetchrow("SELECT id FROM users WHERE email = $1", email)
                    if user_row:
                        user_id = user_row["id"]
                    else:
                        user_id = await conn.fetchval(
                            """
                            INSERT INTO users (email, hashed_password, role, is_active, is_verified)
                            VALUES ($1, $2, 'student', TRUE, TRUE)
                            RETURNING id
                            """,
                            email,
                            DEFAULT_PASSWORD_HASH
                        )

                    # 2. Upsert Student profile
                    existing_student = await conn.fetchrow(
                        "SELECT id FROM students WHERE roll_number = $1 OR user_id = $2",
                        roll_number,
                        user_id
                    )

                    if existing_student:
                        await conn.execute(
                            """
                            UPDATE students
                            SET full_name = $1,
                                branch = $2,
                                batch_year = $3,
                                cgpa = $4,
                                active_backlogs = $5,
                                history_of_backlogs = $6,
                                phone = COALESCE($7, phone),
                                linkedin_url = COALESCE($8, linkedin_url),
                                github_url = COALESCE($9, github_url),
                                updated_at = CURRENT_TIMESTAMP
                            WHERE id = $10
                            """,
                            full_name, branch, batch_year, cgpa,
                            active_backlogs, history_of_backlogs,
                            phone, linkedin_url, github_url,
                            existing_student["id"]
                        )
                        updated += 1
                    else:
                        await conn.execute(
                            """
                            INSERT INTO students (
                                user_id, roll_number, full_name, branch, batch_year,
                                cgpa, active_backlogs, history_of_backlogs, phone,
                                linkedin_url, github_url
                            )
                            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
                            """,
                            user_id, roll_number, full_name, branch, batch_year,
                            cgpa, active_backlogs, history_of_backlogs, phone,
                            linkedin_url, github_url
                        )
                        inserted += 1

        finally:
            await conn.close()
    except Exception as e:
        logger.error(f"Database error during CSV ingestion: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "total_rows": total_rows,
            "inserted": inserted,
            "updated": updated,
            "errors": errors
        }

    return {
        "success": True,
        "total_rows": total_rows,
        "inserted": inserted,
        "updated": updated,
        "error_count": len(errors),
        "errors": errors[:50]  # First 50 error rows for report
    }
