import {useEffect,useState} from "react";
import api from "../api/api";

export default function RecentEvent(){

    const [events,setEvents]=useState([]);

    async function load(){

        const res=await api.get("/dashboard");

        setEvents(res.data.events);

    }

    useEffect(()=>{

        load();

        const timer=setInterval(load,1000);

        return ()=>clearInterval(timer);

    },[]);

    return(

        <div className="panel">

            <h2>Recent Events</h2>

            <table>

                <tbody>

                {

                    events.map((event,index)=>(

                        <tr key={index}>

                            <td>{event.time}</td>

                            <td>{event.message}</td>

                        </tr>

                    ))

                }

                </tbody>

            </table>

        </div>

    );

}