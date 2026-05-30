import Header from "../../components/common/Header";

import "../../styles/resultPage.css";

function ResultPage() {

    const user = {
        name: "김대은"
    };

    const resultList = [
        {
            id: 1,
            exam: "파이썬 기초 시험",
            score: "100점",
            submitTime: "2026-05-16 14:02",
            status: "채점 완료"
        },

        {
            id: 2,
            exam: "자료구조 시험",
            score: "85점",
            submitTime: "2026-05-18 15:11",
            status: "채점 완료"
        },

        {
            id: 3,
            exam: "알고리즘 시험",
            score: "-",
            submitTime: "-",
            status: "응시 예정"
        }
    ];

    return (
        <div className="result-page">

            <Header userName={user.name} />

            {/* 상단 */}
            <section className="student-result-hero">

                <h1 className="student-result-title">
                    채점 결과
                </h1>

                <p className="student-result-subtitle">
                    제출한 시험 결과를 확인할 수 있습니다.
                </p>

            </section>

            {/* 결과 테이블 */}
            <section className="student-result-content">

                <table className="student-result-table">

                    <thead>

                        <tr>
                            <th>번호</th>
                            <th>시험명</th>
                            <th>점수</th>
                            <th>제출 시간</th>
                            <th>상태</th>
                        </tr>

                    </thead>

                    <tbody>

                        {resultList.map((item) => (

                            <tr key={item.id}>

                                <td>{item.id}</td>

                                <td>{item.exam}</td>

                                <td>{item.score}</td>

                                <td>{item.submitTime}</td>

                                <td>{item.status}</td>

                            </tr>

                        ))}

                    </tbody>

                </table>

            </section>

        </div>
    );
}

export default ResultPage;