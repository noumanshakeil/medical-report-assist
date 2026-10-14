# Dev server for medical-report-assist
$env:LLM_MODE = "mock"
uvicorn backend.main:app --reload --port 8000
