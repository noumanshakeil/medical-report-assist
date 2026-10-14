from pydantic import BaseModel, Field

class ReportIn(BaseModel):
    patient_label: str = Field(min_length=1)
    title: str = Field(min_length=2)

class SectionIn(BaseModel):
    heading: str = Field(min_length=1)
    body: str = ""
    sort_order: int = 0

class FindingIn(BaseModel):
    label: str = Field(min_length=1)
    severity: str = "info"
    detail: str = ""
