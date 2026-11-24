import os
import re
import json
import logging
from typing import TypedDict, Optional, List, Dict, Any

from pydantic import BaseModel, Field

# LangGraph imports
try:
    from langgraph.graph import StateGraph, END
except ImportError:
    StateGraph = None
    END = None

# LangChain OpenAI
try:
    from langchain_openai import ChatOpenAI
    from langchain_core.messages import SystemMessage, HumanMessage
except ImportError:
    ChatOpenAI = None
    SystemMessage = None
    HumanMessage = None

import asyncpg
from config import settings, get_asyncpg_dsn
from workflows.resume_parser_graph import CANONICAL_SKILL_MAP

logger = logging.getLogger(__name__)

# ============================================================================
# 1. State Definition
# ============================================================================

class SkillGapState(TypedDict):
    student_id: str
    target_drive_id: Optional[str]
    target_role: str
    student_skills: List[str]
    target_jd_text: str
    missing_skills: List[str]
    recommended_projects: List[Dict[str, Any]]
    roadmap_weeks: List[Dict[str, Any]]
    success: bool
    error: Optional[str]


# ============================================================================
# 2. Heuristic Skill & Curriculum Knowledge
# ============================================================================

ROLE_CORE_SKILLS: Dict[str, List[str]] = {
    "software engineer": ["Data Structures & Algorithms", "Python", "Java", "PostgreSQL", "Git", "REST APIs", "Docker"],
    "frontend developer": ["JavaScript", "TypeScript", "React", "Next.js", "Tailwind CSS", "HTML5", "CSS3", "Git"],
    "backend developer": ["Python", "FastAPI", "Node.js", "PostgreSQL", "Redis", "Docker", "REST APIs", "Git"],
    "full stack developer": ["React", "TypeScript", "Node.js", "PostgreSQL", "Docker", "Git", "REST APIs"],
    "data scientist": ["Python", "Machine Learning", "Pandas", "NumPy", "Scikit-Learn", "SQL", "Deep Learning"],
    "ai/ml engineer": ["Python", "PyTorch", "TensorFlow", "NLP", "LLMs", "RAG", "Docker", "FastAPI"],
    "devops engineer": ["Linux", "Docker", "Kubernetes", "AWS", "CI/CD", "Bash", "Git"]
}


# ============================================================================
# 3. Node Implementations
# ============================================================================

async def fetch_context_node(state: SkillGapState) -> Dict[str, Any]:
    """Fetch student's parsed skills and target drive details from PostgreSQL."""
    student_id = state.get("student_id")
    target_drive_id = state.get("target_drive_id")
    student_skills = list(state.get("student_skills", []))
    target_jd_text = state.get("target_jd_text", "")
    target_role = state.get("target_role", "")

    dsn = get_asyncpg_dsn()
    try:
        conn = await asyncpg.connect(dsn, timeout=5.0)
        try:
            # 1. Fetch student parsed skills if empty
            if not student_skills and student_id:
                row = await conn.fetchrow(
                    "SELECT parsed_resume FROM students WHERE id = $1::uuid",
                    student_id
                )
                if row and row["parsed_resume"]:
                    pr = row["parsed_resume"]
                    if isinstance(pr, str):
                        pr = json.loads(pr)
                    student_skills = pr.get("skills", [])

            # 2. Fetch drive details if target_drive_id provided
            if target_drive_id and (not target_jd_text or not target_role):
                d_row = await conn.fetchrow(
                    "SELECT title, role_name, job_description FROM drives WHERE id = $1::uuid",
                    target_drive_id
                )
                if d_row:
                    if not target_role:
                        target_role = d_row["role_name"] or d_row["title"]
                    if not target_jd_text:
                        target_jd_text = d_row["job_description"]
        finally:
            await conn.close()
    except Exception as e:
        logger.warning(f"Error fetching context from database: {e}")

    if not target_role:
        target_role = "Software Development Engineer"

    return {
        "student_skills": student_skills,
        "target_jd_text": target_jd_text,
        "target_role": target_role
    }


def difference_analyzer_node(state: SkillGapState) -> Dict[str, Any]:
    """Analyzes the delta between target JD requirements and current student skills."""
    target_role = state.get("target_role", "").lower()
    target_jd = state.get("target_jd_text", "").lower()
    student_skills = [s.strip().lower() for s in state.get("student_skills", [])]

    # Normalize existing student skills
    student_canonical = set()
    for s in student_skills:
        student_canonical.add(CANONICAL_SKILL_MAP.get(s, s.title()).lower())

    required_skills = set()

    # Match skills from JD text
    if target_jd:
        for kw, canonical in CANONICAL_SKILL_MAP.items():
            if re.search(r"(?:\b|\s)" + re.escape(kw) + r"(?:\b|\s)", target_jd):
                required_skills.add(canonical)

    # Match skills from target role defaults
    for role_key, skills in ROLE_CORE_SKILLS.items():
        if role_key in target_role:
            for sk in skills:
                required_skills.add(sk)
            break

    # If still empty, supply standard engineering baseline
    if not required_skills:
        required_skills = {"Data Structures & Algorithms", "Python", "SQL", "Git", "System Design", "REST APIs"}

    # Compute difference
    missing = []
    for req in required_skills:
        canon_req = CANONICAL_SKILL_MAP.get(req.lower(), req)
        if canon_req.lower() not in student_canonical:
            missing.append(canon_req)

    # If student already knows everything, recommend advanced placement topics
    if not missing:
        missing = ["System Design (HLD & LLD)", "Distributed Caching with Redis", "Advanced Concurrency", "Kubernetes & Microservices"]

    return {"missing_skills": sorted(missing)}


async def four_week_planner_node(state: SkillGapState) -> Dict[str, Any]:
    """Generates a structured 4-week sprint plan with focus, action items, and recommended projects."""
    missing_skills = state.get("missing_skills", [])
    target_role = state.get("target_role", "Software Engineer")
    student_skills = state.get("student_skills", [])

    api_key = settings.OPENAI_API_KEY
    is_valid_key = api_key and not api_key.startswith("your-") and not api_key.startswith("mock-") and api_key != "mock-key"

    weeks = None
    recommended_projects = []

    # LLM generation if available
    if is_valid_key and ChatOpenAI is not None:
        try:
            llm = ChatOpenAI(model="gpt-4o-mini", api_key=api_key, temperature=0.2)
            prompt = (
                f"You are a Senior Placement Director and Technical Architect.\n"
                f"Create a 4-week placement preparation sprint for a student targeting: '{target_role}'.\n"
                f"Student currently knows: {', '.join(student_skills) if student_skills else 'Basic CS fundamentals'}.\n"
                f"Missing skills to master: {', '.join(missing_skills)}.\n\n"
                f"Output strictly valid JSON with the format:\n"
                "{\n"
                '  "recommended_projects": [\n'
                '    {"title": "...", "description": "...", "tech_stack": ["..."], "deliverables": ["..."]}\n'
                "  ],\n"
                '  "roadmap_weeks": [\n'
                '    {\n'
                '      "week": 1,\n'
                '      "focus": "...",\n'
                '      "dsa_topics": ["..."],\n'
                '      "action_items": ["..."],\n'
                '      "resources": [{"name": "...", "url": "..."}]\n'
                "    }\n"
                "  ]\n"
                "}"
            )
            res = await llm.ainvoke(prompt)
            raw_text = res.content
            # Clean markdown codeblocks
            json_match = re.search(r"\{.*\}", raw_text, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group(0))
                weeks = data.get("roadmap_weeks")
                recommended_projects = data.get("recommended_projects", [])
        except Exception as e:
            logger.warning(f"LLM roadmap planner failed: {e}")

    # Deterministic fallback plan
    if not weeks:
        missing_top = missing_skills[:4] if missing_skills else ["Data Structures & Algorithms", "System Design", "SQL", "Docker"]
        skill_w1 = missing_top[0] if len(missing_top) > 0 else "Core Fundamentals"
        skill_w2 = missing_top[1] if len(missing_top) > 1 else "Frameworks & Tooling"
        skill_w3 = missing_top[2] if len(missing_top) > 2 else "Database & Architecture"
        skill_w4 = missing_top[3] if len(missing_top) > 3 else "System Design & Mock Tests"

        weeks = [
            {
                "week": 1,
                "focus": f"Foundation & Core Skill Gap: {skill_w1}",
                "dsa_topics": ["Arrays", "Two Pointers", "Hashing", "Binary Search"],
                "action_items": [
                    f"Complete 15 LeetCode Medium problems on {skill_w1} patterns",
                    f"Read official documentation and set up local development environment for {skill_w1}",
                    "Write modular unit tests covering core syntax and exception handling"
                ],
                "resources": [
                    {"name": "NeetCode 150 Core Roadmap", "url": "https://neetcode.io/roadmap"},
                    {"name": f"{skill_w1} Official Documentation", "url": f"https://devdocs.io"}
                ]
            },
            {
                "week": 2,
                "focus": f"Applied Engineering & Tooling: {skill_w2}",
                "dsa_topics": ["Trees & Graphs", "Breadth-First Search", "Depth-First Search"],
                "action_items": [
                    f"Implement 3 micro-features using {skill_w2}",
                    "Integrate API endpoints with structured request/response validation",
                    "Solve 10 Graph & Tree problems on LeetCode"
                ],
                "resources": [
                    {"name": f"Mastering {skill_w2} in Production", "url": "https://github.com"},
                    {"name": "Graph Traversal Patterns Guide", "url": "https://leetcode.com"}
                ]
            },
            {
                "week": 3,
                "focus": f"Production Architecture & Blueprint: {skill_w3}",
                "dsa_topics": ["Dynamic Programming", "Heap / Priority Queue", "Greedy Algorithms"],
                "action_items": [
                    f"Architect full end-to-end project incorporating {', '.join(missing_top[:3])}",
                    "Configure database schema, indices, and connection pooling",
                    "Dockerize services and write docker-compose manifest"
                ],
                "resources": [
                    {"name": "System Design Primer", "url": "https://github.com/donnemartin/system-design-primer"},
                    {"name": "Docker & Container Best Practices", "url": "https://docs.docker.com"}
                ]
            },
            {
                "week": 4,
                "focus": f"Placement Readiness, Mock Interviews & Polish: {skill_w4}",
                "dsa_topics": ["System Design (HLD/LLD)", "Sliding Window", "Concurrency"],
                "action_items": [
                    f"Conduct 2 peer mock interviews focusing on {target_role} questions",
                    "Deploy project to cloud or public hosting with live demo link and README",
                    "Review Top-50 Behavioral questions (STAR method) and resume walk-through"
                ],
                "resources": [
                    {"name": "Tech Interview Handbook", "url": "https://techinterviewhandbook.org"},
                    {"name": "STAR Interview Method Template", "url": "https://www.thebalancecareers.com"}
                ]
            }
        ]

        recommended_projects = [
            {
                "title": f"High-Performance {target_role} Portfolio Project",
                "description": f"Full-stack microservices application demonstrating proficiency in {', '.join(missing_skills[:3])}.",
                "tech_stack": missing_skills[:4],
                "deliverables": [
                    "REST / GraphQL APIs with authentication",
                    "Containerized development environment with Docker",
                    "Automated GitHub Actions CI pipeline"
                ]
            }
        ]

    return {
        "roadmap_weeks": weeks,
        "recommended_projects": recommended_projects
    }


async def save_roadmap_node(state: SkillGapState) -> Dict[str, Any]:
    """Persists the generated skill-gap roadmap to skill_gap_roadmaps in PostgreSQL."""
    student_id = state.get("student_id")
    target_drive_id = state.get("target_drive_id")
    target_role = state.get("target_role", "Software Engineer")
    missing_skills = state.get("missing_skills", [])
    recommended_projects = state.get("recommended_projects", [])
    roadmap_weeks = state.get("roadmap_weeks", [])

    dsn = get_asyncpg_dsn()
    success = False
    error = None

    try:
        conn = await asyncpg.connect(dsn, timeout=5.0)
        try:
            query = """
                INSERT INTO skill_gap_roadmaps (
                    student_id, target_drive_id, target_role,
                    missing_skills, recommended_projects, weekly_roadmap
                )
                VALUES ($1::uuid, $2, $3, $4, $5::jsonb, $6::jsonb)
            """
            drive_uuid = target_drive_id if target_drive_id else None
            await conn.execute(
                query,
                student_id,
                drive_uuid,
                target_role,
                missing_skills,
                json.dumps(recommended_projects),
                json.dumps(roadmap_weeks)
            )
            success = True
            logger.info(f"Saved skill gap roadmap for student {student_id}")
        finally:
            await conn.close()
    except Exception as e:
        msg = f"Failed to persist roadmap to postgres: {str(e)}"
        logger.warning(msg)
        error = msg
        # If DB connection fails, roadmap generation was still successful in-memory
        success = True

    return {
        "success": success,
        "error": error
    }


# ============================================================================
# 4. StateGraph Compilation & Pipeline Factory
# ============================================================================

def build_skill_gap_graph():
    """Builds and compiles the LangGraph StateGraph for the Skill-Gap Agent."""
    if StateGraph is None:
        raise ImportError("langgraph is required to build skill_gap_graph")

    workflow = StateGraph(SkillGapState)

    # Register Nodes
    workflow.add_node("fetch_context", fetch_context_node)
    workflow.add_node("difference_analyzer", difference_analyzer_node)
    workflow.add_node("four_week_planner", four_week_planner_node)
    workflow.add_node("save_roadmap", save_roadmap_node)

    # Define Linear Flow
    workflow.set_entry_point("fetch_context")
    workflow.add_edge("fetch_context", "difference_analyzer")
    workflow.add_edge("difference_analyzer", "four_week_planner")
    workflow.add_edge("four_week_planner", "save_roadmap")
    workflow.add_edge("save_roadmap", END)

    return workflow.compile()


# Compiled Singleton Graph
skill_gap_graph = build_skill_gap_graph()
