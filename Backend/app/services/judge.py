import base64
import json
from collections import Counter
from typing import List

import httpx
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.base import SessionLocal

JUDGE0_API_URL = settings.JUDGE0_API_URL
JUDGE0_API_KEY = settings.JUDGE0_API_KEY

ACCEPTED_STATUS_ID = 3


class TestCaseInput(BaseModel):
    stdin: str = ""
    expected_output: str


class SubmissionResult(BaseModel):
    status_id: int
    status_desc: str
    time: float
    memory: int
    stdout: str
    stderr: str


class Judge0APIError(Exception):
    pass


_http_client: httpx.AsyncClient | None = None


def _get_http_client() -> httpx.AsyncClient:
    global _http_client
    if _http_client is None:
        limits = httpx.Limits(max_keepalive_connections=50, max_connections=100)
        _http_client = httpx.AsyncClient(limits=limits, timeout=30.0)
    return _http_client


def _determine_result(results: List[SubmissionResult]) -> tuple[bool, str | None]:
    """
    채점 결과를 분석하여 (passed, error_reason) 튜플을 반환합니다.
    - 전체 Accepted → (True, None)
    - 일부 실패 → (False, "2/5 테스트케이스 실패 (Wrong Answer)")
    """
    total = len(results)
    failed = [r for r in results if r.status_id != ACCEPTED_STATUS_ID]

    if not failed:
        return True, None

    reason_counts = Counter(r.status_desc for r in failed)
    top_reason = reason_counts.most_common(1)[0][0]

    return False, f"{len(failed)}/{total} 테스트케이스 실패 ({top_reason})"


class Judge0Client:
    def __init__(self):
        self.api_url = JUDGE0_API_URL
        self.headers = {
            "X-RapidAPI-Key": JUDGE0_API_KEY,
            "X-RapidAPI-Host": "judge0-ce.p.rapidapi.com",
            "Content-Type": "application/json"
        }
        self.client = _get_http_client()

    async def verify_api_key(self) -> bool:
        if not JUDGE0_API_KEY:
            return False

        try:
            response = await self.client.post(
                f"{self.api_url}/authenticate",
                headers=self.headers,
                timeout=5.0
            )
            return response.status_code == 200
        except httpx.RequestError:
            return False

    def _encode_b64(self, text: str) -> str:
        if not text:
            return ""
        return base64.b64encode(text.encode("utf-8")).decode("utf-8")

    def _decode_b64(self, text: str) -> str:
        if not text:
            return ""
        return base64.b64decode(text.encode("utf-8")).decode("utf-8", errors="replace")

    async def submit_batch(
        self,
        source_code: str,
        language_id: int,
        test_cases: List[TestCaseInput],
        time_limit: float = 2.0
    ) -> str:
        """
        코드와 입출력을 Base64로 인코딩한 뒤, Batch Queue에 삽입하고 즉시 tokens 문자열만 리턴합니다.
        (FastAPI의 메인 쓰레드를 블로킹하지 않음)
        """
        b64_source_code = self._encode_b64(source_code)

        submissions = []
        for tc in test_cases:
            submissions.append({
                "source_code": b64_source_code,
                "language_id": language_id,
                "stdin": self._encode_b64(tc.stdin),
                "expected_output": self._encode_b64(tc.expected_output),
                "cpu_time_limit": time_limit
            })

        try:
            response = await self.client.post(
                f"{self.api_url}/submissions/batch",
                params={"base64_encoded": "true"},
                headers=self.headers,
                json={"submissions": submissions}
            )
            response.raise_for_status()
            tokens_data = response.json()

            tokens = [item.get("token") for item in tokens_data if item.get("token")]
            return ",".join(tokens)

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                raise Judge0APIError("API 요청 한도 초과(429)")
            elif e.response.status_code in (401, 403):
                raise Judge0APIError("API KEY 인증 실패(401/403)")
            else:
                raise Judge0APIError(f"Judge0 API 통신 에러({e.response.status_code})")
        except httpx.RequestError as e:
            raise Judge0APIError(f"Judge0 네트워크 에러: {str(e)}")

    async def poll_and_update(self, tokens_str: str, submission_id: str):
        """
        BackgroundTasks 로 던져질 백그라운드용 함수입니다.
        독립적인 DB Session을 생성하여 폴링 결과를 DB에 기록합니다.
        """
        import asyncio

        # BackgroundTask에서는 독립적인 DB 세션을 사용
        db: Session = SessionLocal()
        results: List[SubmissionResult] = []

        try:
            from app.models.submission import Submission

            for _ in range(20):  # 최대 30초 대기
                await asyncio.sleep(1.5)
                res_get = await self.client.get(
                    f"{self.api_url}/submissions/batch",
                    params={"tokens": tokens_str, "base64_encoded": "true"},
                    headers=self.headers
                )
                if res_get.status_code != 200:
                    continue  # 일시적인 에러 가능성이 있으니 재시도

                raw_results = res_get.json().get("submissions", [])

                in_progress = any(r.get("status", {}).get("id", 1) in (1, 2) for r in raw_results)
                if not in_progress:
                    break
            else:
                # 타임아웃
                submission = db.query(Submission).filter(Submission.id == submission_id).first()
                if submission:
                    submission.status = "Timeout"
                    submission.passed = False
                    submission.error_reason = "채점 시간 초과 (Judge0 응답 없음)"
                    db.commit()
                return

            # 결과 파싱
            for res in raw_results:
                status = res.get("status", {})
                results.append(SubmissionResult(
                    status_id=status.get("id", 0),
                    status_desc=status.get("description", "Unknown"),
                    time=float(res.get("time") or 0.0),
                    memory=int(float(res.get("memory") or 0.0)),
                    stdout=self._decode_b64(res.get("stdout", "")),
                    stderr=self._decode_b64(res.get("stderr") or res.get("compile_output") or "")
                ))

            # passed / error_reason 판정
            passed, error_reason = _determine_result(results)

            # DB 업데이트
            submission = db.query(Submission).filter(Submission.id == submission_id).first()
            if submission:
                submission.status = "Completed"
                submission.passed = passed
                submission.error_reason = error_reason
                submission.result_json = json.dumps(
                    [r.model_dump() for r in results], ensure_ascii=False
                )
                db.commit()

        except Exception as e:
            submission = db.query(Submission).filter(Submission.id == submission_id).first()
            if submission:
                submission.status = "Error"
                submission.passed = False
                submission.error_reason = f"Worker Error: {str(e)}"
                db.commit()
        finally:
            db.close()
