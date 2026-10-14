from __future__ import annotations
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.llm import get_llm
from backend.models import Finding, Report, ReportSection
from backend.repositories import audit
from backend.utils.ids import short_id

DISCLAIMER = """NOT CLINICAL ADVICE: This assistant uses synthetic demo data only. Do not use for diagnosis or treatment decisions. Consult a licensed clinician."""

def _wrap_disclaimer(body: str) -> str:
    body = (body or "").strip()
    return f"{DISCLAIMER}\n\n{body}\n\n{DISCLAIMER}"

async def create_report(session: AsyncSession, patient_label: str, title: str) -> Report:
    row = Report(id=short_id(), patient_label=patient_label[:120], title=title[:200])
    session.add(row)
    await session.commit()
    await session.refresh(row)
    audit.record("report_created", row.id)
    return row

async def list_reports(session: AsyncSession) -> list[Report]:
    stmt = select(Report).order_by(Report.created_at.desc()).limit(50)
    return list((await session.execute(stmt)).scalars())

async def get_report(session: AsyncSession, report_id: str) -> Report | None:
    return await session.get(Report, report_id)

async def create_section(session: AsyncSession, report_id: str, heading: str, body: str, sort_order: int) -> ReportSection:
    if not await session.get(Report, report_id):
        raise ValueError("report not found")
    sec = ReportSection(id=short_id(), report_id=report_id, heading=heading[:120], body=body, sort_order=sort_order)
    session.add(sec)
    await session.commit()
    await session.refresh(sec)
    return sec

async def update_section(session: AsyncSession, section_id: str, heading: str, body: str, sort_order: int) -> ReportSection:
    sec = await session.get(ReportSection, section_id)
    if not sec:
        raise ValueError("section not found")
    sec.heading, sec.body, sec.sort_order = heading[:120], body, sort_order
    await session.commit()
    await session.refresh(sec)
    return sec

async def delete_section(session: AsyncSession, section_id: str) -> None:
    sec = await session.get(ReportSection, section_id)
    if not sec:
        raise ValueError("section not found")
    await session.delete(sec)
    await session.commit()

async def list_sections(session: AsyncSession, report_id: str) -> list[ReportSection]:
    stmt = select(ReportSection).where(ReportSection.report_id == report_id).order_by(ReportSection.sort_order)
    return list((await session.execute(stmt)).scalars())

async def add_finding(session: AsyncSession, report_id: str, label: str, severity: str, detail: str) -> Finding:
    if not await session.get(Report, report_id):
        raise ValueError("report not found")
    f = Finding(id=short_id(), report_id=report_id, label=label[:160], severity=severity[:24], detail=detail)
    session.add(f)
    await session.commit()
    await session.refresh(f)
    return f

async def list_findings(session: AsyncSession, report_id: str) -> list[Finding]:
    stmt = select(Finding).where(Finding.report_id == report_id)
    return list((await session.execute(stmt)).scalars())

async def draft_assist(session: AsyncSession, report_id: str) -> dict[str, str]:
    report = await session.get(Report, report_id)
    if not report:
        raise ValueError("report not found")
    sections = await list_sections(session, report_id)
    findings = await list_findings(session, report_id)
    bullets = "\n".join(f"- {f.label} ({f.severity}): {f.detail[:120]}" for f in findings)
    outline = "\n".join(f"## {s.heading}\n{s.body[:400]}" for s in sections)
    llm = get_llm()
    raw = await llm.complete(
        f"Draft a synthetic demo report summary for {report.title}.\nFindings:\n{bullets}\nSections:\n{outline}",
        system="Educational demo only; no medical advice.",
    )
    wrapped = _wrap_disclaimer(raw)
    report.draft_text = wrapped
    report.status = "draft_ready"
    await session.commit()
    audit.record("draft_assist", report_id)
    return {"draft": wrapped, "disclaimer": DISCLAIMER}
