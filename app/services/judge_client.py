import httpx
from app.core.config import settings

async def submit_code(source_code: str, language_id: int = 71, stdin: str = "", time_limit: float = 2.0, memory_limit: int = 128) -> str:
    """Judge0 API 호출 래퍼"""
    
    # 만약 환경 변수에 API Key가 없다면 더미 토큰 반환 (테스트 용도)
    if not settings.JUDGE0_API_KEY:
        print("WARNING: JUDGE0_API_KEY is not set. Returning a dummy token.")
        return "dummy-token-12345"

    headers = {
        "X-RapidAPI-Key": settings.JUDGE0_API_KEY,
        "X-RapidAPI-Host": "judge0-ce.p.rapidapi.com",
        "Content-Type": "application/json"
    }
    
    payload = {
        "source_code": source_code,
        "language_id": language_id, # 기본값 71 (Python 3.8.1)
        "stdin": stdin,
        "cpu_time_limit": time_limit,
        "memory_limit": memory_limit * 1024 # MB to KB
    }
    
    async with httpx.AsyncClient() as client:
        # RapidAPI Judge0 endpoint 기준
        response = await client.post(
            f"{settings.JUDGE0_API_URL}/submissions",
            headers=headers,
            params={"base64_encoded": "false", "fields": "*"},
            json=payload
        )
        response.raise_for_status()
        return response.json().get("token")
