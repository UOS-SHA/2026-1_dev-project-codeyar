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
