import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.security import hash_password, verify_password, create_access_token
from app.models.user import User
from app.models.school import School

router = APIRouter()


# ─── 요청/응답 스키마 ──────────────────────────────────────

class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, description="로그인 ID")
    password: str = Field(..., min_length=4, description="비밀번호")
    role: str = Field("student", description="student 또는 professor")
    school_id: str = Field(..., description="소속 학교 ID")


class RegisterResponse(BaseModel):
    user_id: str
    username: str
    role: str


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ─── 엔드포인트 ────────────────────────────────────────────

@router.post("/register", response_model=RegisterResponse, status_code=201)
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """회원가입: username, password, role, school_id를 받아 계정을 생성합니다."""

    # 학교 존재 확인
    school = db.query(School).filter(School.id == request.school_id).first()
    if not school:
        raise HTTPException(status_code=400, detail="존재하지 않는 학교 ID입니다.")

    # role 유효성
    if request.role not in ("student", "professor"):
        raise HTTPException(status_code=400, detail="role은 'student' 또는 'professor'여야 합니다.")

    # 중복 username
    existing = db.query(User).filter(User.username == request.username).first()
    if existing:
        raise HTTPException(status_code=409, detail="이미 사용 중인 username입니다.")

    user = User(
        id=str(uuid.uuid4()),
        username=request.username,
        password=hash_password(request.password),
        role=request.role,
        school_id=request.school_id,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return RegisterResponse(user_id=user.id, username=user.username, role=user.role)


@router.post("/login", response_model=LoginResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """로그인: username + password 검증 후 JWT 발급"""

    user = db.query(User).filter(User.username == request.username).first()
    if not user or not verify_password(request.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="잘못된 username 또는 비밀번호입니다.",
        )

    token = create_access_token(user.id)
    return LoginResponse(access_token=token)

# ─── 학교 등록 API (연습용) ──────────────────────────────────

class SchoolCreateRequest(BaseModel):
    id: str = Field(..., description="학교 ID (예: UOS)")
    name: str = Field(..., description="학교 이름 (예: 서울시립대학교)")
    code: str = Field(..., description="학교 코드 (예: UOS)")

@router.post("/schools", status_code=201)
def create_school(request: SchoolCreateRequest, db: Session = Depends(get_db)):
    # 1. 이미 존재하는 학교인지 DB 조회
    existing = db.query(School).filter(School.id == request.id).first()
    if existing:
        raise HTTPException(status_code=400, detail="이미 등록된 학교 ID입니다.")

    # 2. 새로운 학교 객체 생성 및 DB 저장
    new_school = School(
        id=request.id,
        name=request.name,
        code=request.code
    )
    db.add(new_school) # DB에 추가 대기
    db.commit()        # 실제 DB(SQLite)에 반영
    db.refresh(new_school)
    
    return {"message": "학교 등록 성공!", "school": new_school}

@router.get("/schools") #DB 조회 함수
def get_all_schools(db: Session = Depends(get_db)):
    schools = db.query(School).all() # DB의 모든 학교 데이터를 가져와라!
    return schools