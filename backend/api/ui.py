from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from backend.db import get_db
from backend.services import medical_report as svc

router = APIRouter()
templates = Jinja2Templates(directory="backend/templates")

@router.get("/", response_class=HTMLResponse)
async def home(request: Request, db: AsyncSession = Depends(get_db)):
    reports = await svc.list_reports(db)
    return templates.TemplateResponse("index.html", {"request": request, "title": "Medical Report Assist", "reports": reports, "draft": None})

@router.post("/ui/reports")
async def ui_report(patient_label: str = Form("Demo patient"), title: str = Form(...), db: AsyncSession = Depends(get_db)):
    await svc.create_report(db, patient_label, title)
    return RedirectResponse("/", status_code=303)

@router.post("/ui/draft/{report_id}")
async def ui_draft(report_id: str, request: Request, db: AsyncSession = Depends(get_db)):
    out = await svc.draft_assist(db, report_id)
    reports = await svc.list_reports(db)
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "title": "Medical Report Assist", "reports": reports, "draft": out["draft"][:600]},
    )
