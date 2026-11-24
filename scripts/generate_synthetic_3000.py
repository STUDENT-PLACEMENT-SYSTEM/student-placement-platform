#!/usr/bin/env python3
"""
Synthetic Dataset Generator for Student Placement Platform.
Generates 3,000 realistic Indian engineering student profiles with realistic correlations
between academic performance, skills, placement status, and CTC packages.
"""

import argparse
import json
import logging
import os
import random
import numpy as np
import pandas as pd
from faker import Faker

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

BRANCHES = ["CS", "IT", "ECE", "EE", "ME", "Civil"]
BRANCH_WEIGHTS = [0.28, 0.22, 0.20, 0.12, 0.10, 0.08]

BATCH_YEARS = [2025, 2026]

# Tech skills pool categorised
CORE_CS_IT_SKILLS = [
    "Python", "Java", "C++", "JavaScript", "TypeScript", "SQL", "HTML/CSS",
    "React", "Node.js", "FastAPI", "Spring Boot", "Express.js", "Django", "Next.js",
    "PostgreSQL", "MongoDB", "Redis", "MySQL",
    "Docker", "Kubernetes", "AWS", "Git", "Linux", "CI/CD",
    "Machine Learning", "PyTorch", "TensorFlow", "Pandas", "DSA"
]

ECE_EE_SKILLS = [
    "Embedded C", "C++", "Python", "MATLAB", "Verilog", "VHDL", "Arduino",
    "IoT", "Microcontrollers", "PCB Design", "Digital Signal Processing",
    "FPGA", "Linux", "SQL", "Git", "Simulink", "VLSI Design"
]

ME_CIVIL_SKILLS = [
    "AutoCAD", "SolidWorks", "ANSYS", "CATIA", "MATLAB", "Python",
    "Revit", "STAAD Pro", "ETABS", "GIS", "MS Project", "MS Excel",
    "Structural Analysis", "CNC Programming", "Thermodynamics Simulation", "SQL"
]

# Companies grouped by hiring tier
TIER_1_COMPANIES = [
    "Google", "Microsoft", "Amazon", "Adobe", "Goldman Sachs",
    "Flipkart", "Cisco", "Salesforce", "Uber", "Atlassian",
    "Oracle Cloud", "Directi", "Intuit", "Walmart Global Tech"
]

TIER_2_COMPANIES = [
    "Oracle", "Samsung R&D", "LTI Mindtree", "Barclays", "Morgan Stanley",
    "Deloitte", "ZS Associates", "Siemens", "Qualcomm", "Intel",
    "Schneider Electric", "Tata Motors", "Bosch", "Texas Instruments",
    "Persistent Systems", "Publicis Sapient", "Paytm"
]

TIER_3_COMPANIES = [
    "TCS", "Infosys", "Wipro", "Cognizant", "Accenture",
    "Capgemini", "HCLTech", "L&T Technology Services", "Hexaware",
    "Tech Mahindra", "DXC Technology", "KPIT Technologies"
]

COMMON_INDIAN_FIRST_NAMES_MALE = [
    "Aarav", "Aditya", "Amit", "Aniket", "Arjun", "Ayush", "Chirag", "Deepak",
    "Dhruv", "Gaurav", "Harsh", "Ishaan", "Kartik", "Kunal", "Manish", "Mayank",
    "Naveen", "Nikhil", "Pranav", "Prateek", "Rahul", "Rishi", "Rohan", "Rohit",
    "Sachin", "Saurabh", "Shivam", "Siddharth", "Tanmay", "Utkarsh", "Varun",
    "Vikas", "Vikram", "Vishal", "Yash"
]

COMMON_INDIAN_FIRST_NAMES_FEMALE = [
    "Aanya", "Aditi", "Ananya", "Anjali", "Anushka", "Avani", "Deepika", "Divya",
    "Isha", "Kavya", "Khushi", "Meera", "Neha", "Nisha", "Pallavi", "Pooja",
    "Prachi", "Priya", "Rhea", "Riddhi", "Riya", "Sakshi", "Samiksha", "Sanya",
    "Shreya", "Simran", "Sneha", "Tanvi", "Trisha", "Vaishnavi", "Vanshika"
]

COMMON_INDIAN_LAST_NAMES = [
    "Agarwal", "Bhatia", "Chauhan", "Deshmukh", "Dubey", "Gupta", "Iyer", "Jain",
    "Jha", "Joshi", "Kapoor", "Kaur", "Kulkarni", "Kumar", "Mishra", "Mukherjee",
    "Nair", "Pandey", "Patel", "Pillai", "Prasad", "Rao", "Reddy", "Roy", "Saha",
    "Saxena", "Sen", "Sharma", "Singh", "Soni", "Tiwari", "Varma", "Verma", "Yadav"
]


def generate_full_name(gender: str, fake: Faker) -> str:
    use_preset = random.random() < 0.65
    if use_preset:
        first = random.choice(COMMON_INDIAN_FIRST_NAMES_MALE if gender == "Male" else COMMON_INDIAN_FIRST_NAMES_FEMALE)
        last = random.choice(COMMON_INDIAN_LAST_NAMES)
        return f"{first} {last}"
    else:
        if gender == "Male":
            return f"{fake.first_name_male()} {fake.last_name()}"
        else:
            return f"{fake.first_name_female()} {fake.last_name()}"


def generate_skills(branch: str, coding_score: float, projects: int) -> list:
    """Generate realistic skills array based on branch, proficiency, and projects."""
    if branch in ["CS", "IT"]:
        pool = CORE_CS_IT_SKILLS
        base_skills = ["Python", "SQL", "Git"]
    elif branch in ["ECE", "EE"]:
        pool = ECE_EE_SKILLS
        base_skills = ["Embedded C", "MATLAB"]
    else:
        pool = ME_CIVIL_SKILLS
        base_skills = ["AutoCAD", "MS Excel"]

    # Number of skills scales with coding score and projects
    num_skills = min(max(3, int(2 + coding_score * 0.6 + projects * 0.5)), 9)
    available_pool = [s for s in pool if s not in base_skills]
    sampled = random.sample(available_pool, min(num_skills - len(base_skills), len(available_pool)))
    
    # If student is high coder in non-CS branch, add some modern tech
    if coding_score >= 7.0 and branch not in ["CS", "IT"]:
        if "Python" not in sampled and "Python" not in base_skills:
            sampled.append("Python")
        if random.random() < 0.6:
            sampled.append(random.choice(["React", "FastAPI", "Docker", "Machine Learning"]))

    skills = list(set(base_skills + sampled))
    random.shuffle(skills)
    return skills


def generate_dataset(num_records: int = 3000, seed: int = 42) -> pd.DataFrame:
    np.random.seed(seed)
    random.seed(seed)
    fake = Faker("en_IN")
    Faker.seed(seed)

    records = []
    branch_roll_counters = {b: {2025: 1, 2026: 1} for b in BRANCHES}

    logger.info("Generating %d student profiles...", num_records)

    for i in range(1, num_records + 1):
        student_id = i
        gender = "Male" if random.random() < 0.62 else "Female"
        branch = np.random.choice(BRANCHES, p=BRANCH_WEIGHTS)
        batch_year = np.random.choice(BATCH_YEARS, p=[0.5, 0.5])
        
        # Roll number format: e.g. 2021CS001 (batch 2025 -> admission 2021)
        admission_year = batch_year - 4
        counter = branch_roll_counters[branch][batch_year]
        branch_roll_counters[branch][batch_year] += 1
        roll_number = f"{admission_year}{branch}{counter:03d}"
        
        full_name = generate_full_name(gender, fake)

        # CGPA: bounded normal distribution (5.5 to 9.8)
        cgpa_raw = np.random.normal(loc=7.62, scale=0.92)
        cgpa = round(float(np.clip(cgpa_raw, 5.50, 9.80)), 2)

        # Backlogs: lower CGPA increases probability of active backlogs
        if cgpa < 6.5:
            backlog_probs = [0.25, 0.35, 0.22, 0.12, 0.06]
        elif cgpa < 7.5:
            backlog_probs = [0.65, 0.22, 0.08, 0.03, 0.02]
        elif cgpa < 8.5:
            backlog_probs = [0.88, 0.09, 0.02, 0.01, 0.00]
        else:
            backlog_probs = [0.97, 0.03, 0.00, 0.00, 0.00]
        backlogs = int(np.random.choice([0, 1, 2, 3, 4], p=backlog_probs))

        # History of backlogs >= active backlogs, bounded to max 6
        extra_cleared = int(np.random.choice([0, 1, 2, 3], p=[0.60, 0.25, 0.10, 0.05]))
        history_of_backlogs = min(backlogs + extra_cleared, 6)

        # Coding skills score (1-10): correlated with branch and CGPA
        branch_coding_bias = {
            "CS": 1.6, "IT": 1.4, "ECE": 0.2, "EE": -0.4, "ME": -0.8, "Civil": -1.1
        }[branch]
        coding_mean = 5.2 + branch_coding_bias + 0.9 * (cgpa - 7.5)
        coding_skills_score = round(float(np.clip(np.random.normal(coding_mean, 1.45), 1.0, 10.0)), 1)

        # Aptitude score (1-100): correlated with CGPA and coding
        apt_mean = 50.0 + 3.2 * cgpa + 1.8 * coding_skills_score
        aptitude_score = int(np.clip(np.random.normal(apt_mean, 8.5), 25, 100))

        # Communication score (1-10)
        comm_mean = 6.2 + 0.3 * (cgpa - 7.0)
        communication_score = round(float(np.clip(np.random.normal(comm_mean, 1.5), 1.0, 10.0)), 1)

        # Internships (0 to 3): higher for high CGPA, good coding, batch 2025
        internship_lambda = max(0.1, 0.35 + 0.45 * (cgpa - 7.0) + 0.25 * (coding_skills_score - 5.0))
        if backlogs > 0:
            internship_lambda *= 0.5
        internships = int(np.clip(np.random.poisson(internship_lambda), 0, 3))

        # Projects count (0 to 5)
        proj_mean = 1.8 + 0.25 * coding_skills_score + 0.3 * internships
        projects_count = int(np.clip(np.round(np.random.normal(proj_mean, 1.0)), 0, 5))

        # Certifications count (0 to 4)
        cert_mean = 1.2 + 0.18 * coding_skills_score + 0.2 * projects_count
        certifications_count = int(np.clip(np.round(np.random.normal(cert_mean, 0.9)), 0, 4))

        # Skills list (JSON array)
        skills = generate_skills(branch, coding_skills_score, projects_count)
        skills_list_json = json.dumps(skills)

        # Placement Probability Model (realistic campus placement dynamics)
        branch_placement_bias = {
            "CS": 0.55, "IT": 0.40, "ECE": 0.10, "EE": -0.15, "ME": -0.35, "Civil": -0.50
        }[branch]

        # Logit formula
        z = (
            0.45
            + 1.25 * (cgpa - 7.5)
            - 1.65 * backlogs
            - 0.30 * (history_of_backlogs - backlogs)
            + 0.70 * internships
            + 0.35 * (coding_skills_score - 5.5)
            + 0.22 * (communication_score - 5.5)
            + 0.035 * (aptitude_score - 65.0)
            + 0.20 * projects_count
            + 0.12 * certifications_count
            + branch_placement_bias
        )
        
        # Hard campus recruitment filters:
        if backlogs >= 2:
            z -= 2.0  # heavy penalty for multiple active backlogs
        if cgpa < 6.0:
            z -= 2.2  # cutoff for most campus drives

        prob = 1.0 / (1.0 + np.exp(-z))
        placed = 1 if np.random.rand() < prob else 0

        # CTC and Company allocation for placed students
        if placed == 1:
            # Probability of Tier 1 (Dream / Super Dream 18 - 45 LPA)
            # Requires strong coding skill, high CGPA, 0 active backlogs
            t1_logit = (
                -4.2
                + 0.95 * (coding_skills_score - 7.5)
                + 1.05 * (cgpa - 8.0)
                + 0.50 * internships
                + 0.04 * (aptitude_score - 70.0)
                + (0.4 if branch in ["CS", "IT"] else -0.3)
                - 3.0 * backlogs
            )
            prob_t1 = 1.0 / (1.0 + np.exp(-t1_logit)) if backlogs == 0 and cgpa >= 7.5 and coding_skills_score >= 6.5 else 0.0

            # Probability of Tier 2 (Product / FinTech / Core 8 - 18 LPA)
            t2_logit = (
                -1.1
                + 0.65 * (coding_skills_score - 6.0)
                + 0.75 * (cgpa - 7.2)
                + 0.35 * internships
                + 0.025 * (aptitude_score - 60.0)
                - 1.2 * backlogs
            )
            prob_t2 = 1.0 / (1.0 + np.exp(-t2_logit))

            roll_draw = np.random.rand()
            if roll_draw < prob_t1:
                # Tier 1 Dream Offer
                company_name = random.choice(TIER_1_COMPANIES)
                base_ctc = 18.0 + 3.2 * (coding_skills_score - 7.5) + 2.8 * (cgpa - 8.0) + np.random.normal(0, 3.5)
                package_lpa = round(float(np.clip(base_ctc, 18.0, 45.0)), 2)
            elif roll_draw < (prob_t1 + prob_t2):
                # Tier 2 Mid-Tier Offer
                company_name = random.choice(TIER_2_COMPANIES)
                base_ctc = 8.5 + 1.4 * (coding_skills_score - 6.0) + 1.2 * (cgpa - 7.2) + np.random.normal(0, 1.4)
                package_lpa = round(float(np.clip(base_ctc, 8.0, 17.8)), 2)
            else:
                # Tier 3 Mass Recruiter / Core Entry Offer
                company_name = random.choice(TIER_3_COMPANIES)
                base_ctc = 3.6 + 0.6 * (coding_skills_score - 4.5) + 0.4 * (cgpa - 6.5) + np.random.normal(0, 0.6)
                package_lpa = round(float(np.clip(base_ctc, 3.5, 7.8)), 2)
        else:
            company_name = None
            package_lpa = 0.0

        records.append({
            "student_id": student_id,
            "roll_number": roll_number,
            "full_name": full_name,
            "gender": gender,
            "branch": branch,
            "batch_year": batch_year,
            "cgpa": cgpa,
            "backlogs": backlogs,
            "history_of_backlogs": history_of_backlogs,
            "internships": internships,
            "projects_count": projects_count,
            "certifications_count": certifications_count,
            "coding_skills_score": coding_skills_score,
            "communication_score": communication_score,
            "aptitude_score": aptitude_score,
            "skills_list": skills_list_json,
            "placed": placed,
            "company_name": company_name,
            "package_lpa": package_lpa
        })

    df = pd.DataFrame(records)
    logger.info("Generated %d records successfully.", len(df))
    return df


def main():
    parser = argparse.ArgumentParser(description="Generate realistic synthetic placement dataset.")
    parser.add_argument(
        "--output",
        default="/home/kali/AIML_student_placement/dataset/synthetic_3000_students.csv",
        help="Target output CSV filepath."
    )
    parser.add_argument("--num-records", type=int, default=3000, help="Number of student records to generate.")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility.")
    args = parser.parse_args()

    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
    df = generate_dataset(num_records=args.num_records, seed=args.seed)

    df.to_csv(args.output, index=False)
    logger.info("Saved dataset to %s", args.output)

    # Print summary statistics
    print("\n--- SYNTHETIC DATASET SUMMARY ---")
    print(f"Total Records: {len(df)}")
    print(f"Overall Placement Rate: {df['placed'].mean():.2%}")
    print(f"Branch Breakdown:\n{df['branch'].value_counts()}")
    print("\nPlacement Rate by Branch:")
    print(df.groupby('branch')['placed'].mean().apply(lambda x: f"{x:.2%}"))
    print("\nPlacement Rate by Backlogs:")
    print(df.groupby('backlogs')['placed'].mean().apply(lambda x: f"{x:.2%}"))
    
    placed_df = df[df['placed'] == 1]
    print(f"\nPlaced Students CTC Stats (N={len(placed_df)}):")
    print(placed_df['package_lpa'].describe().round(2))
    print(f"\nTop Hiring Companies:\n{placed_df['company_name'].value_counts().head(10)}")


if __name__ == "__main__":
    main()
