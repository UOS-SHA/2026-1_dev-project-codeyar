# 🔧 코드야르 (CodeYar) — 구현 계획서

> **작성일**: 2026-04-02  
> **버전**: v1.0

---

## 1. 시스템 아키텍처 개요

```
[ C# WinForms Client ]
        ↕ REST API (HTTP/HTTPS)
[ FastAPI Server ]
    ├── Auth Module         # JWT 인증
    ├── Problem Module      # 문제 관리
    ├── Submission Module   # 제출 처리
    │       ↓ (AST 검사 Pass 시)
    │   [ Judge0 API ]      # 외부 Docker 채점기
    ├── EventLog Module     # 안티치트 이벤트 수신
    └── DB (SQLAlchemy)
        
[ React Frontend (교수용 대시보드 Web UI) ]
        ↕ REST API
[ FastAPI Server ]
```

---

## 2. 디렉토리 구조 (Backend / FastAPI)

```
Backend/
├── app/
│   ├── main.py                  # FastAPI 진입점, 라우터 등록
│   ├── core/
│   │   ├── config.py            # 환경변수, 설정값 관리
│   │   ├── security.py          # JWT 생성/검증
│   │   └── middleware.py        # User-Agent 검증 미들웨어
│   ├── db/
│   │   ├── base.py              # SQLAlchemy Base 설정
│   │   └── session.py           # DB 세션 관리
│   ├── models/                  # DB 테이블 모델
│   │   ├── user.py
│   │   ├── problem.py
│   │   ├── submission.py
│   │   └── event_log.py
│   ├── schemas/                 # Pydantic 요청/응답 스키마
│   │   ├── user.py
│   │   ├── problem.py
│   │   ├── submission.py
│   │   └── event_log.py
│   ├── api/
│   │   └── v1/
│   │       ├── auth.py          # 로그인/토큰 발급
│   │       ├── problems.py      # 문제 CRUD
│   │       ├── submissions.py   # 코드 제출 및 결과 확인
│   │       └── event_logs.py    # 안티치트 이벤트 수신
│   └── services/
│       ├── judge0_client.py     # Judge0 API 호출 래퍼
│       └── ast_checker.py       # Python AST 구조 검사기
├── tests/
├── .env
├── requirements.txt
└── Dockerfile
```

---

## 3. 데이터 모델 설계

### User
| 필드 | 타입 | 설명 |
| :--- | :--- | :--- |
| `id` | UUID | Primary Key |
| `username` | str | 로그인 ID |
| `password_hash` | str | 해시된 비밀번호 |
| `role` | enum | `professor` / `student` |
| `created_at` | datetime | 생성 시각 |

### Problem
| 필드 | 타입 | 설명 |
| :--- | :--- | :--- |
| `id` | UUID | Primary Key |
| `title` | str | 문제 제목 |
| `description` | str | 문제 설명 |
| `time_limit` | int | 실행 시간 제한 (ms) |
| `memory_limit` | int | 메모리 제한 (MB) |
| `test_cases` | JSON | 입/출력 데이터셋 목록 |
| `ast_conditions` | JSON | AST 검사 조건 목록 |
| `created_by` | UUID | FK → User (교수) |

### Submission
| 필드 | 타입 | 설명 |
| :--- | :--- | :--- |
| `id` | UUID | Primary Key |
| `problem_id` | UUID | FK → Problem |
| `student_id` | UUID | FK → User |
| `code` | text | 제출 코드 |
| `language` | str | 언어 (현재 Python) |
| `status` | enum | `Accepted`, `Wrong Answer`, `TLE`, `MLE`, `Runtime Error`, `AST Fail` |
| `cpu_time` | float | Judge0가 측정한 CPU 시간 |
| `memory` | int | Judge0가 측정한 메모리 사용량 |
| `submitted_at` | datetime | 제출 시각 |

### EventLog
| 필드 | 타입 | 설명 |
| :--- | :--- | :--- |
| `id` | UUID | Primary Key |
| `student_id` | UUID | FK → User |
| `event_type` | enum | `PASTE`, `FOCUS_LOST`, `APP_RESTART`, `NETWORK_LOST`, ... |
| `detail` | JSON | 이벤트 부가 정보 (예: 붙여넣기 시 내용 등) |
| `occurred_at` | datetime | 이벤트 발생 시각 |

---

## 4. API 엔드포인트 설계

### 4-1. 인증 (`/api/v1/auth`)
| Method | Endpoint | 설명 |
| :--- | :--- | :--- |
| `POST` | `/login` | ID/PW → JWT 토큰 발급 |
| `POST` | `/refresh` | 토큰 갱신 |

### 4-2. 문제 관리 (`/api/v1/problems`) — 교수 전용
| Method | Endpoint | 설명 |
| :--- | :--- | :--- |
| `GET` | `/` | 문제 목록 조회 |
| `POST` | `/` | 문제 출제 |
| `GET` | `/{id}` | 특정 문제 조회 |
| `PUT` | `/{id}` | 문제 수정 |
| `DELETE` | `/{id}` | 문제 삭제 |

### 4-3. 코드 제출 (`/api/v1/submissions`)
| Method | Endpoint | 설명 |
| :--- | :--- | :--- |
| `POST` | `/` | 코드 제출 (AST 검사 → Judge0 채점) |
| `GET` | `/{id}` | 특정 제출 결과 조회 (Polling) |
| `GET` | `/problem/{problem_id}` | 특정 문제의 내 제출 내역 |

### 4-4. 이벤트 로그 (`/api/v1/events`)
| Method | Endpoint | 설명 |
| :--- | :--- | :--- |
| `POST` | `/` | 클라이언트에서 이벤트 전송 |
| `GET` | `/student/{student_id}` | 특정 학생의 이벤트 목록 (교수 전용) |

---

## 5. 핵심 로직 구현 상세

### 5-1. User-Agent 검증 미들웨어 (`core/middleware.py`)
```python
# C# WinForms 클라이언트에서는 User-Agent를 커스텀 값으로 설정
# 이 값이 없는 요청은 차단 (API 직접 호출 방지)
ALLOWED_USER_AGENTS = ["CodeYar-Client/1.0", "CodeYar-Admin/1.0"]

@app.middleware("http")
async def verify_user_agent(request: Request, call_next):
    # /api/v1/ 경로에 대해서만 검증
    # 관리자 페이지(React)는 별도 처리
    ...
```

### 5-2. 코드 제출 처리 흐름 (`api/v1/submissions.py`)
```
POST /submissions
    │
    ├── 1. JWT 인증 확인
    │
    ├── 2. AST 검사 (services/ast_checker.py)
    │       ├── FAIL → status: "AST Fail", 즉시 반환
    │       └── PASS → 다음 단계
    │
    ├── 3. Judge0 API 호출 (services/judge0_client.py)
    │       ├── source_code, language_id, stdin 전달
    │       ├── time_limit, memory_limit 전달
    │       └── token 수신 (비동기 처리)
    │
    ├── 4. DB에 Submission 저장 (status: "Pending")
    │
    └── 5. token 반환 → 클라이언트는 GET /submissions/{id}로 결과 Polling
```

### 5-3. AST 검사기 (`services/ast_checker.py`)
```python
import ast

def check_ast_conditions(code: str, conditions: list[dict]) -> tuple[bool, str]:
    """
    conditions 예시:
    [
        {"type": "function_exists", "name": "fibo"},
        {"type": "recursive_call", "function": "fibo"},
        {"type": "forbidden_call", "names": ["os.system", "subprocess.run"]},
    ]
    """
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        return False, f"Syntax Error: {e}"
    
    for condition in conditions:
        if condition["type"] == "forbidden_call":
            # ast.walk()로 모든 노드 순회하며 금지 함수 호출 탐지
            ...
        elif condition["type"] == "function_exists":
            # FunctionDef 노드에서 함수명 확인
            ...
        elif condition["type"] == "recursive_call":
            # 함수 내부에서 자기 자신을 호출하는지 확인
            ...
    
    return True, "OK"
```

### 5-4. Judge0 클라이언트 (`services/judge0_client.py`)
```python
import httpx

JUDGE0_URL = "http://localhost:2358"  # Self-hosted Judge0

async def submit_code(source_code: str, language_id: int, 
                       stdin: str, time_limit: float, memory_limit: int) -> str:
    """Judge0에 코드를 제출하고 token을 반환"""
    payload = {
        "source_code": source_code,
        "language_id": language_id,   # Python 3 = 71
        "stdin": stdin,
        "cpu_time_limit": time_limit,
        "memory_limit": memory_limit * 1024,  # MB → KB
    }
    async with httpx.AsyncClient() as client:
        res = await client.post(f"{JUDGE0_URL}/submissions", json=payload)
        return res.json()["token"]

async def get_result(token: str) -> dict:
    """Judge0에서 채점 결과를 가져옴 (Polling)"""
    async with httpx.AsyncClient() as client:
        res = await client.get(f"{JUDGE0_URL}/submissions/{token}")
        return res.json()
```

---

## 6. 인프라 (Docker Compose)

```yaml
# docker-compose.yml
services:
  server:
    build: ./Backend
    ports:
      - "8000:8000"
    depends_on:
      - db
      - judge0

  db:
    image: postgres:15

  # Judge0 관련 (공식 docker-compose 파일 기준)
  judge0-server:
    image: judge0/judge0:latest
    ports:
      - "2358:2358"
    depends_on:
      - judge0-db
      - judge0-redis

  judge0-workers:
    image: judge0/judge0:latest
    command: ["./scripts/workers"]

  judge0-db:
    image: postgres:13

  judge0-redis:
    image: redis:6.0
```

---

## 7. 개발 단계별 TODO (Backend)

### Phase 1 — Foundation (기반 구축)
- [ ] FastAPI 프로젝트 초기화 및 디렉토리 구조 생성
- [ ] SQLAlchemy ORM 설정 및 DB 모델 작성 (`User`, `Problem`, `Submission`, `EventLog`)
- [ ] JWT 기반 임시 로그인 시스템 구현
- [ ] User-Agent 검증 미들웨어 구현

### Phase 2 — Core Judge (핵심 채점)
- [ ] Judge0 Docker 로컬 배포 및 테스트
- [ ] `judge0_client.py` — Judge0 API 호출 래퍼 구현
- [ ] 제출 API 구현 (코드 제출 → Judge0 연동 → 결과 저장)
- [ ] Polling 방식 결과 조회 API 구현

### Phase 3 — AST & Anti-Cheat (검증 & 안티치트)
- [ ] `ast_checker.py` — AST 기반 금지 함수 탐지 구현
- [ ] `ast_checker.py` — 코드 구조 조건 검사 구현 (함수 존재, 재귀 호출 등)
- [ ] 이벤트 로그 수신 API 구현
- [ ] 교수용 이벤트 로그 조회 API 구현

### Phase 4 — Dashboard (교수용 대시보드)
- [ ] 문제 CRUD API
- [ ] 학생 성적 집계 API
- [ ] 부정행위 리포트 API

### Phase 5 — Integration & Security (통합 및 보안)
- [ ] C# 클라이언트 ↔ FastAPI 연동 테스트
- [ ] Docker 환경 분리 (Judge0 컨테이너 네트워크 차단)
- [ ] 전체 흐름 통합 테스트

---

## 8. 채점 상태 코드 정의

| 상태 코드 | 설명 |
| :--- | :--- |
| `Pending` | 채점 대기 중 |
| `Processing` | Judge0에서 실행 중 |
| `Accepted` | 정답 |
| `Wrong Answer` | 오답 |
| `Time Limit Exceeded` | 시간 초과 |
| `Memory Limit Exceeded` | 메모리 초과 |
| `Runtime Error` | 런타임 에러 |
| `Compile Error` | 컴파일/문법 오류 |
| `AST Fail` | AST 조건 불충족 (제출 거절) |
