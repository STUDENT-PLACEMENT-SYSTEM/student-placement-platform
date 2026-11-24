import os
import sys
import logging
from typing import List, Dict, Any, Optional
from fastmcp import FastMCP
from dotenv import load_dotenv

# Ensure local imports work cleanly
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tools.branch_stats import get_branch_placement_stats as _branch_stats
from tools.eligibility import find_eligible_students as _eligibility
from tools.high_cgpa_unplaced import get_unplaced_high_cgpa_students as _unplaced
from tools.company_summary import get_company_offer_summary as _company_summary

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("PlacementAnalyticsMCP")

# Create FastMCP server instance
mcp = FastMCP("PlacementAnalyticsMCP")


@mcp.tool(
    name="get_branch_placement_stats",
    description="Returns aggregate placement counts, percentages, and average CTC for a given engineering branch."
)
async def get_branch_placement_stats(branch: str) -> Dict[str, Any]:
    """
    Returns aggregate placement counts, percentages, and average CTC for a given engineering branch.

    Args:
        branch: Engineering branch name (e.g. 'Computer Science', 'Information Technology', 'ECE', 'ME', 'Civil', 'EE').
    """
    return await _branch_stats(branch)


@mcp.tool(
    name="find_eligible_students",
    description="Queries students meeting minimum CGPA, maximum backlogs, and specific required technical skills."
)
async def find_eligible_students(
    min_cgpa: float = 6.0,
    max_backlogs: int = 0,
    required_skills: Optional[List[str]] = None
) -> List[Dict[str, Any]]:
    """
    Queries students meeting minimum CGPA, maximum backlogs, and specific required technical skills.

    Args:
        min_cgpa: Minimum acceptable CGPA out of 10.0 (default 6.0).
        max_backlogs: Maximum allowed active backlogs (default 0).
        required_skills: Optional list of skill keywords (e.g. ['React', 'Docker']).
    """
    return await _eligibility(min_cgpa=min_cgpa, max_backlogs=max_backlogs, required_skills=required_skills)


@mcp.tool(
    name="get_unplaced_high_cgpa_students",
    description="Highlights students with CGPA above a specific threshold who remain unplaced, alerting TPO for targeted placement intervention."
)
async def get_unplaced_high_cgpa_students(threshold_cgpa: float = 8.0) -> List[Dict[str, Any]]:
    """
    Highlights students with CGPA above a specific threshold who remain unplaced.

    Args:
        threshold_cgpa: Minimum CGPA threshold to flag (default 8.0).
    """
    return await _unplaced(threshold_cgpa=threshold_cgpa)


@mcp.tool(
    name="get_company_offer_summary",
    description="Summarizes all offers made across companies during the current placement season, ordered by total recruits."
)
async def get_company_offer_summary() -> List[Dict[str, Any]]:
    """
    Summarizes all offers made across companies during the current placement season, ordered by total recruits.
    """
    return await _company_summary()


if __name__ == "__main__":
    host = os.getenv("MCP_SERVER_HOST", "0.0.0.0")
    port = int(os.getenv("MCP_SERVER_PORT", "8001"))
    transport = os.getenv("MCP_TRANSPORT", "http")

    logger.info(f"Starting PlacementAnalyticsMCP on {host}:{port} using {transport} transport...")
    mcp.run(transport=transport, host=host, port=port)
