import Header from "../../components/common/Header";
import MenuCard from "../../components/student/MenuCard";
import { useNavigate } from "react-router-dom";

import "../../styles/studentMain.css";

function StudentMainPage() {

    const navigate = useNavigate();

    const user = {
        name: "홍길동"
    };

    const menuList = [
        {
            title: "최근 본 시험",
            description:
                "최근에 확인한 시험과 문제들을 다시 보기",
            path: "/stuent/exams"
        },

        {
            title: "채점 결과",
            description:
                "제출한 시험의 점수와 결과 확인",
            path: "/student/result"
        },

        {
            title: "클래스 목록",
            description:
                "수강 중인 클래스 확인",
            path: "/student/classes"
        }
    ];

    return (
        <div className="student-main-page">

            <Header userName={user.name} />

            <div className="menu-list">

                {menuList.map((menu, index) => (
                    <MenuCard
                        key={index}
                        title={menu.title}
                        description={menu.description}
                        onClick={() => navigate(menu.path)}
                    />
                ))}

            </div>

        </div>
    );
}

export default StudentMainPage;