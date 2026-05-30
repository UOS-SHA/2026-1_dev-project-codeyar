import Header from "../../components/common/Header";

import "../../styles/submissionPage.css";

function SubmissionPage() {

    const user = {
        name: "홍길동"
    };

    return (
        <div className="submission-page">

            <Header userName={user.name} />

            <section className="submission-hero">

                <h1 className="submission-title">
                    제출이 완료되었습니다.
                </h1>

                <p className="submission-subtitle">
                    파이썬 기초 시험
                </p>

            </section>

        </div>
    );
}

export default SubmissionPage;