import { useEffect, useState } from "react";
import api from "../api/api";

export default function MachineStatus() {

    const [data, setData] = useState(null);

    async function loadDashboard() {
        try {
            const res = await api.get("/dashboard");
            setData(res.data);
        }
        catch (err) {
            console.log(err);
        }
    }

    useEffect(() => {

        loadDashboard();

        const timer = setInterval(loadDashboard, 1000);

        return () => clearInterval(timer);

    }, []);

    if (!data)
        return <div>Loading...</div>;

    return (

        <div className="panel">

            <h2>Machine Status</h2>

            <table>

                <tbody>

                    <tr>
                        <td>Machine</td>
                        <td>{data.machine}</td>
                    </tr>

                    <tr>
                        <td>State</td>
                        <td>{data.state}</td>
                    </tr>

                    <tr>
                        <td>Program</td>
                        <td>{data.program}</td>
                    </tr>

                    <tr>
                        <td>Running</td>
                        <td>{data.running ? "YES" : "NO"}</td>
                    </tr>

                    <tr>
                        <td>PLC</td>
                        <td>{data.plc}</td>
                    </tr>

                    <tr>
                        <td>Project</td>
                        <td>{data.project}</td>
                    </tr>

                </tbody>

            </table>

        </div>

    );
}