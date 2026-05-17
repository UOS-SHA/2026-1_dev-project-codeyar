import "../../styles/pagination.css";

function Pagination() {
    return (
        <div className="pagination">

            <button>{"<"}</button>

            <button>1</button>
            <button>2</button>

            <button className="active-page">
                3
            </button>

            <button>4</button>
            <button>5</button>

            <button>{">"}</button>

        </div>
    );
}

export default Pagination;