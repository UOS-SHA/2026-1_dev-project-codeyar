import Header from "../../components/common/Header";

import ClassCard from "../../components/student/ClassCard";
import Pagination from "../../components/student/Pagination";

import "../../styles/classList.css";

import {useNavigate} from "react-router-dom"

function ClassListPage() {

    const navigate = useNavigate();

    const user = {
        name: "홍길동"
    };

    const classList = [
        {
            title: "클래스1",
            subtitle: "파이썬 기초 테스트",
            lecture: "강의명",
            professor: "교수명",
            date: "날짜"
        },

        {
            title: "클래스2",
            subtitle: "파이썬 기초 테스트",
            lecture: "강의명",
            professor: "교수명",
            date: "날짜"
        },

        {
            title: "클래스3",
            subtitle: "파이썬 기초 테스트",
            lecture: "강의명",
            professor: "교수명",
            date: "날짜"
        }
    ];

    return (
        <div className="class-list-page">

            <Header userName={user.name} />

            <div className="class-list-container">

                <h1 className="page-title">
                    클래스 목록
                </h1>

                <div className="class-list">

                    {classList.map((item, index) => (
                        <ClassCard
                            key={index}
                            title={item.title}
                            subtitle={item.subtitle}
                            lecture={item.lecture}
                            professor={item.professor}
                            date={item.date}
                            onClick={() => navigate("/student/exam")}
                        />
                    ))}

                </div>

                <Pagination />

            </div>

        </div>
    );
}

export default ClassListPage;