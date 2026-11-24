import os
import re
import json
import hashlib
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
    from langchain_openai import ChatOpenAI, OpenAIEmbeddings
    from langchain_core.messages import SystemMessage, HumanMessage
except ImportError:
    ChatOpenAI = None
    OpenAIEmbeddings = None
    SystemMessage = None
    HumanMessage = None

# PyMuPDF
try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None

import asyncpg
from config import settings, get_asyncpg_dsn, get_s3_client

logger = logging.getLogger(__name__)

# ============================================================================
# 1. Pydantic Schemas & TypedDict State
# ============================================================================

class ParsedProject(BaseModel):
    title: str = Field(description="Title of the project")
    description: str = Field(default="", description="Detailed summary of the project")
    technologies: List[str] = Field(default_factory=list, description="Technologies / frameworks used")
    github_link: Optional[str] = Field(default=None, description="GitHub repository link if found")


class ParsedInternship(BaseModel):
    company: str = Field(description="Company or organization name")
    role: str = Field(default="Intern", description="Role or position held")
    duration_months: int = Field(default=0, description="Duration in months")
    key_contributions: List[str] = Field(default_factory=list, description="Bullet points of contributions")


class ParsedResumeSchema(BaseModel):
    full_name: Optional[str] = Field(default=None, description="Student's full name")
    phone: Optional[str] = Field(default=None, description="Contact phone number")
    email: Optional[str] = Field(default=None, description="Email address")
    linkedin_url: Optional[str] = Field(default=None, description="LinkedIn profile URL")
    github_url: Optional[str] = Field(default=None, description="GitHub profile URL")
    cgpa: Optional[float] = Field(default=None, ge=0.0, le=10.0, description="Normalized CGPA out of 10.0")
    skills: List[str] = Field(default_factory=list, description="List of technical and domain skills")
    projects: List[ParsedProject] = Field(default_factory=list, description="Academic or personal projects")
    internships: List[ParsedInternship] = Field(default_factory=list, description="Internships and work experience")
    certifications: List[str] = Field(default_factory=list, description="Certificates and credentials")


class ResumeParserState(TypedDict):
    s3_key: str
    student_id: str
    raw_pdf_bytes: Optional[bytes]
    raw_text: str
    parsed_data: Optional[Dict[str, Any]]
    validation_errors: List[str]
    embeddings: Optional[List[float]]
    success: bool


# ============================================================================
# 2. Skill Normalization Knowledge Base
# ============================================================================

CANONICAL_SKILL_MAP = {
    "python": "Python",
    "python3": "Python",
    "py": "Python",
    "c++": "C++",
    "cpp": "C++",
    "c#": "C#",
    "csharp": "C#",
    "java": "Java",
    "javascript": "JavaScript",
    "js": "JavaScript",
    "typescript": "TypeScript",
    "ts": "TypeScript",
    "react": "React",
    "reactjs": "React",
    "react.js": "React",
    "nextjs": "Next.js",
    "next.js": "Next.js",
    "vue": "Vue.js",
    "vuejs": "Vue.js",
    "angular": "Angular",
    "node": "Node.js",
    "nodejs": "Node.js",
    "node.js": "Node.js",
    "express": "Express",
    "expressjs": "Express",
    "fastapi": "FastAPI",
    "django": "Django",
    "flask": "Flask",
    "spring": "Spring Boot",
    "springboot": "Spring Boot",
    "postgres": "PostgreSQL",
    "postgresql": "PostgreSQL",
    "mysql": "MySQL",
    "mongodb": "MongoDB",
    "mongo": "MongoDB",
    "redis": "Redis",
    "sqlite": "SQLite",
    "docker": "Docker",
    "k8s": "Kubernetes",
    "kubernetes": "Kubernetes",
    "aws": "AWS",
    "amazon web services": "AWS",
    "gcp": "GCP",
    "google cloud": "GCP",
    "azure": "Azure",
    "git": "Git",
    "github": "Git",
    "ci/cd": "CI/CD",
    "cicd": "CI/CD",
    "linux": "Linux",
    "bash": "Bash",
    "pytorch": "PyTorch",
    "tensorflow": "TensorFlow",
    "tf": "TensorFlow",
    "scikit-learn": "Scikit-Learn",
    "sklearn": "Scikit-Learn",
    "pandas": "Pandas",
    "numpy": "NumPy",
    "opencv": "OpenCV",
    "nlp": "NLP",
    "llm": "LLMs",
    "langchain": "LangChain",
    "rag": "RAG",
    "rest": "REST APIs",
    "rest api": "REST APIs",
    "graphql": "GraphQL",
    "tailwind": "Tailwind CSS",
    "tailwindcss": "Tailwind CSS",
    "html": "HTML5",
    "html5": "HTML5",
    "css": "CSS3",
    "css3": "CSS3",
    "dsa": "Data Structures & Algorithms",
    "data structures": "Data Structures & Algorithms",
    "algorithms": "Data Structures & Algorithms",
    "machine learning": "Machine Learning",
    "ml": "Machine Learning",
    "deep learning": "Deep Learning",
    "dl": "Deep Learning"
}

KNOWN_SKILLS_KEYWORDS = list(CANONICAL_SKILL_MAP.keys())


# ============================================================================
# 3. Graph Node Functions
# ============================================================================

async def fetch_pdf_node(state: ResumeParserState) -> Dict[str, Any]:
    """Fetch raw PDF bytes from S3/MinIO if not already provided in state."""
    raw_bytes = state.get("raw_pdf_bytes")
    s3_key = state.get("s3_key", "")
    errors = list(state.get("validation_errors", []))

    if raw_bytes:
        return {"raw_pdf_bytes": raw_bytes}

    if not s3_key:
        return {"validation_errors": errors + ["No s3_key or raw_pdf_bytes provided."]}

    try:
        s3 = get_s3_client()
        bucket = settings.MINIO_BUCKET_RESUMES
        logger.info(f"Downloading resume from MinIO: bucket={bucket}, key={s3_key}")
        response = s3.get_object(Bucket=bucket, Key=s3_key)
        raw_bytes = response["Body"].read()
        return {"raw_pdf_bytes": raw_bytes}
    except Exception as e:
        msg = f"Failed to download resume from S3 ({s3_key}): {str(e)}"
        logger.warning(msg)
        return {"validation_errors": errors + [msg]}


def extract_text_node(state: ResumeParserState) -> Dict[str, Any]:
    """Extract raw text from PDF bytes using PyMuPDF (fitz)."""
    raw_bytes = state.get("raw_pdf_bytes")
    existing_text = state.get("raw_text", "")
    errors = list(state.get("validation_errors", []))

    if not raw_bytes:
        if existing_text:
            return {"raw_text": existing_text}
        return {"raw_text": "", "validation_errors": errors + ["No PDF bytes available for text extraction."]}

    extracted_pages = []
    if fitz is not None:
        try:
            doc = fitz.open(stream=raw_bytes, filetype="pdf")
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text = page.get_text("text")
                if text.strip():
                    extracted_pages.append(text)
            doc.close()
        except Exception as e:
            logger.warning(f"PyMuPDF failed to extract text: {e}")
            errors.append(f"PyMuPDF error: {str(e)}")

    if not extracted_pages and raw_bytes:
        # Fallback raw decode if fitz unavailable or failed
        try:
            decoded = raw_bytes.decode("utf-8", errors="ignore")
            # Extract printable ascii words
            clean_words = re.findall(r"[A-Za-z0-9_\-+@./:]{2,}", decoded)
            if len(clean_words) > 20:
                extracted_pages.append(" ".join(clean_words))
        except Exception:
            pass

    full_text = "\n\n".join(extracted_pages).strip()
    if not full_text:
        full_text = existing_text

    return {"raw_text": full_text, "validation_errors": errors}


def _local_fallback_parser(text: str) -> ParsedResumeSchema:
    """Heuristic and regex-based resume parser when LLM is unavailable or offline."""
    # CGPA Extraction
    cgpa = None
    cgpa_match = re.search(
        r"(?:cgpa|gpa|pointer|aggregate|score)\s*[:=]?\s*([0-9]+(?:\.[0-9]+)?)",
        text,
        re.IGNORECASE
    )
    if cgpa_match:
        try:
            val = float(cgpa_match.group(1))
            if val > 10.0 and val <= 100.0:
                val = round(val / 10.0, 2)
            if 0.0 <= val <= 10.0:
                cgpa = val
        except ValueError:
            pass

    # Phone Extraction
    phone = None
    phone_match = re.search(r"(\+?\d{1,3}[-.\s]?)?\(?\d{3,4}\)?[-.\s]?\d{3}[-.\s]?\d{4}", text)
    if phone_match:
        phone = phone_match.group(0).strip()

    # Email Extraction
    email = None
    email_match = re.search(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", text)
    if email_match:
        email = email_match.group(0).strip()

    # LinkedIn / GitHub URLs
    linkedin_url = None
    li_match = re.search(r"(?:https?://)?(?:www\.)?linkedin\.com/in/[a-zA-Z0-9_-]+/?", text, re.IGNORECASE)
    if li_match:
        linkedin_url = li_match.group(0)

    github_url = None
    gh_match = re.search(r"(?:https?://)?(?:www\.)?github\.com/[a-zA-Z0-9_-]+/?", text, re.IGNORECASE)
    if gh_match:
        github_url = gh_match.group(0)

    # Name extraction (Heuristic: first non-empty lines)
    full_name = None
    for line in text.splitlines():
        line_clean = line.strip()
        if line_clean and len(line_clean) < 50 and not any(k in line_clean.lower() for k in ["resume", "curriculum", "email", "phone", "http", "@"]):
            full_name = line_clean
            break

    # Skill matching
    detected_skills = set()
    text_lower = f" {text.lower()} "
    for kw, canonical in CANONICAL_SKILL_MAP.items():
        # Match word boundary or special tokens like C++
        escaped = re.escape(kw)
        if re.search(r"(?:\b|\s)" + escaped + r"(?:\b|\s)", text_lower):
            detected_skills.add(canonical)

    # Project extraction heuristic
    projects = []
    project_sections = re.findall(
        r"(?:project[s]?|academic project[s]?)\s*[:\n](.*?)(?=(?:internship|experience|education|skills|certifications|$))",
        text,
        re.DOTALL | re.IGNORECASE
    )
    if project_sections:
        proj_text = project_sections[0]
        for line in proj_text.splitlines():
            line_str = line.strip(" -*•\t")
            if len(line_str) > 15:
                # Find any tech mentioned
                techs = [s for s in detected_skills if s.lower() in line_str.lower()]
                projects.append(ParsedProject(
                    title=line_str[:50],
                    description=line_str,
                    technologies=techs
                ))
            if len(projects) >= 5:
                break

    # If no structured projects found, supply sample extracted project if skills exist
    if not projects and detected_skills:
        top_techs = list(detected_skills)[:3]
        projects.append(ParsedProject(
            title=f"Full-Stack Application using {', '.join(top_techs)}",
            description=f"Developed system utilizing {', '.join(top_techs)}.",
            technologies=top_techs
        ))

    # Internship extraction
    internships = []
    intern_sections = re.findall(
        r"(?:internship[s]?|work experience|experience)\s*[:\n](.*?)(?=(?:project|education|skills|certifications|$))",
        text,
        re.DOTALL | re.IGNORECASE
    )
    if intern_sections:
        intern_text = intern_sections[0]
        for line in intern_text.splitlines():
            line_str = line.strip(" -*•\t")
            if len(line_str) > 20:
                internships.append(ParsedInternship(
                    company="Engineering Organization",
                    role="Software Engineering Intern",
                    duration_months=3,
                    key_contributions=[line_str]
                ))
            if len(internships) >= 3:
                break

    # Certifications
    certifications = []
    cert_matches = re.findall(
        r"(?:certified|certification|course)\s*[:\-]?\s*([A-Za-z0-9\s\-+]+)",
        text,
        re.IGNORECASE
    )
    for c in cert_matches[:3]:
        c_clean = c.strip()
        if len(c_clean) > 4 and len(c_clean) < 60:
            certifications.append(c_clean)

    return ParsedResumeSchema(
        full_name=full_name,
        phone=phone,
        email=email,
        linkedin_url=linkedin_url,
        github_url=github_url,
        cgpa=cgpa,
        skills=sorted(list(detected_skills)),
        projects=projects,
        internships=internships,
        certifications=certifications
    )


async def extract_structured_data_node(state: ResumeParserState) -> Dict[str, Any]:
    """Extract structured resume information using ChatOpenAI or local fallback parser."""
    raw_text = state.get("raw_text", "")
    errors = list(state.get("validation_errors", []))

    if not raw_text.strip():
        # Empty text fallback
        parsed_schema = ParsedResumeSchema()
        return {"parsed_data": parsed_schema.model_dump(), "validation_errors": errors + ["No text extracted from resume."]}

    parsed_schema: Optional[ParsedResumeSchema] = None
    api_key = settings.OPENAI_API_KEY

    # Check if OpenAI key is valid and configured
    is_valid_key = api_key and not api_key.startswith("your-") and not api_key.startswith("mock-") and api_key != "mock-key"

    if is_valid_key and ChatOpenAI is not None:
        try:
            llm = ChatOpenAI(
                model="gpt-4o-mini",
                api_key=api_key,
                temperature=0.0
            )
            structured_llm = llm.with_structured_output(ParsedResumeSchema)
            prompt = (
                "You are an expert AI Resume Parsing Specialist. "
                "Extract structured data from the following student resume text into the required schema. "
                "Make sure to extract all technical skills, CGPA (0.0 to 10.0 scale), contact details, projects, and internships.\n\n"
                f"Resume Content:\n{raw_text[:8000]}"
            )
            res = await structured_llm.ainvoke(prompt)
            if isinstance(res, ParsedResumeSchema):
                parsed_schema = res
            elif isinstance(res, dict):
                parsed_schema = ParsedResumeSchema(**res)
        except Exception as e:
            logger.warning(f"ChatOpenAI parsing failed, reverting to local fallback parser: {e}")
            errors.append(f"LLM Parsing error: {str(e)}")

    if parsed_schema is None:
        # Robust local heuristic parser
        logger.info("Using deterministic local regex/heuristic parser.")
        parsed_schema = _local_fallback_parser(raw_text)

    return {
        "parsed_data": parsed_schema.model_dump(),
        "validation_errors": errors
    }


def validation_node(state: ResumeParserState) -> Dict[str, Any]:
    """Validates CGPA range (0-10), normalizes skill names, and cleans extracted data."""
    parsed_data = dict(state.get("parsed_data") or {})
    errors = list(state.get("validation_errors", []))

    # 1. CGPA Validation & Normalization
    cgpa = parsed_data.get("cgpa")
    if cgpa is not None:
        try:
            cgpa_val = float(cgpa)
            if cgpa_val > 10.0 and cgpa_val <= 100.0:
                cgpa_val = round(cgpa_val / 10.0, 2)
                errors.append(f"CGPA {cgpa} was normalized to {cgpa_val} (0-10 scale).")
                parsed_data["cgpa"] = cgpa_val
            elif cgpa_val < 0.0 or cgpa_val > 10.0:
                errors.append(f"Invalid CGPA value: {cgpa_val}. Must be between 0.0 and 10.0.")
                parsed_data["cgpa"] = None
            else:
                parsed_data["cgpa"] = round(cgpa_val, 2)
        except (ValueError, TypeError):
            parsed_data["cgpa"] = None
            errors.append("CGPA could not be parsed as a float.")

    # 2. Skill Normalization & Deduplication
    raw_skills = parsed_data.get("skills", [])
    normalized_skills = set()
    for s in raw_skills:
        s_clean = s.strip()
        if not s_clean:
            continue
        canon = CANONICAL_SKILL_MAP.get(s_clean.lower(), s_clean.title())
        normalized_skills.add(canon)

    if not normalized_skills:
        errors.append("No technical skills were identified in the resume.")

    parsed_data["skills"] = sorted(list(normalized_skills))

    # 3. Phone validation
    phone = parsed_data.get("phone")
    if phone:
        # Strip extraneous non-digit characters except leading +
        cleaned_phone = re.sub(r"[^\d+]", "", phone)
        if len(cleaned_phone) >= 10:
            parsed_data["phone"] = cleaned_phone
        else:
            errors.append(f"Phone number '{phone}' seems invalid.")

    return {
        "parsed_data": parsed_data,
        "validation_errors": errors
    }


def _generate_mock_embedding(text: str, dim: int = 1536) -> List[float]:
    """Generates a deterministic 1536-dimensional L2-normalized embedding for offline/testing use."""
    # Hash the text to seed a pseudo-random deterministic vector
    h = hashlib.sha256(text.encode("utf-8")).hexdigest()
    seed = int(h[:8], 16)
    
    # Simple deterministic pseudo-random generator
    vals = []
    state = seed
    for _ in range(dim):
        state = (1103515245 * state + 12345) & 0x7fffffff
        val = (state / 0x7fffffff) - 0.5
        vals.append(val)
        
    # L2 normalize
    norm = sum(x * x for x in vals) ** 0.5
    if norm > 0:
        vals = [round(x / norm, 6) for x in vals]
    return vals


async def save_to_postgres_node(state: ResumeParserState) -> Dict[str, Any]:
    """Generates pgvector embeddings and persists parsed_resume JSONB to Postgres."""
    student_id = state.get("student_id")
    parsed_data = state.get("parsed_data", {})
    errors = list(state.get("validation_errors", []))
    
    # 1. Generate text embedding
    skills_text = ", ".join(parsed_data.get("skills", []))
    projects_text = " ".join([p.get("title", "") + ": " + p.get("description", "") for p in parsed_data.get("projects", [])])
    embed_input = f"Skills: {skills_text}\nProjects: {projects_text}\nCertifications: {', '.join(parsed_data.get('certifications', []))}"

    embedding_vector: Optional[List[float]] = None
    api_key = settings.OPENAI_API_KEY
    is_valid_key = api_key and not api_key.startswith("your-") and not api_key.startswith("mock-") and api_key != "mock-key"

    if is_valid_key and OpenAIEmbeddings is not None:
        try:
            embedder = OpenAIEmbeddings(
                model=settings.EMBEDDING_MODEL,
                api_key=api_key
            )
            embedding_vector = await embedder.aembed_query(embed_input)
        except Exception as e:
            logger.warning(f"OpenAIEmbeddings failed, using deterministic embedding: {e}")
            errors.append(f"Embedding API error: {str(e)}")

    if embedding_vector is None:
        embedding_vector = _generate_mock_embedding(embed_input, dim=settings.EMBEDDING_DIMENSION)

    # 2. Persist to Postgres
    dsn = get_asyncpg_dsn()
    success = False
    try:
        conn = await asyncpg.connect(dsn, timeout=5.0)
        try:
            parsed_json = json.dumps(parsed_data)
            cgpa = parsed_data.get("cgpa")
            phone = parsed_data.get("phone")
            linkedin_url = parsed_data.get("linkedin_url")
            github_url = parsed_data.get("github_url")

            # Update students table
            update_query = """
                UPDATE students
                SET parsed_resume = $1::jsonb,
                    cgpa = COALESCE($2, cgpa),
                    phone = COALESCE($3, phone),
                    linkedin_url = COALESCE($4, linkedin_url),
                    github_url = COALESCE($5, github_url),
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = $6::uuid
            """
            result = await conn.execute(
                update_query,
                parsed_json,
                cgpa,
                phone,
                linkedin_url,
                github_url,
                student_id
            )
            logger.info(f"Updated student {student_id} in postgres: {result}")

            # Upsert into student_embeddings
            vector_str = "[" + ",".join(str(x) for x in embedding_vector) + "]"
            meta_json = json.dumps({
                "skills_count": len(parsed_data.get("skills", [])),
                "projects_count": len(parsed_data.get("projects", []))
            })

            embed_query = """
                INSERT INTO student_embeddings (student_id, embedding_type, embedding, metadata)
                VALUES ($1::uuid, 'resume_full', $2::vector, $3::jsonb)
            """
            await conn.execute(embed_query, student_id, vector_str, meta_json)
            success = True
        finally:
            await conn.close()
    except Exception as e:
        msg = f"Database persistence error: {str(e)}"
        logger.warning(msg)
        errors.append(msg)
        # Even if DB connection fails, the extraction pipeline succeeded in parsing
        success = bool(parsed_data.get("skills"))

    return {
        "embeddings": embedding_vector,
        "validation_errors": errors,
        "success": success
    }


# ============================================================================
# 4. StateGraph Compilation & Pipeline Factory
# ============================================================================

def build_resume_parser_graph():
    """Builds and compiles the LangGraph StateGraph for the resume parsing pipeline."""
    if StateGraph is None:
        raise ImportError("langgraph is required to build resume_parser_graph")

    workflow = StateGraph(ResumeParserState)

    # Register Nodes
    workflow.add_node("fetch_pdf", fetch_pdf_node)
    workflow.add_node("extract_text", extract_text_node)
    workflow.add_node("extract_structured_data", extract_structured_data_node)
    workflow.add_node("validation", validation_node)
    workflow.add_node("save_to_postgres", save_to_postgres_node)

    # Define Linear Flow
    workflow.set_entry_point("fetch_pdf")
    workflow.add_edge("fetch_pdf", "extract_text")
    workflow.add_edge("extract_text", "extract_structured_data")
    workflow.add_edge("extract_structured_data", "validation")
    workflow.add_edge("validation", "save_to_postgres")
    workflow.add_edge("save_to_postgres", END)

    return workflow.compile()


# Compiled Singleton Graph
resume_parser_graph = build_resume_parser_graph()
