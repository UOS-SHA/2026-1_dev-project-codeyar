import Header from "../../components/common/Header";
import {useNavigate} from "react-router-dom"

import "../../styles/examPage.css";

function ExamPage() {

    const navigate = useNavigate();

    const user = {
        name: "홍길동"
    };

    return (
        <div className="exam-page">

            <Header userName={user.name} />

            <section className="exam-hero">

                <h1 className="exam-title">
                    클래스1
                </h1>

                <p className="exam-subtitle">
                    파이썬 기초 시험
                </p>

            </section>

            <section className="exam-content">

                <div className="exam-left">

                    <div className="exam-info">

                        <div className="info-item">
                            <span className="info-label">
                                응시자
                            </span>

                            <span className="info-value">
                                홍길동
                            </span>
                        </div>

                        <div className="info-item">
                            <span className="info-label">
                                학번
                            </span>

                            <span className="info-value">
                                20201234
                            </span>
                        </div>

                        <div className="info-item">
                            <span className="info-label">
                                클래스
                            </span>

                            <span className="info-value">
                                자료구조
                            </span>
                        </div>

                    </div>

                    <div className="exam-summary">

                        <div className="summary-item">
                            ⏰ 제한 시간 : 120분
                        </div>

                        <div className="summary-item">
                            📝 문제 수 : 5문제
                        </div>

                        <div className="summary-item">
                            🚫 시험 중 새로고침 제한
                        </div>

                    </div>

                    <textarea
                        className="intro-textarea"
                        placeholder="시험 관련 안내사항..."
                    />

                    <button 
                        className="enter-exam-button"
                        onClick={() => navigate("/student/solve")}
                    >
                        시험 입장하기
                    </button>

                </div>

                <div className="exam-right">

                    <button className="description-button">
                        ← 시험 설명
                    </button>

                    <div className="description-box">

                        <p>
                            시험 유형
                        </p>

                        <h3>
                            Python Coding Test
                        </h3>

                        <p>
                            제한 시간
                        </p>

                        <h3>
                            2 Hours
                        </h3>

                        <p>
                            시험 범위
                        </p>

                        <h3>
                            자료구조 / 알고리즘
                        </h3>

                    </div>

                </div>

            </section>

        </div>
    );
}

export default ExamPage;