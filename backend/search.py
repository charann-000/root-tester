import os
from typing import Optional, List, Dict
from duckduckgo_search import DDGS
from config import get_settings

settings = get_settings()

async def search_cve(cve_id: str, max_results: int = 5) -> List[Dict[str, str]]:
    try:
        ddgs = DDGS()
        results = ddgs.text(f"{cve_id} exploit mitigation patch fix 2024", max_results=max_results)
        return [
            {"title": r["title"], "body": r["body"], "href": r["href"]}
            for r in results
        ]
    except Exception as e:
        return [{"error": str(e)}]

async def search_tool(tool: str, query: str, max_results: int = 5) -> List[Dict[str, str]]:
    try:
        ddgs = DDGS()
        results = ddgs.text(f"{tool} {query}", max_results=max_results)
        return [
            {"title": r["title"], "body": r["body"], "href": r["href"]}
            for r in results
        ]
    except Exception as e:
        return [{"error": str(e)}]

async def enrich_cve_with_search(cve_ids: List[str]) -> Dict[str, List[Dict[str, str]]]:
    enriched = {}
    for cve_id in cve_ids:
        results = await search_cve(cve_id)
        enriched[cve_id] = results
    return enriched

async def get_cve_details(cve_id: str) -> Optional[Dict[str, str]]:
    results = await search_cve(cve_id, max_results=3)
    if results and "error" not in results[0]:
        return results[0]
    return None