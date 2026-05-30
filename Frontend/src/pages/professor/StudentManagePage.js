import Header from "../../components/common/Header";

import Pagination from "../../components/student/Pagination";

import "../../styles/studentManage.css";

function StudentManagePage() {

    const user = {
        name: "김교수"
    };

    const studentList = [
        { id: 1, name: "학생1" },
        { id: 2, name: "학생2" },
        { id: 3, name: "학생3" },
        { id: 4, name: "학생4" },
        { id: 5, name: "학생5" },
        { id: 6, name: "학생6" },
        { id: 7, name: "학생7" },
        { id: 8, name: "학생8" },
        { id: 9, name: "학생9" },
        { id: 10, name: "학생10" }
    ];

    return (
        <div className="student-manage-page">

            <Header userName={user.name} />

            <div className="student-manage-container">

                {/* 상단 검색 */}
                <div className="student-toolbar">

                    <input
                        className="student-search"
                        type="text"
                        placeholder="Search..."
                    />

                    <select className="student-select">
                        <option>
                            Default
                        </option>
                    </select>

                    <select className="student-select">
                        <option>
                            Sort by: Featured
                        </option>
                    </select>

                </div>

                {/* 학생 카드 */}
                <div className="student-grid">

                    {studentList.map((student) => (

                        <div
                            className="student-card"
                            key={student.id}
                        >

                            <div className="student-image">
                            </div>

                            <div className="student-info">

                                <h3>
                                    Conference Chair
                                </h3>

                                <p>
                                    {student.name}
                                </p>

                            </div>

                        </div>

                    ))}

                </div>

                <Pagination />

            </div>

        </div>
    );
}

export default StudentManagePage;