import { useEffect,useState } from "react";
import api from "../api/api";

function ExplorerTree({onSelect}){

    const [devices,setDevices]=useState([]);
    const [programs,setPrograms]=useState([]);

    useEffect(()=>{

        api.get("/devices")
        .then(res=>setDevices(res.data));

        api.get("/programs")
        .then(res=>setPrograms(res.data));

    },[]);

    return(

        <div
        style={{
            width:"300px",
            borderRight:"1px solid lightgray",
            paddingRight:20
        }}
        >

            <h3>Devices</h3>

            {

                devices.map(d=>

                    <div
                    key={d.id}
                    style={{
                        cursor:"pointer",
                        padding:5
                    }}
                    onClick={()=>onSelect({
                        type:"device",
                        value:d
                    })}
                    >

                        {d.tag}

                    </div>

                )

            }

            <hr/>

            <h3>Programs</h3>

            {

                programs.map(p=>

                    <div
                    key={p.id}
                    style={{
                        cursor:"pointer",
                        padding:5
                    }}
                    onClick={()=>onSelect({
                        type:"program",
                        value:p
                    })}
                    >

                        {p.program}

                    </div>

                )

            }

        </div>

    )

}

export default ExplorerTree;