import Header from "../../components/common/Header";

import "../../styles/problemManage.css";

function ProblemManagePage() {

    const user = {
        name: "김교수"
    };

    return (
        <div className="exam-create-page">

            <Header userName={user.name} />

            {/* 상단 */}
            <section className="create-hero">

                <h1 className="create-title">
                    시험 생성
                </h1>

                <p className="create-subtitle">
                    새로운 시험을 생성합니다.
                </p>

            </section>

            {/* 입력 폼 */}
            <section className="create-content">

                <div className="create-form">

                    <div className="form-group">

                        <label>
                            시험명
                        </label>

                        <input
                            type="text"
                            placeholder="시험명을 입력하세요"
                        />

                    </div>

                    <div className="form-group">

                        <label>
                            시험 설명
                        </label>

                        <textarea
                            placeholder="시험 설명을 입력하세요"
                        />

                    </div>

                    <div className="form-group">

                        <label>
                            제한 시간
                        </label>

                        <input
                            type="text"
                            placeholder="예: 120분"
                        />

                    </div>

                    <div className="form-group">

                        <label>
                            시험 날짜
                        </label>

                        <input
                            type="date"
                        />

                    </div>

                    <button className="create-button">
                        시험 생성하기
                    </button>

                </div>

            </section>

        </div>
    );
}

export default ProblemManagePage;