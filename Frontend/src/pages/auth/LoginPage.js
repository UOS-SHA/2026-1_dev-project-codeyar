import "../../styles/auth.css";
import { useState } from "react";
import { useNavigate } from "react-router-dom";

function LoginPage() {

    const navigate = useNavigate();
    const [role, setRole] = useState("student");
    const [userId, setUserId] = useState("");
    const [password, setPassword] = useState("");

    return (
        <div className="auth-page">

            <div className="logo">
                OnlineJudge
            </div>

            <div className="auth-container">

                <h1>로그인</h1>

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
                    <label>아이디</label>
                    <input
                        type = "text" 
                        value = {userId}
                        onChange = {(e) => setUserId(e.target.value)} 
                    />
                </div>

                <div className="input-group">
                    <label>비밀번호</label>
                    <input 
                        type = "password"
                        value = {password}
                        onChange = {(e) => setPassword(e.target.value)}
                    />
                </div>

                <button 
                    className = "main-button"
                    onClick = {() => {
                        console.log(userId);
                        console.log(password);
                        console.log(role);

                        if (role === "student") {
                            navigate("/student/main");
                            } else {
                                navigate("/professor/main");
                            }
                    }}
                >
                    로그인
                </button>

                <button 
                    className = "sub-button"
                    onClick = {() => navigate("/signup")}
                >
                    회원가입
                </button>

            </div>
        </div>
    );
}

export default LoginPage;