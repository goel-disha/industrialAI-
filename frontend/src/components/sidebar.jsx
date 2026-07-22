import { NavLink } from "react-router-dom";

export default function Sidebar(){

    return(

        <div className="sidebar">

            <h2>IndustrialAI</h2>

            <NavLink to="/">

                Dashboard

            </NavLink>

            <NavLink to="/live">

                Live Monitor

            </NavLink>

            <NavLink to="/explorer">

                Explorer

            </NavLink>

            <NavLink to="/analytics">

                Analytics

            </NavLink>

            <NavLink to="/ai">

                AI Assistant

            </NavLink>

        </div>

    );

}