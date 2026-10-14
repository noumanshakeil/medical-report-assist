import pytest

@pytest.mark.asyncio
async def test_draft_has_disclaimer(client):
    r = await client.post("/api/reports", json={"patient_label": "P1", "title": "Demo MRI"})
    rid = r.json()["id"]
    await client.post(f"/api/reports/{rid}/sections", json={"heading": "Impression", "body": "Stable.", "sort_order": 1})
    await client.post(f"/api/reports/{rid}/findings", json={"label": "nodule", "severity": "low", "detail": "2mm"})
    d = await client.post(f"/api/reports/{rid}/draft-assist")
    assert d.status_code == 200
    body = d.json()["draft"]
    assert "NOT CLINICAL ADVICE" in body
    assert body.count("NOT CLINICAL ADVICE") >= 2

@pytest.mark.asyncio
async def test_section_crud(client):
    r = await client.post("/api/reports", json={"patient_label": "P2", "title": "Labs"})
    rid = r.json()["id"]
    c = await client.post(f"/api/reports/{rid}/sections", json={"heading": "CBC", "body": "WNL", "sort_order": 0})
    sid = c.json()["id"]
    u = await client.put(f"/api/reports/{rid}/sections/{sid}", json={"heading": "CBC updated", "body": "ok", "sort_order": 1})
    assert u.status_code == 200
    await client.delete(f"/api/reports/{rid}/sections/{sid}")
    lst = await client.get(f"/api/reports/{rid}/sections")
    assert lst.json()["sections"] == []
