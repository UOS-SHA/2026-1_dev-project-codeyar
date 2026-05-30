import "../../styles/classCard.css";

function ClassCard({
    title,
    subtitle,
    lecture,
    professor,
    date,
    onClick
}) {
    return (
        <div 
            className="class-card" 
            onClick={onClick}
        >

            <h2 className="class-title">
                {title}
            </h2>

            <p className="class-subtitle">
                {subtitle}
            </p>

            <div className="class-info">

                <p>📍 {lecture}</p>

                <p>👨‍🏫 {professor}</p>

                <p>📅 {date}</p>

            </div>

        </div>
    );
}

export default ClassCard;