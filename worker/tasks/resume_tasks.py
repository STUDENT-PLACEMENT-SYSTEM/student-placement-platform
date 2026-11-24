import logging
from typing import Optional, Dict, Any
from workflows.resume_parser_graph import resume_parser_graph, ResumeParserState

logger = logging.getLogger(__name__)


async def process_resume_task(
    ctx_or_student_id: Any = None,
    student_id_or_s3_key: Optional[str] = None,
    s3_key: Optional[str] = None,
    student_id: Optional[str] = None,
    raw_pdf_bytes: Optional[bytes] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Entrypoint task to execute the LangGraph Resume Parsing state machine.
    Compatible with:
      - ARQ worker call: process_resume_task(ctx, student_id, s3_key)
      - Direct positional: process_resume_task(student_id, s3_key)
      - Direct keyword: process_resume_task(student_id=..., s3_key=...)
    """
    # Resolve student_id and s3_key across calling conventions
    actual_student_id = student_id
    actual_s3_key = s3_key or ""

    if actual_student_id is None:
        if isinstance(ctx_or_student_id, dict) or hasattr(ctx_or_student_id, "redis"):
            # ARQ context passed first
            actual_student_id = student_id_or_s3_key
        else:
            # student_id passed as first argument
            actual_student_id = ctx_or_student_id
            if student_id_or_s3_key and not actual_s3_key:
                actual_s3_key = student_id_or_s3_key

    logger.info(f"Starting resume processing task: student_id={actual_student_id}, s3_key={actual_s3_key}")

    initial_state: ResumeParserState = {
        "s3_key": actual_s3_key or "",
        "student_id": str(actual_student_id or ""),
        "raw_pdf_bytes": raw_pdf_bytes,
        "raw_text": "",
        "parsed_data": None,
        "validation_errors": [],
        "embeddings": None,
        "success": False
    }

    try:
        final_state = await resume_parser_graph.ainvoke(initial_state)
        logger.info(f"Resume parsing completed for student_id={actual_student_id}, success={final_state.get('success')}")
        return {
            "student_id": actual_student_id,
            "success": final_state.get("success", False),
            "parsed_data": final_state.get("parsed_data"),
            "validation_errors": final_state.get("validation_errors", []),
            "has_embeddings": bool(final_state.get("embeddings"))
        }
    except Exception as e:
        logger.error(f"Error executing resume parser graph for student {actual_student_id}: {e}", exc_info=True)
        return {
            "student_id": actual_student_id,
            "success": False,
            "error": str(e),
            "validation_errors": [str(e)]
        }
