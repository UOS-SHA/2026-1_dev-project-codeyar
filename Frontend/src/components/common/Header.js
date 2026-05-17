import "./../../styles/header.css";

function Header({userName}) {
    return (
        <header className="header">
            <div className="header-left">
                <div className="logo-circle"></div>

                <h2 className="logo-text">
                    OnlineJudge
                </h2>

                <span className="nav-item">
                    Home
                </span>
            </div>

            <div className="header-right">
                <button className="icon-button">
                    🔍
                </button>

                <span className="user-name">
                    {userName}
                </span>

                <button className="logout-button">
                    로그아웃
                </button>
            </div>
        </header>
    );
}

export default Header;