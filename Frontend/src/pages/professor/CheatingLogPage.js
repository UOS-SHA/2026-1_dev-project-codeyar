import Header from "../../components/common/Header";

import "../../styles/cheatingLog.css";

function CheatingLogPage() {

    const user = {
        name: "김교수"
    };

    const logList = [
        {
            id: 1,
            student: "학생1",
            action: "창 이탈 감지",
            time: "14:03:21",
            level: "주의"
        },

        {
            id: 2,
            student: "학생2",
            action: "복사 / 붙여넣기 감지",
            time: "14:07:12",
            level: "위험"
        },

        {
            id: 3,
            student: "학생3",
            action: "비정상 코드 제출",
            time: "14:11:42",
            level: "경고"
        },

        {
            id: 4,
            student: "학생4",
            action: "장시간 화면 이탈",
            time: "14:22:08",
            level: "주의"
        }
    ];

    return (
        <div className="cheating-log-page">

            <Header userName={user.name} />

            {/* 상단 */}
            <section className="log-hero">

                <h1 className="log-title">
                    부정행위 로그
                </h1>

                <p className="log-subtitle">
                    시험 중 감지된 이상 행동 기록
                </p>

            </section>

            {/* 로그 테이블 */}
            <section className="log-content">

                <table className="log-table">

                    <thead>

                        <tr>
                            <th>번호</th>
                            <th>학생명</th>
                            <th>감지 내용</th>
                            <th>시간</th>
                            <th>위험도</th>
                        </tr>

                    </thead>

                    <tbody>

                        {logList.map((item) => (

                            <tr key={item.id}>

                                <td>{item.id}</td>

                                <td>{item.student}</td>

                                <td>{item.action}</td>

                                <td>{item.time}</td>

                                <td>

                                    <span
                                        className={`log-badge ${item.level}`}
                                    >
                                        {item.level}
                                    </span>

                                </td>

                            </tr>

                        ))}

                    </tbody>

                </table>

            </section>

        </div>
    );
}

export default CheatingLogPage;