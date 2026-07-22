import { useEffect, useState } from "react";
import api from "../api/api";
import "../styles/livemonitor.css";

function LiveMonitor() {
    const [liveData, setLiveData] = useState([]);
    const [search, setSearch] = useState("");

    useEffect(() => {
        fetchData();

        const interval = setInterval(fetchData, 1000);

        return () => clearInterval(interval);
    }, []);

    async function fetchData() {
        try {
            const res = await api.get("/dashboard");
            setLiveData(res.data.live || []);
        } catch (err) {
            console.error(err);
        }
    }

    const filtered = liveData.filter((item) =>
        item.tag?.toLowerCase().includes(search.toLowerCase()) ||
        item.comment?.toLowerCase().includes(search.toLowerCase())
    );

    return (
        <div style={{ padding: "20px" }}>
            <h1>Live PLC Monitor</h1>

            <input
                type="text"
                placeholder="Search tag..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                style={{
                    width: "300px",
                    padding: "8px",
                    marginBottom: "20px"
                }}
            />

            <table border="1" cellPadding="8" width="100%">
                <thead>
                    <tr>
                        <th>Tag</th>
                        <th>Type</th>
                        <th>Address</th>
                        <th>Value</th>
                        <th>Comment</th>
                    </tr>
                </thead>

                <tbody>
                    {filtered.map((item, index) => (
                        <tr key={index}>
                            <td>{item.tag}</td>
                            <td>{item.type}</td>
                            <td>{item.address}</td>
                            <td>
                                {typeof item.value === "boolean"
                                    ? item.value
                                        ? "ON"
                                        : "OFF"
                                    : item.value}
                            </td>
                            <td>{item.comment}</td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
}

export default LiveMonitor;