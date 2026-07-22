import Sidebar from "../components/sidebar";
import Toolbar from "../components/toolbar";

import "../styles/layout.css";

export default function MainLayout({children}){

    return(

        <div className="layout">

            <Sidebar/>

            <div className="content">

                <Topbar/>

                <div className="page">

                    {children}

                </div>

            </div>

        </div>

    );

}