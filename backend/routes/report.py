from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import tempfile
import os

from db import get_db, get_scan
from report_generator import generate_report

router = APIRouter(prefix="/api/report", tags=["report"])

@router.get("/{scan_id}")
async def download_report(
    scan_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    scan = get_scan(db, scan_id, current_user.id)
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    
    if not scan.summary:
        raise HTTPException(status_code=404, detail="No analysis results found for this scan")
    
    import json
    try:
        ai_analysis = json.loads(scan.summary.ai_analysis)
    except:
        ai_analysis = {}
    
    try:
        attack_surface = json.loads(scan.summary.attack_surface) if scan.summary.attack_surface else {}
    except:
        attack_surface = {}
    
    analysis = {
        "target": scan.target,
        "scan_timestamp": scan.scan_date.isoformat() if scan.scan_date else "",
        "overall_risk_level": scan.overall_risk or "Unknown",
        "executive_summary": scan.summary.executive_summary or "",
        "vulnerabilities": [
            {
                "vuln_id": v.vuln_id,
                "name": v.name,
                "severity": v.severity,
                "cvss_score": v.cvss_score,
                "cve_ids": v.cve_ids,
                "affected_port": v.affected_port,
                "affected_service": v.affected_service,
                "description": v.description,
                "evidence": v.evidence,
                "attack_vector": v.attack_vector,
                "exploitability": v.exploitability
            }
            for v in scan.vulnerabilities
        ],
        "attack_surface": attack_surface,
        "exploit_suggestions": [
            {
                "vuln_id": e.vuln_id,
                "exploit_name": e.exploit_name,
                "tool": e.tool_used,
                "payload": e.payload,
                "difficulty": e.difficulty
            }
            for e in scan.exploits
        ],
        "fixes": [
            {
                "vuln_id": f.vuln_id,
                "fix_summary": f.fix_summary,
                "fix_detail": f.fix_detail,
                "patch_ref": f.patch_ref,
                "priority": f.priority
            }
            for f in scan.fixes
        ],
        "additional_recon_suggested": [],
        "pentest_notes": scan.summary.pentest_notes or ""
    }
    
    tmp = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
    tmp_path = tmp.name
    tmp.close()
    
    try:
        generate_report(analysis, tmp_path)
        
        target_safe = scan.target.replace("/", "_").replace(".", "_")
        return FileResponse(
            tmp_path,
            media_type="application/pdf",
            filename=f"metatron_{target_safe}_{scan_id}.pdf",
            background=lambda: os.unlink(tmp_path)
        )
    except Exception as e:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
        raise HTTPException(status_code=500, detail=f"Failed to generate report: {str(e)}")