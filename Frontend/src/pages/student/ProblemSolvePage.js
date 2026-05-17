import Header from "../../components/common/Header";

import MonacoEditor from "@monaco-editor/react";

import { useNavigate } from "react-router-dom";

import "../../styles/problemSolve.css";

function ProblemSolvePage() {

    const navigate = useNavigate();

    const user = {
        name: "홍길동"
    };

    return (
        <div className="solve-page">

            <Header userName={user.name} />

            <div className="solve-container">

                {/* 왼쪽 문제 영역 */}
                <div className="problem-panel">

                    <h2 className="problem-title">
                        두 수의 합
                    </h2>

                    <p className="problem-description">
                        두 정수 A와 B를 입력받아
                        합을 출력하는 프로그램을 작성하세요.
                    </p>

                    <div className="io-box">

                        <h3>입력 형식</h3>

                        <p>
                            첫째 줄에 A와 B가 주어진다.
                        </p>

                    </div>

                    <div className="io-box">

                        <h3>출력 형식</h3>

                        <p>
                            두 수의 합을 출력한다.
                        </p>

                    </div>

                </div>

                {/* 오른쪽 */}
                <div className="editor-panel">

                    {/* 에디터 상단 */}
                    <div className="editor-header">

                        <div className="editor-tab">
                            main.py
                        </div>

                        <button className="run-button">
                            실행
                        </button>

                    </div>

                    {/* 코드 에디터 */}
                    <div className="editor-wrapper">

                        <MonacoEditor
                            height="100%"
                            defaultLanguage="python"
                            defaultValue={`a, b = map(int, input().split())

print(a + b)`}
                            theme="vs-dark"
                            options={{
                                fontSize: 16,
                                minimap: {
                                    enabled: false
                                },
                                scrollBeyondLastLine: false
                            }}
                        />

                    </div>

                    {/* 터미널 */}
                    <div className="terminal-panel">

                        <div className="terminal-header">
                            TERMINAL
                        </div>

                        <div className="terminal-content">

                            <p>
                                ▶ Python 3.10.0
                            </p>

                            <p>
                                실행 결과가 여기에 출력됩니다.
                            </p>

                        </div>

                    </div>

                    {/* 제출 버튼 */}
                    <div className="submit-section">

                        <button
                            className="submit-button"
                            onClick={() => 
                                navigate("/student/submission")
                            }
                        >
                            제출하기
                        </button>
                    </div>

                </div>

            </div>

        </div>
    );
}

export default ProblemSolvePage;