import { useEffect, useState } from "react";
import api from "../api/api";

export default function ProductionPanel() {

    const [data, setData] = useState({});

    async function loadProduction() {

        try {

            const res = await api.get("/dashboard");

            setData(res.data);

        } catch (err) {

            console.error(err);

        }

    }

    useEffect(() => {

        loadProduction();

        const timer = setInterval(loadProduction, 1000);

        return () => clearInterval(timer);

    }, []);

    return (

        <div className="panel">

            <h2>Production</h2>

            <table>

                <tbody>

                    <tr>
                        <td>Boxes Today</td>
                        <td>{data.boxes_today}</td>
                    </tr>

                    <tr>
                        <td>Cycle Time</td>
                        <td>{data.cycle_time} sec</td>
                    </tr>

                    <tr>
                        <td>Program</td>
                        <td>{data.program}</td>
                    </tr>

                    <tr>
                        <td>Machine</td>
                        <td>{data.machine}</td>
                    </tr>

                    <tr>
                        <td>Status</td>
                        <td>{data.state}</td>
                    </tr>

                </tbody>

            </table>

        </div>

    );

}