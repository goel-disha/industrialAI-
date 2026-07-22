import { useEffect,useState } from "react";
import api from "../api/api";

function DetailPanel({item}){

    const [relations,setRelations]=useState(null);

    useEffect(()=>{

        if(!item) return;

        if(item.type==="device"){

            api.get(`/relationships/${item.value.tag}`)

            .then(res=>setRelations(res.data));

        }

    },[item]);

    if(!item){

        return(

            <div
            style={{
                flex:1,
                padding:30
            }}
            >

                Click a Device

            </div>

        )

    }

    return(

        <div
        style={{
            flex:1,
            padding:30
        }}
        >

            <h2>

                {item.type.toUpperCase()}

            </h2>

            <pre>

                {JSON.stringify(item.value,null,4)}

            </pre>

            {

                relations&&

                <>

                    <h3>

                        Relationships

                    </h3>

                    <pre>

                        {JSON.stringify(relations,null,4)}

                    </pre>

                </>

            }

        </div>

    )

}

export default DetailPanel;