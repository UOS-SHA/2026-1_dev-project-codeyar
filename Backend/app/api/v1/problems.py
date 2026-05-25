import json
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.models.problem import Problem
from app.models.exam import Exam
from app.models.user import User  # 임시 권한 검사용 유저 조회
from app.schemas.exam import ExamCreate, ExamResponse
from app.schemas.problem import ProblemCreate, ProblemResponse

router = APIRouter()

# ==========================================
# 1. 시험(Exam) 생성 API
# ==========================================
@router.post("/exams", response_model=ExamResponse, status_code=status.HTTP_201_CREATED, summary="시험 생성 (교수용)")
def create_exam(exam_data: ExamCreate, db: Session = Depends(get_db)):
    # [중복 검사] 이미 존재하는 시험 ID 인지 확인
    existing_exam = db.query(Exam).filter(Exam.id == exam_data.id).first()
    if existing_exam:
        raise HTTPException(status_code=400, detail="이미 존재하는 시험 ID입니다.")

    # [임시 권한/유저 검사] 일단 DB에 있는 'withacry1' 유저를 생성자로 지정합니다.
    mock_professor = db.query(User).filter(User.username == "withacry1").first()
    if not mock_professor:
        raise HTTPException(status_code=404, detail="시험을 생성할 교수(withacry1) 계정이 DB에 없습니다. 회원가입을 먼저 진행해주세요.")

    # DB 객체 생성
    new_exam = Exam(
        id=exam_data.id,
        title=exam_data.title,
        school_id=exam_data.school_id,
        created_by=mock_professor.id, # 조회한 진짜 UUID 주입
        start_time=exam_data.start_time,
        end_time=exam_data.end_time
    )
    
    db.add(new_exam)
    db.commit()
    db.refresh(new_exam)
    return new_exam


# ==========================================
# 2. 문제(Problem) 생성 API
# ==========================================
@router.post("/", response_model=ProblemResponse, status_code=status.HTTP_201_CREATED, summary="문제 생성 (교수용)")
def create_problem(prob_data: ProblemCreate, db: Session = Depends(get_db)):
    # [중복 검사] 이미 존재하는 문제 ID 인지 확인
    existing_prob = db.query(Problem).filter(Problem.id == prob_data.id).first()
    if existing_prob:
        raise HTTPException(status_code=400, detail="이미 존재하는 문제 ID입니다.")

    # [외래키 검사] 엮으려고 하는 시험(exam_id)이 실제로 존재하는지 확인
    target_exam = db.query(Exam).filter(Exam.id == prob_data.exam_id).first()
    if not target_exam:
        raise HTTPException(status_code=404, detail=f"입력하신 시험 ID({prob_data.exam_id})가 존재하지 않습니다.")

    # JSON 데이터 문자열(Text)로 직렬화 변환 (파이썬 list -> JSON string)
    ast_str = json.dumps(prob_data.ast_conditions)
    global_ast_str = json.dumps(prob_data.global_ast_conditions)
    test_cases_str = json.dumps(prob_data.test_cases)

    # DB 객체 생성
    new_problem = Problem(
        id=prob_data.id,
        exam_id=prob_data.exam_id,
        title=prob_data.title,
        description=prob_data.description,
        time_limit=prob_data.time_limit,
        memory_limit=prob_data.memory_limit,
        language_id=prob_data.language_id,
        ast_conditions=ast_str,
        global_ast_conditions=global_ast_str,
        test_cases=test_cases_str
    )

    db.add(new_problem)
    db.commit()
    db.refresh(new_problem)
    return new_problem


# ==========================================
# 3. 기존의 조회(GET) API 목록
# ==========================================
@router.get("/", response_model=List[ProblemResponse])
def get_problems(db: Session = Depends(get_db)):
    return db.query(Problem).all()

@router.get("/{problem_id}", response_model=ProblemResponse)
def get_problem(problem_id: str, db: Session = Depends(get_db)):
    problem = db.query(Problem).filter(Problem.id == problem_id).first()
    if not problem:
        raise HTTPException(status_code=404, detail="문제를 찾을 수 없습니다.")
    return problem