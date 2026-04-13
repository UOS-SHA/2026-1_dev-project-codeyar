from fastapi import APIRouter, HTTPException, BackgroundTasks
import uuid

from app.schemas.submission import SubmitRequest, SubmitResponse, SubmissionStatusResponse
from app.services.judge import Judge0Client, Judge0APIError

router = APIRouter()
judge_client = Judge0Client()

# (임시) 데이터베이스 역할을 하는 메모리 저장소
# 실무 구현 시에는 SqlAlchemy 같은 ORM의 Session을 넘겨 DB에 insert/update 합니다.
fake_db = {}

@router.post("/", response_model=SubmitResponse, status_code=202)
async def submit_code(request: SubmitRequest, background_tasks: BackgroundTasks):
    """
    작성된 코드에 대해 Judge0 '발급 토큰'만 즉시 받고 Background에서 폴링을 시작합니다.
    사용자에게는 대기(Block) 없는 0.1초의 초고속 응답속도로 고유 추적 ID가 돌아갑니다.
    """
    try:
        tokens_str = await judge_client.submit_batch(
            source_code=request.code,
            language_id=request.language_id,
            test_cases=request.test_cases,
            time_limit=request.time_limit
        )
    except Judge0APIError as e:
        raise HTTPException(status_code=400, detail=str(e))
        
    # 데이터베이스에 상태 기록 (임시 dict 이용)
    submission_id = str(uuid.uuid4())
    fake_db[submission_id] = {
        "status": "Pending",
        "results": []
    }
    
    # 백엔드 뒷단을 조용히 돌아가는 Background 폴링 워커 투입!
    background_tasks.add_task(judge_client.poll_and_update, tokens_str, submission_id, fake_db)
    
    return SubmitResponse(submission_id=submission_id, status="Pending")


@router.get("/{submission_id}", response_model=SubmissionStatusResponse)
async def get_submission(submission_id: str):
    """
    프론트엔드가 결과를 조회하러 정기적으로 방문하는 엔드포인트입니다.
    """
    if submission_id not in fake_db:
        raise HTTPException(status_code=404, detail="Submission not found")
        
    data = fake_db[submission_id]
    return SubmissionStatusResponse(
        status=data["status"], 
        results=data["results"]
    )
