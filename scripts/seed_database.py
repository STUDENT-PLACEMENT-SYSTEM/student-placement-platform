import asyncio
import csv
import json
import os
import uuid
from datetime import datetime, timezone, date, timedelta
import bcrypt
import asyncpg

DB_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5433/placement_db")

def hash_pw(pw: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pw[:72].encode("utf-8"), salt).decode("utf-8")

async def seed():
    print(f"Connecting to {DB_URL}...")
    conn = await asyncpg.connect(DB_URL)
    
    print("Clearing existing seed data...")
    await conn.execute("""
        TRUNCATE TABLE placement_offers, drive_applications, drives, recruiters, 
        student_embeddings, skill_gap_roadmaps, ml_predictions, students, audit_logs, users CASCADE;
    """)

    admin_pw = hash_pw("Admin@123")
    tpo_pw = hash_pw("Tpo@123")
    rec_pw = hash_pw("Recruiter@123")
    std_pw = hash_pw("Student@123")

    print("Creating core role accounts (Admin, TPO, Recruiters)...")
    # 1. Admin
    admin_id = await conn.fetchval("""
        INSERT INTO users (email, hashed_password, role, is_active, is_verified)
        VALUES ('admin@college.edu', $1, 'admin', true, true) RETURNING id;
    """, admin_pw)

    # 2. TPO
    tpo_id = await conn.fetchval("""
        INSERT INTO users (email, hashed_password, role, is_active, is_verified)
        VALUES ('tpo@college.edu', $1, 'tpo', true, true) RETURNING id;
    """, tpo_pw)

    # 3. Recruiters (Google, Microsoft, Amazon, TCS)
    companies = [
        ("recruiter@google.com", "Google India", "Software & Cloud", "Sundar Pichai", "https://google.com"),
        ("recruiter@microsoft.com", "Microsoft IDC", "Enterprise Cloud", "Satya Nadella", "https://microsoft.com"),
        ("recruiter@amazon.com", "Amazon Development Centre", "E-Commerce & AWS", "Andy Jassy", "https://amazon.jobs"),
        ("recruiter@tcs.com", "Tata Consultancy Services", "IT & Consulting", "K. Krithivasan", "https://tcs.com")
    ]
    
    recruiter_ids = {}
    for email, company, industry, contact, website in companies:
        u_id = await conn.fetchval("""
            INSERT INTO users (email, hashed_password, role, is_active, is_verified)
            VALUES ($1, $2, 'recruiter', true, true) RETURNING id;
        """, email, rec_pw)
        
        r_id = await conn.fetchval("""
            INSERT INTO recruiters (user_id, company_name, industry, website, contact_person, is_approved)
            VALUES ($1, $2, $3, $4, $5, true) RETURNING id;
        """, u_id, company, industry, website, contact)
        recruiter_ids[company] = r_id

    # 4. Placement Drives
    print("Creating placement drives...")
    now = datetime.now(timezone.utc)
    drives_data = [
        ("Software Engineer (Backend)", "Google India", 8.0, 0, ["Computer Science", "Information Technology", "ECE"], 25.0, 32.0, "Bangalore / Hybrid", 28.5),
        ("Software Development Engineer - 1", "Microsoft IDC", 7.5, 0, ["Computer Science", "Information Technology"], 20.0, 26.0, "Hyderabad", 22.0),
        ("SDE-1 (AWS Services)", "Amazon Development Centre", 7.0, 0, ["Computer Science", "Information Technology", "ECE", "Electrical"], 18.0, 24.0, "Bangalore", 20.0),
        ("Associate Software Engineer", "Tata Consultancy Services", 6.0, 1, ["Computer Science", "Information Technology", "ECE", "Electrical", "Mechanical", "Civil"], 4.0, 7.5, "PAN India", 4.5)
    ]
    
    drive_ids = {}
    for role, comp, min_cgpa, max_bl, branches, ctc_min, ctc_max, loc, avg_ctc in drives_data:
        r_id = recruiter_ids.get(comp)
        d_id = await conn.fetchval("""
            INSERT INTO drives (
                recruiter_id, title, role_name, job_description, min_cgpa, max_backlogs,
                allowed_branches, ctc_min_lpa, ctc_max_lpa, job_location, drive_date,
                registration_deadline, status, approved_by_tpo_id
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, 'active', $13)
            RETURNING id;
        """, r_id, f"{comp} - {role}", role, f"We are hiring {role} graduates. Exciting work on cloud, high-scale architectures.",
        min_cgpa, max_bl, branches, ctc_min, ctc_max, loc, date.today() + timedelta(days=15), now + timedelta(days=7), tpo_id)
        drive_ids[comp] = (d_id, avg_ctc)

    # 5. Bulk Ingest 3,000 Synthetic Students
    csv_path = "/home/kali/AIML_student_placement/dataset/synthetic_3000_students.csv"
    if not os.path.exists(csv_path):
        print(f"Warning: {csv_path} not found. Skipping student bulk ingestion.")
        await conn.close()
        return

    print("Reading synthetic 3,000 students dataset...")
    student_records = []
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            student_records.append(row)

    print(f"Ingesting {len(student_records)} students into PostgreSQL...")
    batch_size = 500
    
    # We will insert students and default accounts
    # Demo student first
    demo_user_id = await conn.fetchval("""
        INSERT INTO users (email, hashed_password, role, is_active, is_verified)
        VALUES ('student@college.edu', $1, 'student', true, true) RETURNING id;
    """, std_pw)
    
    await conn.execute("""
        INSERT INTO students (
            user_id, roll_number, full_name, branch, batch_year, cgpa,
            active_backlogs, history_of_backlogs, phone, placement_status
        ) VALUES ($1, 'DEMO-2021-000', 'Aarav Patel (Demo Student)', 'Computer Science', 2025, 8.65, 0, 0, '9876543210', 'unplaced');
    """, demo_user_id)

    placed_count = 0
    offers_to_insert = []

    for i, s in enumerate(student_records):
        email = f"student{s['student_id']}@college.edu"
        roll = s.get("roll_number", f"2021{s['branch'][:2].upper()}{str(i+2).zfill(3)}")
        cgpa = float(s.get("cgpa", 7.5))
        backlogs = int(s.get("backlogs", 0))
        history_bl = int(s.get("history_of_backlogs", 0))
        placed_val = int(s.get("placed", 0))
        placement_status = "placed" if placed_val == 1 else "unplaced"
        pkg_lpa = float(s.get("package_lpa", 0.0))
        comp_name = s.get("company_name", "TCS") if placed_val == 1 else None

        # Insert user
        u_id = await conn.fetchval("""
            INSERT INTO users (email, hashed_password, role, is_active, is_verified)
            VALUES ($1, $2, 'student', true, true) RETURNING id;
        """, email, std_pw)

        # Parse skills if present
        skills_raw = s.get("skills_list", "[]")
        try:
            skills = json.loads(skills_raw) if isinstance(skills_raw, str) else []
        except Exception:
            skills = ["Python", "SQL"]

        parsed_resume = {
            "skills": skills,
            "internships_count": int(s.get("internships", 0)),
            "projects_count": int(s.get("projects_count", 2)),
            "coding_score": float(s.get("coding_skills_score", 6.0))
        }

        # Insert student
        st_id = await conn.fetchval("""
            INSERT INTO students (
                user_id, roll_number, full_name, branch, batch_year, cgpa,
                active_backlogs, history_of_backlogs, parsed_resume, placement_status
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10) RETURNING id;
        """, u_id, roll, s["full_name"], s["branch"], int(s.get("batch_year", 2025)),
        cgpa, backlogs, history_bl, json.dumps(parsed_resume), placement_status)

        # If placed, record offer
        if placed_val == 1 and pkg_lpa > 0:
            placed_count += 1
            offers_to_insert.append((st_id, comp_name or "TCS", pkg_lpa))

        if (i + 1) % 500 == 0:
            print(f"  Ingested {i + 1} / {len(student_records)} students...")

    print(f"Recorded {len(offers_to_insert)} placement offers...")
    for st_id, comp, ctc in offers_to_insert:
        await conn.execute("""
            INSERT INTO placement_offers (student_id, company_name, ctc_lpa, status, is_on_campus)
            VALUES ($1, $2, $3, 'accepted', true);
        """, st_id, comp, ctc)

    await conn.close()
    print("Database seeding completed successfully!")

if __name__ == "__main__":
    asyncio.run(seed())
