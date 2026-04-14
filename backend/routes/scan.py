from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import json

from db import get_db, create_scan, get_scan, update_scan_status, save_vulnerability, save_fix, save_exploit, save_summary, get_user_scans, delete_scan, get_user_by_email
from auth_utils import get_current_user, validate_target
from tools import get_tools_for_preset, run_tool_by_name, TOOL_MAP, TOOL_TIMEOUTS

router = APIRouter(prefix="/api/scan", tags=["scan"])

class ScanStartRequest(BaseModel):
    target: str
    tools: Optional[List[str]] = None
    preset: str = "quick"
    auto_recon: bool = False
    has_accepted_disclaimer: int = 0

class ScanResponse(BaseModel):
    scan_id: int
    status: str
    target: str
    message: str = ""

class ScanDetailResponse(BaseModel):
    id: int
    target: str
    tools_used: list
    status: str
    scan_date: str
    overall_risk: Optional[str]
    vulnerabilities: list
    fixes: list
    exploits: list
    summary: Optional[dict]

async def run_scan_task(scan_id: int, target: str, tools: List[str], auto_recon: bool, has_accepted_disclaimer: int):
    from db import SessionLocal, get_scan as db_get_scan, update_scan_status as db_update_status, save_vulnerability as db_save_vuln, save_fix as db_save_fix, save_exploit as db_save_exploit, save_summary as db_save_summary
    from llm import analyze_with_llm, agentic_loop
    
    db = SessionLocal()
    try:
        scan = db_get_scan(db, scan_id, 0)
        if not scan:
            return
        
        tool_results = {}
        ws_clients = []
        
        for i, tool in enumerate(tools):
            try:
                if tool in TOOL_MAP:
                    result = await run_tool_by_name(tool, target)
                    tool_results[tool] = result
            
            except Exception as e:
                tool_results[tool] = {
                    "tool": tool,
                    "output": "",
                    "error": str(e),
                    "duration": 0,
                    "returncode": -1
                }
        
        db_update_status(db, scan_id, "running")
        
        try:
            llm_analysis = await analyze_with_llm(tool_results, target)
            llm_analysis["llm_timestamp"] = datetime.utcnow().isoformat()
            
            vulnerabilities = llm_analysis.get("vulnerabilities", [])
            for vuln in vulnerabilities:
                if vuln.get("name"):
                    db_save_vuln(db, scan_id, vuln)
            
            fixes = llm_analysis.get("fixes", [])
            for fix in fixes:
                if fix.get("fix_summary"):
                    db_save_fix(db, scan_id, fix)
            
            exploits = llm_analysis.get("exploit_suggestions", [])
            for exploit in exploits:
                if exploit.get("exploit_name"):
                    db_save_exploit(db, scan_id, {
                        "vuln_id": exploit.get("vuln_id"),
                        "exploit_name": exploit.get("exploit_name"),
                        "tool_used": exploit.get("tool", ""),
                        "payload": exploit.get("payload", ""),
                        "difficulty": exploit.get("difficulty", ""),
                        "notes": ""
                    })
            
            if auto_recon and llm_analysis.get("additional_recon_suggested"):
                llm_analysis = await agentic_loop(target, tool_results, scan_id, auto_recon)
            
            raw_outputs_json = json.dumps(tool_results)
            db_save_summary(db, scan_id, {
                "raw_outputs": raw_outputs_json,
                "ai_analysis": json.dumps(llm_analysis),
                "executive_summary": llm_analysis.get("executive_summary", ""),
                "attack_surface": json.dumps(llm_analysis.get("attack_surface", {})),
                "pentest_notes": llm_analysis.get("pentest_notes", ""),
                "generated_at": datetime.utcnow()
            })
            
            risk = llm_analysis.get("overall_risk_level", "Unknown")
            db_update_status(db, scan_id, "complete", risk)
            
        except Exception as e:
            db_update_status(db, scan_id, "failed")
            print(f"Scan analysis error: {str(e)}")
    
    finally:
        db.close()

@router.post("/start", response_model=ScanResponse)
async def start_scan(
    request: ScanStartRequest,
    background_tasks: BackgroundTasks,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not validate_target(request.target):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid target. Must be valid IP or domain. Internal/loopback addresses not allowed."
        )
    
    if request.has_accepted_disclaimer != 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You must accept the disclaimer before scanning."
        )
    
    tools = request.tools if request.tools else get_tools_for_preset(request.preset)
    
    scan = create_scan(db, current_user.id, request.target, tools, request.has_accepted_disclaimer)
    
    background_tasks.add_task(
        run_scan_task,
        scan.id,
        request.target,
        tools,
        request.auto_recon,
        request.has_accepted_disclaimer
    )
    
    return ScanResponse(
        scan_id=scan.id,
        status="started",
        target=request.target,
        message="Scan started successfully"
    )

@router.get("/{scan_id}", response_model=ScanDetailResponse)
async def get_scan_detail(
    scan_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    scan = get_scan(db, scan_id, current_user.id)
    if not scan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scan not found"
        )
    
    vulnerabilities = []
    if scan.vulnerabilities:
        for v in scan.vulnerabilities:
            vulnerabilities.append({
                "id": v.id,
                "vuln_id": v.vuln_id,
                "name": v.name,
                "severity": v.severity,
                "cvss_score": v.cvss_score,
                "cve_ids": v.cve_ids,
                "affected_port": v.affected_port,
                "affected_service": v.affected_service,
                "description": v.description,
                "evidence": v.evidence
            })
    
    fixes = []
    if scan.fixes:
        for f in scan.fixes:
            fixes.append({
                "id": f.id,
                "vuln_id": f.vuln_id,
                "fix_summary": f.fix_summary,
                "fix_detail": f.fix_detail,
                "patch_ref": f.patch_ref,
                "priority": f.priority
            })
    
    exploits = []
    if scan.exploits:
        for e in scan.exploits:
            exploits.append({
                "id": e.id,
                "vuln_id": e.vuln_id,
                "exploit_name": e.exploit_name,
                "tool_used": e.tool_used,
                "payload": e.payload,
                "difficulty": e.difficulty
            })
    
    summary = None
    if scan.summary:
        summary = {
            "raw_outputs": scan.summary.raw_outputs,
            "ai_analysis": scan.summary.ai_analysis,
            "executive_summary": scan.summary.executive_summary,
            "attack_surface": scan.summary.attack_surface,
            "pentest_notes": scan.summary.pentest_notes,
            "user_notes": scan.summary.user_notes
        }
    
    return ScanDetailResponse(
        id=scan.id,
        target=scan.target,
        tools_used=scan.tools_used or [],
        status=scan.status,
        scan_date=scan.scan_date.isoformat() if scan.scan_date else "",
        overall_risk=scan.overall_risk,
        vulnerabilities=vulnerabilities,
        fixes=fixes,
        exploits=exploits,
        summary=summary
    )

@router.delete("/{scan_id}")
async def delete_scan_endpoint(
    scan_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    success = delete_scan(db, scan_id, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scan not found"
        )
    return {"message": "Scan deleted successfully"}