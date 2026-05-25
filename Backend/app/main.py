from fastapi import FastAPI
from app.db.base import Base, engine
from app.api.v1 import submissions, auth, problems

# 앱 시작 시 SQLite 테이블 자동 생성
# 모든 모델을 import 해야 Base.metadata에 등록됩니다.
import app.models.school      # noqa: F401
import app.models.user        # noqa: F401
import app.models.exam        # noqa: F401
import app.models.problem     # noqa: F401
import app.models.submission   # noqa: F401
import app.models.event_log   # noqa: F401

Base.metadata.create_all(bind=engine)

app = FastAPI(title="CodeYar API", version="1.0.0")

# 라우터 등록
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(submissions.router, prefix="/api/v1/submissions", tags=["submissions"])

app.include_router(problems.router, prefix="/api/v1/problems", tags=["problems"])

@app.get("/")
def read_root():
    return {"message": "CodeYar Backend is running!"}
