import { useState } from "react";

import "../styles/explorer.css";
import ExplorerTree from "../components/explorertree";
import DetailPanel from "../components/detailpanel";
import SearchBox from "../components/searchbox";

function Explorer(){

    const [selected,setSelected]=useState(null);

    return(

        <div>

            <h1>Engineering Explorer</h1>

            <SearchBox/>

            <div
            style={{
                display:"flex",
                marginTop:20
            }}
            >

                <ExplorerTree
                onSelect={setSelected}
                />

                <DetailPanel
                item={selected}
                />

            </div>

        </div>

    )

}

export default Explorer;