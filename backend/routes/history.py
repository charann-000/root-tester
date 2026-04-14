from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from db import get_db, get_user_scans, get_scan, get_scan_stats, delete_scan
from auth_utils import get_current_user

router = APIRouter(prefix="/api/history", tags=["history"])

class ScanListResponse(BaseModel):
    id: int
    target: str
    tools_used: list
    status: str
    scan_date: str
    overall_risk: Optional[str]
    vuln_count: int = 0

class ScanStatsResponse(BaseModel):
    total: int
    complete: int
    critical: int
    high: int
    medium: int
    low: int

@router.get("", response_model=List[ScanListResponse])
async def get_history(
    skip: int = 0,
    limit: int = 50,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    scans = get_user_scans(db, current_user.id, skip, limit)
    result = []
    for scan in scans:
        vuln_count = len(scan.vulnerabilities) if scan.vulnerabilities else 0
        result.append(ScanListResponse(
            id=scan.id,
            target=scan.target,
            tools_used=scan.tools_used or [],
            status=scan.status,
            scan_date=scan.scan_date.isoformat() if scan.scan_date else "",
            overall_risk=scan.overall_risk,
            vuln_count=vuln_count
        ))
    return result

@router.get("/stats", response_model=ScanStatsResponse)
async def get_stats(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    stats = get_scan_stats(db, current_user.id)
    return ScanStatsResponse(**stats)

@router.get("/{scan_id}")
async def get_history_detail(
    scan_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    scan = get_scan(db, scan_id, current_user.id)
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    
    return {
        "id": scan.id,
        "target": scan.target,
        "tools_used": scan.tools_used,
        "status": scan.status,
        "scan_date": scan.scan_date.isoformat() if scan.scan_date else None,
        "overall_risk": scan.overall_risk,
        "vulnerabilities": [
            {
                "vuln_id": v.vuln_id,
                "name": v.name,
                "severity": v.severity
            }
            for v in scan.vulnerabilities
        ]
    }

@router.delete("/{scan_id}")
async def delete_history_scan(
    scan_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    success = delete_scan(db, scan_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Scan not found")
    return {"message": "Scan deleted from history"}