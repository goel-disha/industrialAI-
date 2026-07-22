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

    if(!project){

        return <CircularProgress/>

    }

    return(

        <>

        <Typography
        variant="h4"
        mb={3}
        >

            IndustrialAI Dashboard

        </Typography>

        <Grid container spacing={3}>

            <Grid item xs={3}>

                <DashboardCard
                title="Devices"
                value={project.devices}
                />

            </Grid>

            <Grid item xs={3}>

                <DashboardCard
                title="Programs"
                value={project.programs}
                />

            </Grid>

            <Grid item xs={3}>

                <DashboardCard
                title="Motion"
                value={project.motion_parameters}
                />

            </Grid>

            <Grid item xs={3}>

                <DashboardCard
                title="Positions"
                value={project.positions}
                />

            </Grid>

            <Grid item xs={12}>

                <MachineFlow/>

            </Grid>

            <Grid item xs={4}>

                <MachineStatus
                live={live}
                />

            </Grid>

            <Grid item xs={8}>

                <ServoPanel
                live={live}
                />

            </Grid>

            <Grid item xs={12}>

                <RecentEvents/>

            </Grid>

            <div className="top-row">

               <MachineStatus />

               <ServoPanel />

            </div>

            <ProductionPanel />

            <RecentEvents />

        </Grid>

        </>

    )

}

export default Dashboard;