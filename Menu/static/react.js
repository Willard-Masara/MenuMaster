const App = () => {
    const [menu, setMenu] = React.useState(null);
    const [error, setError] = React.useState(null);

    const fetchMenu = async (restaurant) => {
        try {
            const response = await fetch(`/menus/${restaurant}`);
            const data = await response.json();
            if (response.ok) {
                setMenu(data);
                setError(null);
            } else {
                setMenu(null);
                setError(data.error);
            }
        } catch (err) {
            setMenu(null);
            setError("Failed to fetch menu");
        }
    };

    return (
        <div>
            <button onClick={() => fetchMenu('Mezepoli')}>Mezepoli Menu</button>
            <button onClick={() => fetchMenu('Ciccio')}>Ciccio Menu</button>
            <button onClick={() => fetchMenu('The Big Mouth')}>The Big Mouth Menu</button>
            <button onClick={() => fetchMenu('Ukko')}>Ukko Menu</button>

            {error && <div>{error}</div>}
            {menu && (
                <ul>
                    {menu.map((item, index) => (
                        <li key={index}>
                            {item.type}: {item.item} - {item.price}
                        </li>
                    ))}
                </ul>
            )}
        </div>
    );
};

ReactDOM.render(<App />, document.getElementById('app'));

