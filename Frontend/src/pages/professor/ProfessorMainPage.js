import Header from "../../components/common/Header";

import MenuCard from "../../components/student/MenuCard";

import { useNavigate } from "react-router-dom";

import "../../styles/studentMain.css";

function ProfessorMainPage() {

    const navigate = useNavigate();

    const user = {
        name: "김교수"
    };

    const menuList = [
        {
            title: "오늘 시험 현황",
            description:
                "오늘 진행 중인 시험과 응시 현황을 확인할 수 있습니다.",
            path: "/professor/classes"
        },

        {
            title: "부정행위 탐지",
            description:
                "학생들의 이상 행동 및 부정행위 여부를 확인할 수 있습니다.",
            path: "/professor/classes"
        },

        {
            title: "클래스 목록",
            description:
                "담당 중인 클래스와 시험을 관리할 수 있습니다.",
            path: "/professor/classes"
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

export default ProfessorMainPage;