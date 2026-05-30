import "../../styles/auth.css";
import { useState } from "react";

function SignupPage() {

    const [role, setRole] = useState("student");

    return (
        <div className="auth-page">

            <div className="logo">
                OnlineJudge
            </div>

            <div className="auth-container">

                <h1>회원가입</h1>

                <div className="role-select">
                    <button
                        className = {role === "student" ? "selected" : ""}
                        onClick = {() => setRole("student")}
                    >
                        학생
                    </button>

                    <button
                        className = {role === "professor" ? "selected" : ""}
                        onClick = {() => setRole("professor")}
                        >
                            교수
                        </button>
                </div>

                <div className="input-group">
                    <label>이름</label>
                    <input type="text" />
                </div>

                <div className="input-group">
                    <label>학교</label>
                    <input type="text" />
                </div>

                <div className="input-group">
                    <label>학번</label>
                    <input type="text" />
                </div>

                <div className="input-group">
                    <label>아이디</label>
                    <input type="text" />
                </div>

                <div className="input-group">
                    <label>비밀번호</label>
                    <input type="password" />
                </div>

                <div className="input-group">
                    <label>비밀번호 확인</label>
                    <input type="password" />
                </div>

                <button className="main-button">
                    회원가입
                </button>

            </div>
        </div>
    );
}

export default SignupPage;