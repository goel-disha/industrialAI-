import React, { useEffect, useState } from "react";
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  Chip,
  Divider,
  LinearProgress,
  IconButton,
  Tooltip,
} from "@mui/material";

import RefreshIcon from "@mui/icons-material/Refresh";
import PlayArrowIcon from "@mui/icons-material/PlayArrow";
import StopIcon from "@mui/icons-material/Stop";
import RestartAltIcon from "@mui/icons-material/RestartAlt";
import WarningAmberIcon from "@mui/icons-material/WarningAmber";
import CheckCircleIcon from "@mui/icons-material/CheckCircle";
import ErrorIcon from "@mui/icons-material/Error";
import SettingsIcon from "@mui/icons-material/Settings";
import MemoryIcon from "@mui/icons-material/Memory";
import PrecisionManufacturingIcon from "@mui/icons-material/PrecisionManufacturing";
import AIHealthPanel from "../components/ai/AIHealthPanel";
import AICyclePanel from "../components/ai/AICyclePanel";

import "../styles/dashboard.css";

const API = import.meta.env.VITE_API_URL || "http://localhost:8000";

function Dashboard() {
  const [project, setProject] = useState({});
  const [machine, setMachine] = useState({});
  const [live, setLive] = useState({});
  const [alarms, setAlarms] = useState([]);
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);

  // ==========================================================
  // LOAD DASHBOARD DATA
  // ==========================================================

  const loadDashboard = async () => {
    try {
      const [
        projectRes,
        machineRes,
        liveRes,
        alarmsRes,
        eventsRes,
      ] = await Promise.all([
        fetch(`${API}/project`),
        fetch(`${API}/machine`),
        fetch(`${API}/live`),
        fetch(`${API}/alarms`),
        fetch(`${API}/events`),
      ]);

      const [
        projectData,
        machineData,
        liveData,
        alarmsData,
        eventsData,
      ] = await Promise.all([
        projectRes.json(),
        machineRes.json(),
        liveRes.json(),
        alarmsRes.json(),
        eventsRes.json(),
      ]);

      setProject(projectData || {});
      setMachine(machineData || {});
      setLive(liveData || {});

      setAlarms(
        Array.isArray(alarmsData)
          ? alarmsData
          : alarmsData?.alarms || []
      );

      setEvents(
        Array.isArray(eventsData)
          ? eventsData
          : eventsData?.events || []
      );

      setLoading(false);
    } catch (error) {
      console.error("Dashboard loading error:", error);
      setLoading(false);
    }
  };

  // ==========================================================
  // INITIAL + LIVE UPDATE
  // ==========================================================

  useEffect(() => {
    loadDashboard();

    const interval = setInterval(() => {
      loadDashboard();
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  // ==========================================================
  // CONTROL
  // ==========================================================

  const control = async (endpoint) => {
    try {
      setActionLoading(true);

      await fetch(`${API}${endpoint}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
      });

      await loadDashboard();
    } catch (error) {
      console.error("Control error:", error);
    } finally {
      setActionLoading(false);
    }
  };

  // ==========================================================
  // HELPERS
  // ==========================================================

  const getMachineState = () => {
    return (
      machine.state ||
      live.machine?.state ||
      live.state ||
      "IDLE"
    );
  };

  const getModel = () => {
    return (
      machine.model ||
      live.machine?.model ||
      1
    );
  };

  const isRunning = () => {
    const state = getMachineState();

    return (
      state !== "IDLE" &&
      state !== "STOPPED" &&
      state !== "EMERGENCY"
    );
  };

  const safety = live.safety || machine.safety || {};

  const servo = live.servo || machine.servo || {};

  const centering =
    live.centering ||
    machine.centering ||
    {};

  const production =
    live.production ||
    machine.production ||
    {};

  const sequence =
    live.sequence ||
    machine.sequence ||
    {};

  const axis1 = servo.axis1 || {};
  const axis2 = servo.axis2 || {};
  const axis3 = servo.axis3 || {};

  const activeAlarms = alarms.filter(
    (alarm) =>
      alarm.active === true ||
      alarm.status === "ACTIVE"
  );

  // ==========================================================
  // LOADING
  // ==========================================================

  if (loading) {
    return (
      <Box className="dashboard-loading">
        <Typography>
          Loading IndustrialAI Dashboard...
        </Typography>

        <LinearProgress />
      </Box>
    );
  }

  // ==========================================================
  // DASHBOARD
  // ==========================================================

  return (
    <Box className="dashboard">

      {/* =====================================================
          HEADER
      ===================================================== */}

      <Box className="dashboard-header">

        <Box>
          <Typography className="dashboard-title">
            IndustrialAI
          </Typography>

          <Typography className="dashboard-subtitle">
            AUTO TAPPING · Mitsubishi MELSEC-Q
          </Typography>
        </Box>

        <Box className="header-actions">

          <Chip
            icon={
              safety.safe === false
                ? <ErrorIcon />
                : <CheckCircleIcon />
            }
            label={
              safety.safe === false
                ? "UNSAFE"
                : "SYSTEM SAFE"
            }
            className={
              safety.safe === false
                ? "chip-danger"
                : "chip-success"
            }
          />

          <Tooltip title="Refresh">

            <IconButton
              onClick={loadDashboard}
              className="refresh-button"
            >
              <RefreshIcon />
            </IconButton>

          </Tooltip>

        </Box>

      </Box>

      {/* =====================================================
          TOP STATUS CARDS
      ===================================================== */}

      <Grid container spacing={2}>

        <Grid item xs={12} md={3}>
          <StatusCard
            title="Machine State"
            value={getMachineState()}
            icon={<PrecisionManufacturingIcon />}
            status={isRunning() ? "running" : "idle"}
          />
        </Grid>

        <Grid item xs={12} md={3}>
          <StatusCard
            title="Selected Model"
            value={`MODEL ${getModel()}`}
            icon={<SettingsIcon />}
            status="normal"
          />
        </Grid>

        <Grid item xs={12} md={3}>
          <StatusCard
            title="Cycle Status"
            value={
              production.cycle_running ||
              machine.cycle_running
                ? "RUNNING"
                : "READY"
            }
            icon={<MemoryIcon />}
            status={
              production.cycle_running
                ? "running"
                : "normal"
            }
          />
        </Grid>

        <Grid item xs={12} md={3}>
          <StatusCard
            title="Active Alarms"
            value={activeAlarms.length}
            icon={<WarningAmberIcon />}
            status={
              activeAlarms.length
                ? "danger"
                : "normal"
            }
          />
        </Grid>

      </Grid>

      {/* =====================================================
          MACHINE + SERVO
      ===================================================== */}

      <Grid
        container
        spacing={2}
        className="dashboard-section"
      >

        {/* MACHINE SEQUENCE */}

        <Grid item xs={12} md={7}>
          <Card className="dashboard-card">

            <CardContent>

              <SectionTitle
                title="Machine Sequence"
                subtitle="Real-time automatic cycle"
              />

              <Box className="sequence-container">

                <SequenceStep
                  label="SERVO 1"
                  active={
                    sequence.state === "SERVO1" ||
                    getMachineState() === "SERVO1"
                  }
                  complete={
                    axis1.complete === true &&
                    axis1.position !== 0
                  }
                />

                <SequenceArrow />

                <SequenceStep
                  label="SERVO 2 / 3"
                  active={
                    sequence.state === "SERVO2_3_POS2" ||
                    sequence.state === "SERVO2_3_POS1"
                  }
                  complete={
                    axis2.complete === true &&
                    axis3.complete === true &&
                    axis2.position !== 0
                  }
                />

                <SequenceArrow />

                <SequenceStep
                  label="CENTER"
                  active={
                    sequence.state === "CENTER_FORWARD" ||
                    sequence.state === "CENTER_REVERSE"
                  }
                  complete={
                    centering.part_centered === true
                  }
                />

                <SequenceArrow />

                <SequenceStep
                  label="HOME"
                  active={
                    sequence.state === "RETURN_HOME"
                  }
                  complete={false}
                />

              </Box>

              <Divider sx={{ my: 2 }} />

              <Box className="machine-state-row">

                <Box>
                  <Typography className="small-label">
                    CURRENT STATE
                  </Typography>

                  <Typography className="large-value">
                    {getMachineState()}
                  </Typography>
                </Box>

                <Box>
                  <Typography className="small-label">
                    MODEL
                  </Typography>

                  <Typography className="large-value">
                    {getModel()}
                  </Typography>
                </Box>

                <Box>
                  <Typography className="small-label">
                    AUTO MODE
                  </Typography>

                  <Chip
                    label={
                      machine.auto_mode ||
                      live.auto_mode
                        ? "AUTO"
                        : "MANUAL"
                    }
                    className={
                      machine.auto_mode ||
                      live.auto_mode
                        ? "chip-success"
                        : "chip-warning"
                    }
                  />
                </Box>

              </Box>

            </CardContent>

          </Card>

        </Grid>

        {/* SAFETY */}

        <Grid item xs={12} md={5}>

          <Card className="dashboard-card">

            <CardContent>

              <SectionTitle
                title="Safety Status"
                subtitle="Machine safety interlocks"
              />

              <SafetyRow
                label="Emergency Stop"
                value={safety.emergency}
              />

              <SafetyRow
                label="Air Fault"
                value={safety.air_fault}
              />

              <SafetyRow
                label="System Safe"
                value={
                  safety.safe !== false
                }
                invert
              />

              <Divider sx={{ my: 2 }} />

              <Typography className="small-label">
                CENTERING
              </Typography>

              <Box className="center-status">

                <Chip
                  label="FORWARD"
                  className={
                    centering.forward
                      ? "chip-active"
                      : "chip-off"
                  }
                />

                <Chip
                  label="REVERSE"
                  className={
                    centering.reverse
                      ? "chip-active"
                      : "chip-off"
                  }
                />

                <Chip
                  label="REVERSE LIMIT"
                  className={
                    centering.reverse_limit
                      ? "chip-success"
                      : "chip-off"
                  }
                />

              </Box>

            </CardContent>

          </Card>

        </Grid>

      </Grid>

      {/* =====================================================
          SERVO AXES
      ===================================================== */}

      <Box className="dashboard-section">

        <Typography className="section-heading">
          Servo Axes
        </Typography>

        <Grid container spacing={2}>

          <Grid item xs={12} md={4}>
            <ServoCard
              axis="Axis 1"
              data={axis1}
              feedback={
                live.positions?.axis1 ??
                axis1.position ??
                0
              }
            />
          </Grid>

          <Grid item xs={12} md={4}>
            <ServoCard
              axis="Axis 2"
              data={axis2}
              feedback={
                live.positions?.axis2 ??
                axis2.position ??
                0
              }
            />
          </Grid>

          <Grid item xs={12} md={4}>
            <ServoCard
              axis="Axis 3"
              data={axis3}
              feedback={
                live.positions?.axis3 ??
                axis3.position ??
                0
              }
            />
          </Grid>


          <Grid item xs={12}>
            <AIHealthPanel />
          </Grid>

          <Grid item xs={12}>
            <AICyclePanel />
          </Grid>

        </Grid>

      </Box>

      {/* =====================================================
          PRODUCTION
      ===================================================== */}

      <Grid
        container
        spacing={2}
        className="dashboard-section"
      >

        <Grid item xs={12} md={7}>

          <Card className="dashboard-card">

            <CardContent>

              <SectionTitle
                title="Production"
                subtitle="Cycle statistics"
              />

              <Grid container spacing={2}>

                <ProductionMetric
                  label="Total Cycles"
                  value={
                    production.total ??
                    production.total_cycles ??
                    0
                  }
                />

                <ProductionMetric
                  label="Completed"
                  value={
                    production.completed ??
                    production.completed_cycles ??
                    0
                  }
                />

                <ProductionMetric
                  label="Rejected"
                  value={
                    production.rejected ??
                    production.rejected_cycles ??
                    0
                  }
                />

                <ProductionMetric
                  label="Current Cycle"
                  value={
                    production.current ??
                    production.current_cycle ??
                    0
                  }
                />

              </Grid>

            </CardContent>

          </Card>

        </Grid>

        {/* PROJECT INFO */}

        <Grid item xs={12} md={5}>

          <Card className="dashboard-card">

            <CardContent>

              <SectionTitle
                title="System Information"
                subtitle="Engineering database"
              />

              <InfoRow
                label="PLC"
                value={
                  project.plc ||
                  "Mitsubishi MELSEC-Q"
                }
              />

              <InfoRow
                label="Servo Devices"
                value={
                  project.servo_devices ??
                  project.devices ??
                  0
                }
              />

              <InfoRow
                label="Programs"
                value={
                  project.programs ?? 0
                }
              />

              <InfoRow
                label="Statements"
                value={
                  project.statements ?? 0
                }
              />

              <InfoRow
                label="Version"
                value={
                  project.version || "1.0"
                }
              />

            </CardContent>

          </Card>

        </Grid>

      </Grid>

      {/* =====================================================
          MACHINE CONTROLS
      ===================================================== */}

      <Card className="dashboard-card dashboard-section">

        <CardContent>

          <SectionTitle
            title="Machine Control"
            subtitle="Operator commands"
          />

          <Box className="control-panel">

            <Button
              variant="contained"
              startIcon={<PlayArrowIcon />}
              disabled={actionLoading}
              className="control-start"
              onClick={() =>
                control("/control/start")
              }
            >
              START
            </Button>

            <Button
              variant="contained"
              startIcon={<StopIcon />}
              disabled={actionLoading}
              className="control-stop"
              onClick={() =>
                control("/control/stop")
              }
            >
              STOP
            </Button>

            <Button
              variant="contained"
              startIcon={<ErrorIcon />}
              disabled={actionLoading}
              className="control-emergency"
              onClick={() =>
                control("/control/emergency")
              }
            >
              EMERGENCY STOP
            </Button>

            <Button
              variant="outlined"
              startIcon={<RestartAltIcon />}
              disabled={actionLoading}
              className="control-reset"
              onClick={() =>
                control("/control/reset")
              }
            >
              RESET
            </Button>

          </Box>

        </CardContent>

      </Card>

      {/* =====================================================
          ALARMS + EVENTS
      ===================================================== */}

      <Grid
        container
        spacing={2}
        className="dashboard-section"
      >

        <Grid item xs={12} md={6}>

          <Card className="dashboard-card">

            <CardContent>

              <SectionTitle
                title="Active Alarms"
                subtitle={`${activeAlarms.length} active`}
              />

              {activeAlarms.length === 0 ? (

                <EmptyState
                  icon={<CheckCircleIcon />}
                  text="No active alarms"
                />

              ) : (

                activeAlarms
                  .slice(0, 6)
                  .map((alarm, index) => (

                    <AlarmRow
                      key={alarm.id || index}
                      alarm={alarm}
                    />

                  ))

              )}

            </CardContent>

          </Card>

        </Grid>

        <Grid item xs={12} md={6}>

          <Card className="dashboard-card">

            <CardContent>

              <SectionTitle
                title="Recent Events"
                subtitle="Latest machine activity"
              />

              {events.length === 0 ? (

                <EmptyState
                  icon={<MemoryIcon />}
                  text="No recent events"
                />

              ) : (

                events
                  .slice(0, 6)
                  .map((event, index) => (

                    <EventRow
                      key={event.id || index}
                      event={event}
                    />

                  ))

              )}

            </CardContent>

          </Card>

        </Grid>

      </Grid>

    </Box>
  );
}


// ==========================================================
// COMPONENTS
// ==========================================================

function StatusCard({
  title,
  value,
  icon,
  status,
}) {
  return (
    <Card className={`status-card ${status}`}>

      <CardContent>

        <Box className="status-card-top">

          <Box className="status-icon">
            {icon}
          </Box>

          <Typography className="small-label">
            {title}
          </Typography>

        </Box>

        <Typography className="status-value">
          {value}
        </Typography>

      </CardContent>

    </Card>
  );
}


function SectionTitle({
  title,
  subtitle,
}) {
  return (
    <Box className="section-title">

      <Typography className="card-title">
        {title}
      </Typography>

      <Typography className="card-subtitle">
        {subtitle}
      </Typography>

    </Box>
  );
}


function SequenceStep({
  label,
  active,
  complete,
}) {
  return (
    <Box
      className={`sequence-step ${
        active ? "active" : ""
      } ${complete ? "complete" : ""}`}
    >

      <Box className="sequence-dot">
        {complete ? "✓" : ""}
      </Box>

      <Typography>
        {label}
      </Typography>

    </Box>
  );
}


function SequenceArrow() {
  return (
    <Typography className="sequence-arrow">
      →
    </Typography>
  );
}


function SafetyRow({
  label,
  value,
  invert = false,
}) {
  const safe = invert
    ? value
    : !value;

  return (
    <Box className="safety-row">

      <Typography>
        {label}
      </Typography>

      <Chip
        label={safe ? "OK" : "FAULT"}
        className={
          safe
            ? "chip-success"
            : "chip-danger"
        }
      />

    </Box>
  );
}


function ServoCard({
  axis,
  data,
  feedback,
}) {
  const position =
    Number(feedback) || 0;

  const target =
    Number(data.target) || 0;

  const progress =
    target !== 0
      ? Math.min(
          100,
          Math.abs(position / target) * 100
        )
      : position === 0
        ? 100
        : 0;

  return (
    <Card className="servo-card">

      <CardContent>

        <Box className="servo-header">

          <Typography className="servo-name">
            {axis}
          </Typography>

          <Chip
            label={
              data.busy
                ? "MOVING"
                : data.complete
                  ? "COMPLETE"
                  : "IDLE"
            }
            className={
              data.busy
                ? "chip-active"
                : data.complete
                  ? "chip-success"
                  : "chip-off"
            }
          />

        </Box>

        <Box className="servo-position">

          <Box>
            <Typography className="small-label">
              POSITION
            </Typography>

            <Typography className="servo-value">
              {position}
            </Typography>
          </Box>

          <Box>
            <Typography className="small-label">
              TARGET
            </Typography>

            <Typography className="servo-target">
              {target}
            </Typography>
          </Box>

        </Box>

        <LinearProgress
          variant="determinate"
          value={progress}
          className="servo-progress"
        />

      </CardContent>

    </Card>
  );
}


function ProductionMetric({
  label,
  value,
}) {
  return (
    <Grid item xs={6} md={3}>

      <Box className="production-metric">

        <Typography className="small-label">
          {label}
        </Typography>

        <Typography className="production-value">
          {value}
        </Typography>

      </Box>

    </Grid>
  );
}


function InfoRow({
  label,
  value,
}) {
  return (
    <Box className="info-row">

      <Typography className="small-label">
        {label}
      </Typography>

      <Typography>
        {value}
      </Typography>

    </Box>
  );
}


function AlarmRow({ alarm }) {
  return (
    <Box className="alarm-row">

      <WarningAmberIcon />

      <Box>
        <Typography className="alarm-title">
          {alarm.message ||
            alarm.description ||
            alarm.name ||
            "Machine Alarm"}
        </Typography>

        <Typography className="alarm-time">
          {alarm.timestamp ||
            alarm.time ||
            ""}
        </Typography>
      </Box>

    </Box>
  );
}


function EventRow({ event }) {
  return (
    <Box className="event-row">

      <Box className="event-dot" />

      <Box>

        <Typography className="event-title">
          {event.message ||
            event.description ||
            event.event ||
            "Machine event"}
        </Typography>

        <Typography className="event-time">
          {event.timestamp ||
            event.time ||
            ""}
        </Typography>

      </Box>

    </Box>
  );
}


function EmptyState({
  icon,
  text,
}) {
  return (
    <Box className="empty-state">

      {icon}

      <Typography>
        {text}
      </Typography>

    </Box>
  );
}

export default Dashboard;