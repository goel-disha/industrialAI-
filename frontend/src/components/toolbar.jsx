import { useEffect, useState } from "react";

export default function Toolbar(){

    const [time,setTime]=useState(new Date());

    useEffect(()=>{

        const t=setInterval(()=>{

            setTime(new Date());

        },1000);

        return ()=>clearInterval(t);

    },[]);

    return(

        <div className="toolbar">

            <h2>

                Mitsubishi Auto Tapping Machine

            </h2>

            <span>

                {time.toLocaleTimeString()}

            </span>

        </div>

    );

}