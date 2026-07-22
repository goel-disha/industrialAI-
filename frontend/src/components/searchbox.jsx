import { useState } from "react";
import api from "../api/api";

function SearchBox(){

    const [query,setQuery]=useState("");

    const [result,setResult]=useState([]);

    function search(){

        api.get(`/search?query=${query}`)

        .then(res=>setResult(res.data.devices));

    }

    return(

        <div>

            <input

            value={query}

            onChange={(e)=>setQuery(e.target.value)}

            placeholder="Search Device"

            />

            <button

            onClick={search}

            >

                Search

            </button>

            {

                result.map(r=>

                    <div key={r.id}>

                        {r.tag}

                    </div>

                )

            }

        </div>

    )

}

export default SearchBox;