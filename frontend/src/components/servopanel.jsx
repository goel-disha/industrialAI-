import { useEffect, useState } from "react";
import api from "../api/api";

export default function ServoPanel() {

    const [servo, setServo] = useState({});

    async function loadServo() {

        try {

            const res = await api.get("/dashboard");

            setServo(res.data);

        } catch (err) {

            console.log(err);

        }

    }

    useEffect(() => {

        loadServo();

        const timer = setInterval(loadServo, 1000);

        return () => clearInterval(timer);

    }, []);

    return (

        <div className="panel">

            <h2>Servo</h2>

            <table>

                <tbody>

                    <tr>
                        <td>Position</td>
                        <td>{servo.axis_position}</td>
                    </tr>

                    <tr>
                        <td>Speed</td>
                        <td>{servo.axis_speed}</td>
                    </tr>

                    <tr>
                        <td>Running</td>
                        <td>{servo.running ? "YES" : "NO"}</td>
                    </tr>

                </tbody>

            </table>
            </div>
        
    );

}
