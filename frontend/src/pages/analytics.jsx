import { useEffect, useState } from "react";
import api from "../api/api";
import "../styles/analytics.css";

export default function Analytics() {

    const [data, setData] = useState({});

    async function load() {

        try {

            const res = await api.get("/dashboard");

            setData(res.data);

        }

        catch(err){

            console.log(err);

        }

    }

    useEffect(()=>{

        load();

        const timer=setInterval(load,1000);

        return ()=>clearInterval(timer);

    },[]);

    const progress=Math.min(

        (data.boxes_today||0)/500*100,

        100

    );

    return(

        <div className="analytics">

            <h1>Analytics</h1>

            <div className="card-grid">

                <div className="card">

                    <h3>Boxes Today</h3>

                    <p>{data.boxes_today}</p>

                </div>

                <div className="card">

                    <h3>Cycle Time</h3>

                    <p>{data.cycle_time} sec</p>

                </div>

                <div className="card">

                    <h3>Axis Position</h3>

                    <p>{data.axis_position}</p>

                </div>

                <div className="card">

                    <h3>Axis Speed</h3>

                    <p>{data.axis_speed}</p>

                </div>

            </div>

            <div className="panel">

                <h2>Production Progress</h2>

                <div className="progress">

                    <div

                        className="progress-fill"

                        style={{width:`${progress}%`}}

                    />

                </div>

                <p>{progress.toFixed(0)}%</p>

            </div>

            <div className="panel">

                <h2>Machine Statistics</h2>

                <table>

                    <tbody>

                        <tr>

                            <td>Machine</td>

                            <td>{data.machine}</td>

                        </tr>

                        <tr>

                            <td>Status</td>

                            <td>{data.status}</td>

                        </tr>

                        <tr>

                            <td>Program</td>

                            <td>{data.program}</td>

                        </tr>

                        <tr>

                            <td>Running</td>

                            <td>{data.running?"YES":"NO"}</td>

                        </tr>

                    </tbody>

                </table>

            </div>

            <div className="panel">

                <h2>Recent Events</h2>

                <table>

                    <tbody>

                        {

                            (data.events||[]).map((event,index)=>(

                                <tr key={index}>

                                    <td>{event.time}</td>

                                    <td>{event.message}</td>

                                </tr>

                            ))

                        }

                    </tbody>

                </table>

            </div>

        </div>

    );

}