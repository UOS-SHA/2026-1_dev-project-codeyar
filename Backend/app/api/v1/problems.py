from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.models.problem import Problem  # 아까 확인한 모델

router = APIRouter()

@router.get("/")
def get_problems(db: Session = Depends(get_db)):
    # DB에서 모든 문제 데이터를 가져옵니다.
    problems = db.query(Problem).all()
    return problems

@router.get("/{problem_id}")
def get_problem(problem_id: str, db: Session = Depends(get_db)):
    # 특정 ID의 문제 1개만 가져옵니다.
    problem = db.query(Problem).filter(Problem.id == problem_id).first()
    if not problem:
        raise HTTPException(status_code=404, detail="문제를 찾을 수 없습니다.")
    return problem