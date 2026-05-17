import Header from "../../components/common/Header";

import "../../styles/examManage.css";

import { useNavigate } from "react-router-dom";

function ExamManagePage() {

    const user = {
        name: "김교수"
    };

    const navigate = useNavigate();

    return (
        <div className="exam-manage-page">

            <Header userName={user.name} />

            {/* 상단 영역 */}
            <section className="manage-hero">

                <h1 className="manage-title">
                    클래스1 관리
                </h1>

                <p className="manage-subtitle">
                    파이썬 기초 시험
                </p>

            </section>

            {/* 아래 카드 */}
            <section className="manage-content">

                <div className="manage-card">

                    <h2>
                        시험1
                    </h2>

                    <p>
                        파이썬 기초 테스트
                    </p>

                    <div className="manage-button-group">

                        <button className="manage-button"
                            onClick={() => navigate("/professor/problem")}>
                            시험 생성
                        </button>

                        <button className="manage-button"
                            onClick={() => navigate("/professor/student")}>
                            학생 관리
                        </button>

                        <button className="manage-button"
                            onClick={() => navigate("/professor/result")}>
                            결과 관리
                        </button>

                        <button className="manage-button"
                            onClick={() => navigate("/professor/log")}>
                            부정행위 로그
                        </button>

                    </div>

                </div>

            </section>

        </div>
    );
}

export default ExamManagePage;