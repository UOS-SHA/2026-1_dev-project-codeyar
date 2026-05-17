import "../../styles/menuCard.css";

function MenuCard({ title, description, onClick }) {
    return (
        <div 
            className="menu-card" 
            onClick = {onClick}
        >

            <div className="menu-icon">
                🔨
            </div>

            <div className="menu-content">

                <h2 className="menu-title">
                    {title}
                </h2>

                <p className="menu-description">
                    {description}
                </p>

            </div>

        </div>
    );
}

export default MenuCard;