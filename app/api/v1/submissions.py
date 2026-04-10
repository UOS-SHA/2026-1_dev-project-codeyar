from fastapi import APIRouter
from app.schemas.submission import SubmitRequest, SubmitResponse
from app.services import judge_client

router = APIRouter()

@router.post("/", response_model=SubmitResponse)
async def submit_code(request: SubmitRequest):
    """
    코드를 제출하고 AST 검사 및 Judge0 채점 큐에 넣습니다.
    (AST 검사 로직은 별도 추가 예정)
    """
    
    # 1. (예정) AST 검사 수행
    # is_valid, fail_reason = ast_checker.check(request.code, ...)
    # if not is_valid: return ...
    
    # 2. Judge0 에 제출
    token = await judge_client.submit_code(
        source_code=request.code,
        time_limit=request.time_limit,
        memory_limit=request.memory_limit
    )
    
    # 3. (예정) DB에 Pending 상태로 저장
    # db.add(Submission(token=token, status="Pending"))
    
    return SubmitResponse(token=token, status="Pending")
