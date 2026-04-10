from fastapi import FastAPI
from app.api.v1 import submissions

app = FastAPI(title="CodeYar API", version="1.0.0")

# 라우터 등록
app.include_router(submissions.router, prefix="/api/v1/submissions", tags=["submissions"])

@app.get("/")
def read_root():
    return {"message": "CodeYar Backend is running!"}
