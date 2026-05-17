import Header from "../../components/common/Header";

import "../../styles/resultManage.css";

function ResultManagePage() {

    const user = {
        name: "김교수"
    };

    const resultList = [
        {
            id: 1,
            student: "학생1",
            score: "100점",
            submitTime: "14:02",
            status: "채점 완료"
        },

        {
            id: 2,
            student: "학생2",
            score: "85점",
            submitTime: "14:10",
            status: "채점 완료"
        },

        {
            id: 3,
            student: "학생3",
            score: "진행 중",
            submitTime: "-",
            status: "응시 중"
        },

        {
            id: 4,
            student: "학생4",
            score: "70점",
            submitTime: "14:25",
            status: "채점 완료"
        }
    ];

    return (
        <div className="result-manage-page">

            <Header userName={user.name} />

            {/* 상단 */}
            <section className="result-hero">

                <h1 className="result-title">
                    결과 관리
                </h1>

                <p className="result-subtitle">
                    학생 제출 결과 및 채점 현황
                </p>

            </section>

            {/* 테이블 */}
            <section className="result-content">

                <table className="result-table">

                    <thead>

                        <tr>
                            <th>번호</th>
                            <th>학생명</th>
                            <th>점수</th>
                            <th>제출 시간</th>
                            <th>상태</th>
                        </tr>

                    </thead>

                    <tbody>

                        {resultList.map((item) => (

                            <tr key={item.id}>

                                <td>{item.id}</td>
                                <td>{item.student}</td>
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

export default ResultManagePage;