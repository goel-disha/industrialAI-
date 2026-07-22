import { useEffect, useState } from "react";
import { Grid, Typography, CircularProgress } from "@mui/material";

import api from "../api/api";

import DashboardCard from "../components/dasboard_card";
import MachineStatus from "../components/machine_status";
import MachineFlow from "../components/machineflow";
import ServoPanel from "../components/servopanel";
import RecentEvents from "../components/recentevent";
import ProductionPanel from "../components/production_panel";
import "../styles/dashboard.css";

function Dashboard() {

    const [project, setProject] = useState(null);
    const [live, setLive] = useState([]);

    useEffect(() => {

        loadProject();
        loadLive();

        const timer = setInterval(() => {loadLive();},1000);

        return () => clearInterval(timer);

    },[]);

    const loadProject = async() =>{

        try{

            const res = await api.get("/project");

            setProject(res.data);

        }

        catch(err){

            console.log(err);

        }

    }

    const loadLive = async()=>{

        try{

            const res = await api.get("/live");

            setLive(res.data);

        }

        catch(err){

            console.log(err);

        }

    }

    if (!project) {
     return <CircularProgress />;
    }

    return (
        <div>
          <h1>Dashboard Loaded</h1>

          <pre>{JSON.stringify(project, null, 2)}</pre>
        </div>
    );

}

export default Dashboard;