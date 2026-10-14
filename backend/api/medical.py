from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from backend.db import get_db
from backend.schemas import FindingIn, ReportIn, SectionIn
from backend.services import medical_report as svc

router = APIRouter()

@router.post("/reports")
async def create_report(payload: ReportIn, db: AsyncSession = Depends(get_db)):
    row = await svc.create_report(db, payload.patient_label, payload.title)
    return {"id": row.id, "status": row.status}

@router.get("/reports")
async def list_reports(db: AsyncSession = Depends(get_db)):
    rows = await svc.list_reports(db)
    return {"reports": [{"id": r.id, "title": r.title, "patient_label": r.patient_label, "status": r.status} for r in rows]}

@router.get("/reports/{report_id}")
async def get_report(report_id: str, db: AsyncSession = Depends(get_db)):
    row = await svc.get_report(db, report_id)
    if not row:
        raise HTTPException(404, "report not found")
    return {"id": row.id, "title": row.title, "draft_text": row.draft_text, "status": row.status}

@router.post("/reports/{report_id}/sections")
async def create_section(report_id: str, payload: SectionIn, db: AsyncSession = Depends(get_db)):
    try:
        sec = await svc.create_section(db, report_id, payload.heading, payload.body, payload.sort_order)
        return {"id": sec.id}
    except ValueError as exc:
        raise HTTPException(404, str(exc)) from exc

@router.put("/reports/{report_id}/sections/{section_id}")
async def update_section(report_id: str, section_id: str, payload: SectionIn, db: AsyncSession = Depends(get_db)):
    try:
        sec = await svc.update_section(db, section_id, payload.heading, payload.body, payload.sort_order)
        return {"id": sec.id, "report_id": report_id}
    except ValueError as exc:
        raise HTTPException(404, str(exc)) from exc

@router.delete("/reports/{report_id}/sections/{section_id}")
async def delete_section(report_id: str, section_id: str, db: AsyncSession = Depends(get_db)):
    try:
        await svc.delete_section(db, section_id)
        return {"ok": True}
    except ValueError as exc:
        raise HTTPException(404, str(exc)) from exc

@router.get("/reports/{report_id}/sections")
async def list_sections(report_id: str, db: AsyncSession = Depends(get_db)):
    rows = await svc.list_sections(db, report_id)
    return {"sections": [{"id": s.id, "heading": s.heading, "body": s.body, "sort_order": s.sort_order} for s in rows]}

@router.post("/reports/{report_id}/findings")
async def add_finding(report_id: str, payload: FindingIn, db: AsyncSession = Depends(get_db)):
    try:
        f = await svc.add_finding(db, report_id, payload.label, payload.severity, payload.detail)
        return {"id": f.id}
    except ValueError as exc:
        raise HTTPException(404, str(exc)) from exc

@router.get("/reports/{report_id}/findings")
async def list_findings(report_id: str, db: AsyncSession = Depends(get_db)):
    rows = await svc.list_findings(db, report_id)
    return {"findings": [{"id": f.id, "label": f.label, "severity": f.severity, "detail": f.detail} for f in rows]}

@router.post("/reports/{report_id}/draft-assist")
async def draft_assist(report_id: str, db: AsyncSession = Depends(get_db)):
    try:
        return await svc.draft_assist(db, report_id)
    except ValueError as exc:
        raise HTTPException(404, str(exc)) from exc
