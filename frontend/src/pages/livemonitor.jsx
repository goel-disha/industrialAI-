import React, { useEffect, useState } from "react";
import {
  Box,
  Card,
  CardContent,
  Grid,
  Typography,
  Chip,
  LinearProgress,
  Divider,
} from "@mui/material";

import "../styles/livemonitor.css";

const API = import.meta.env.VITE_API_URL || "http://localhost:8000";

export default function LiveMonitor() {
  const [data, setData] = useState(null);
  const [telemetry, setTelemetry] = useState([]);
  const [sequenceHistory, setSequenceHistory] = useState([]);
  const [cycleData, setCycleData] = useState(null);
  const [loading, setLoading] = useState(true);

  /* ==========================================================
     LOAD LIVE MACHINE DATA
     ========================================================== */

  const loadLive = async () => {
    try {
      const [
        liveResponse,
        telemetryResponse,
        sequenceResponse,
        cycleResponse,
      ] = await Promise.all([
        fetch(`${API}/live`),
        fetch(`${API}/telemetry/history?limit=100`),
        fetch(`${API}/telemetry/sequence?limit=20`),
        fetch(`${API}/telemetry/cycle`),
      ]);

      const liveResult = await liveResponse.json();
      const telemetryResult = await telemetryResponse.json();
      const sequenceResult = await sequenceResponse.json();
      const cycleResult = await cycleResponse.json();

      setData(liveResult);

      setTelemetry(
        Array.isArray(telemetryResult?.data)
          ? telemetryResult.data
          : []
      );

      setSequenceHistory(
        Array.isArray(sequenceResult?.data)
          ? sequenceResult.data
          : []
      );

      setCycleData(cycleResult?.data || null);

      setLoading(false);
    } catch (error) {
      console.error("Live monitor error:", error);
      setLoading(false);
    }
  };

  /* ==========================================================
     REAL-TIME POLLING
     ========================================================== */

  useEffect(() => {
    loadLive();

    const interval = setInterval(loadLive, 500);

    return () => clearInterval(interval);
  }, []);

  /* ==========================================================
     LOADING
     ========================================================== */

  if (loading) {
    return (
      <Box className="live-loading">
        <Typography>
          Loading Live Monitor...
        </Typography>

        <LinearProgress sx={{ mt: 2 }} />
      </Box>
    );
  }

  /* ==========================================================
     DATA
     ========================================================== */

  const machine = data?.machine || {};
  const safety = data?.safety || {};
  const servo = data?.servo || {};
  const centering = data?.centering || {};
  const sequence = data?.sequence || {};
  const production = data?.production || {};
  const engine = data?.engine || {};
  const servoStatus = data?.servo_status || {};

  const axis1 = servo.axis1 || {};
  const axis2 = servo.axis2 || {};
  const axis3 = servo.axis3 || {};

  /* ==========================================================
     CYCLE
     ========================================================== */

  const cycleNumber =
    cycleData?.cycle_number ??
    machine.cycle_number ??
    production.current ??
    0;

  const cycleRunning =
    cycleData?.running ??
    machine.cycle_running ??
    production.cycle_running ??
    false;

  const cycleDuration =
    cycleData?.current_duration ??
    machine.cycle_duration ??
    0;

  const lastCycleDuration =
    cycleData?.last_cycle_duration ??
    machine.cycle_duration ??
    0;

  /* ==========================================================
     SAFETY
     ========================================================== */

  const emergency = Boolean(safety.emergency);
  const airFault = Boolean(safety.air_fault);
  const cycleStop = Boolean(safety.cycle_stop);

  const systemSafe =
    !emergency &&
    !airFault;

  /* ==========================================================
     RENDER
     ========================================================== */

  return (
    <Box className="live-monitor">

      {/* ======================================================
          HEADER
      ====================================================== */}

      <Box className="live-header">

        <Box>
          <Typography className="live-title">
            Live Monitor
          </Typography>

          <Typography className="live-subtitle">
            Real-time digital twin of Mitsubishi AUTO TAPPING machine
          </Typography>
        </Box>

        <Chip
          label={
            systemSafe
              ? "SYSTEM SAFE"
              : "UNSAFE"
          }
          className={
            systemSafe
              ? "chip-success"
              : "chip-danger"
          }
        />

      </Box>


      {/* ======================================================
          MACHINE OVERVIEW
      ====================================================== */}

      <Grid container spacing={2}>

        <Grid item xs={12} sm={6} md={3}>
          <MonitorCard
            title="Machine State"
            value={
              machine.state ||
              sequence.state ||
              "IDLE"
            }
          />
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <MonitorCard
            title="Model"
            value={`MODEL ${machine.model || 1}`}
          />
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <MonitorCard
            title="Cycle"
            value={
              cycleRunning
                ? `RUNNING #${cycleNumber}`
                : `COMPLETE #${cycleNumber}`
            }
          />
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <MonitorCard
            title="Sequence"
            value={
              sequence.state ||
              machine.state ||
              "IDLE"
            }
          />
        </Grid>

      </Grid>


      {/* ======================================================
          CYCLE INFORMATION
      ====================================================== */}

      <Box className="live-section">

        <Typography className="section-heading">
          Production & Cycle
        </Typography>

        <Grid container spacing={2}>

          <Grid item xs={12} sm={6} md={3}>
            <MonitorCard
              title="Total Cycles"
              value={production.total ?? 0}
            />
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <MonitorCard
              title="Completed"
              value={production.completed ?? 0}
            />
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <MonitorCard
              title="Rejected"
              value={production.rejected ?? 0}
            />
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <MonitorCard
              title="Current Cycle Time"
              value={`${Number(cycleDuration).toFixed(2)} s`}
            />
          </Grid>

        </Grid>

        <Grid container spacing={2} sx={{ mt: 0.2 }}>

          <Grid item xs={12} md={6}>
            <InfoCard
              title="Cycle Status"
              value={
                cycleRunning
                  ? "Cycle Running"
                  : production.completed > 0
                    ? "Cycle Complete"
                    : "Machine Idle"
              }
            />
          </Grid>

          <Grid item xs={12} md={6}>
            <InfoCard
              title="Last Cycle Duration"
              value={`${Number(lastCycleDuration).toFixed(2)} s`}
            />
          </Grid>

        </Grid>

      </Box>


      {/* ======================================================
          SERVO AXES
      ====================================================== */}

      <Box className="live-section">

        <Typography className="section-heading">
          Servo Axes
        </Typography>

        <Grid container spacing={2}>

          <Grid item xs={12} md={4}>
            <ServoMonitor
              axis="Axis 1"
              data={axis1}
            />
          </Grid>

          <Grid item xs={12} md={4}>
            <ServoMonitor
              axis="Axis 2"
              data={axis2}
            />
          </Grid>

          <Grid item xs={12} md={4}>
            <ServoMonitor
              axis="Axis 3"
              data={axis3}
            />
          </Grid>

        </Grid>

      </Box>


      {/* ======================================================
          LIVE POSITION / SPEED
      ====================================================== */}

      <Box className="live-section">

        <Typography className="section-heading">
          Live Motion Telemetry
        </Typography>

        <Grid container spacing={2}>

          <Grid item xs={12} md={6}>
            <TelemetryCard
              title="Position"
              telemetry={telemetry}
              field="position"
              unit=""
            />
          </Grid>

          <Grid item xs={12} md={6}>
            <TelemetryCard
              title="Speed"
              telemetry={telemetry}
              field="speed"
              unit=""
            />
          </Grid>

        </Grid>

      </Box>


      {/* ======================================================
          SERVO STATUS
      ====================================================== */}

      <Box className="live-section">

        <Typography className="section-heading">
          Servo System Status
        </Typography>

        <Card className="live-card">

          <CardContent>

            <Grid container spacing={2}>

              <Grid item xs={6} sm={3}>
                <StatusMetric
                  label="Servo Ready"
                  active={Boolean(servoStatus.ready)}
                />
              </Grid>

              <Grid item xs={6} sm={3}>
                <StatusMetric
                  label="Servo Busy"
                  active={Boolean(servoStatus.busy)}
                  activeLabel="BUSY"
                />
              </Grid>

              <Grid item xs={6} sm={3}>
                <StatusMetric
                  label="Servo Error"
                  active={Boolean(servoStatus.error)}
                  activeLabel="ERROR"
                  danger
                />
              </Grid>

              <Grid item xs={6} sm={3}>
                <StatusMetric
                  label="Position Reached"
                  active={Boolean(
                    servoStatus.position_reached
                  )}
                />
              </Grid>

            </Grid>

          </CardContent>

        </Card>

      </Box>


      {/* ======================================================
          SAFETY + CENTERING
      ====================================================== */}

      <Grid
        container
        spacing={2}
        className="live-section"
      >

        {/* SAFETY */}

        <Grid item xs={12} md={6}>

          <Card className="live-card">

            <CardContent>

              <Typography className="card-title">
                Safety
              </Typography>

              <Divider sx={{ my: 2 }} />

              <LiveRow
                label="Emergency"
                value={emergency}
                danger
              />

              <LiveRow
                label="Air Fault"
                value={airFault}
                danger
              />

              <LiveRow
                label="Cycle Stop"
                value={cycleStop}
                danger
              />

              <LiveRow
                label="System Safe"
                value={systemSafe}
                invert
              />

            </CardContent>

          </Card>

        </Grid>


        {/* CENTERING */}

        <Grid item xs={12} md={6}>

          <Card className="live-card">

            <CardContent>

              <Typography className="card-title">
                Centering
              </Typography>

              <Divider sx={{ my: 2 }} />

              <LiveRow
                label="Forward"
                value={Boolean(
                  centering.forward
                )}
              />

              <LiveRow
                label="Reverse"
                value={Boolean(
                  centering.reverse
                )}
              />

              <LiveRow
                label="Forward Limit"
                value={Boolean(
                  centering.forward_limit
                )}
              />

              <LiveRow
                label="Reverse Limit"
                value={Boolean(
                  centering.reverse_limit
                )}
              />

              <LiveRow
                label="Part Centered"
                value={Boolean(
                  centering.part_centered
                )}
              />

            </CardContent>

          </Card>

        </Grid>

      </Grid>


      {/* ======================================================
          SEQUENCE HISTORY
      ====================================================== */}

      <Box className="live-section">

        <Typography className="section-heading">
          Sequence Timeline
        </Typography>

        <Card className="live-card">

          <CardContent>

            {sequenceHistory.length === 0 ? (

              <Typography className="small-label">
                No sequence transitions recorded yet.
              </Typography>

            ) : (

              <Box className="sequence-timeline">

                {[...sequenceHistory]
                  .reverse()
                  .map((item, index) => (

                    <Box
                      key={`${item.scan}-${index}`}
                      className="sequence-item"
                      sx={{
                        mb: 2,
                        pb: 2,
                        borderBottom:
                          "1px solid rgba(255,255,255,0.08)",
                      }}
                    >

                      <Box
                        sx={{
                          display: "flex",
                          justifyContent:
                            "space-between",
                          alignItems: "center",
                          gap: 2,
                          flexWrap: "wrap",
                        }}
                      >

                        <Typography
                          sx={{
                            fontWeight: 600,
                          }}
                        >
                          {item.from_state}
                          {" → "}
                          {item.to_state}
                        </Typography>

                        <Chip
                          size="small"
                          label={`Cycle ${item.cycle_number}`}
                          className="chip-off"
                        />

                      </Box>

                      <Typography
                        className="small-label"
                        sx={{ mt: 0.5 }}
                      >
                        Model {item.model}
                        {" • "}
                        Scan {item.scan}
                        {" • "}
                        {formatTimestamp(
                          item.timestamp
                        )}
                      </Typography>

                    </Box>

                  ))}

              </Box>

            )}

          </CardContent>

        </Card>

      </Box>


      {/* ======================================================
          ENGINE INFORMATION
      ====================================================== */}

      <Box className="live-section">

        <Typography className="section-heading">
          Digital Twin Engine
        </Typography>

        <Grid container spacing={2}>

          <Grid item xs={12} sm={4}>
            <InfoCard
              title="Scan Count"
              value={engine.scan_count ?? 0}
            />
          </Grid>

          <Grid item xs={12} sm={4}>
            <InfoCard
              title="Telemetry Samples"
              value={
                engine.history_size ??
                telemetry.length
              }
            />
          </Grid>

          <Grid item xs={12} sm={4}>
            <InfoCard
              title="Engine Uptime"
              value={`${Number(
                engine.uptime ?? 0
              ).toFixed(1)} s`}
            />
          </Grid>

        </Grid>

      </Box>


      {/* ======================================================
          LAST UPDATE
      ====================================================== */}

      <Box
        sx={{
          mt: 3,
          mb: 2,
          textAlign: "right",
        }}
      >

        <Typography className="small-label">
          Last update:{" "}
          {formatTimestamp(
            data?.timestamp
          )}
        </Typography>

      </Box>

    </Box>
  );
}


/* ==========================================================
   MONITOR CARD
   ========================================================== */

function MonitorCard({ title, value }) {

  return (
    <Card className="monitor-card">

      <CardContent>

        <Typography className="small-label">
          {title}
        </Typography>

        <Typography className="monitor-value">
          {value}
        </Typography>

      </CardContent>

    </Card>
  );
}


/* ==========================================================
   INFO CARD
   ========================================================== */

function InfoCard({ title, value }) {

  return (
    <Card className="monitor-card">

      <CardContent>

        <Typography className="small-label">
          {title}
        </Typography>

        <Typography className="axis-value">
          {value}
        </Typography>

      </CardContent>

    </Card>
  );
}


/* ==========================================================
   SERVO MONITOR
   ========================================================== */

function ServoMonitor({ axis, data }) {

  const position =
    Number(data.position) || 0;

  const target =
    Number(data.target) || 0;

  const speed =
    Number(data.speed) || 0;

  const actualSpeed =
    Number(data.actual_speed) || 0;

  const positionError =
    Number(data.position_error) || 0;

  const distanceRemaining =
    Number(data.distance_remaining) || 0;

  /* ----------------------------------------------------------
     Position Progress
     ---------------------------------------------------------- */

  let progress = 0;

  if (target !== 0) {

    progress = Math.min(
      100,
      Math.max(
        0,
        Math.abs(position / target) * 100
      )
    );

  } else {

    progress =
      position === 0
        ? 100
        : 0;

  }

  /* ----------------------------------------------------------
     Status
     ---------------------------------------------------------- */

  let status = "IDLE";
  let statusClass = "chip-off";

  if (data.error) {

    status = "ERROR";
    statusClass = "chip-danger";

  } else if (data.busy) {

    status = "MOVING";
    statusClass = "chip-active";

  } else if (data.complete) {

    status = "COMPLETE";
    statusClass = "chip-success";
  }

  return (
    <Card className="servo-monitor-card">

      <CardContent>

        {/* HEADER */}

        <Box className="servo-monitor-header">

          <Typography className="card-title">
            {axis}
          </Typography>

          <Chip
            label={status}
            className={statusClass}
          />

        </Box>

        <Divider sx={{ my: 2 }} />


        {/* POSITION / TARGET */}

        <Grid container spacing={2}>

          <Grid item xs={6}>

            <Typography className="small-label">
              POSITION
            </Typography>

            <Typography className="axis-value">
              {formatNumber(position)}
            </Typography>

          </Grid>

          <Grid item xs={6}>

            <Typography className="small-label">
              TARGET
            </Typography>

            <Typography className="axis-value">
              {formatNumber(target)}
            </Typography>

          </Grid>

        </Grid>


        {/* POSITION PROGRESS */}

        <Typography
          className="small-label"
          sx={{ mt: 2 }}
        >
          POSITION PROGRESS
        </Typography>

        <LinearProgress
          variant="determinate"
          value={progress}
          sx={{ mt: 1 }}
        />

        <Typography
          className="small-label"
          sx={{
            mt: 0.5,
            textAlign: "right",
          }}
        >
          {progress.toFixed(1)}%
        </Typography>


        {/* SPEED */}

        <Grid
          container
          spacing={2}
          sx={{ mt: 0.5 }}
        >

          <Grid item xs={6}>

            <Typography className="small-label">
              COMMAND SPEED
            </Typography>

            <Typography className="axis-value">
              {formatNumber(speed)}
            </Typography>

          </Grid>

          <Grid item xs={6}>

            <Typography className="small-label">
              ACTUAL SPEED
            </Typography>

            <Typography className="axis-value">
              {formatNumber(actualSpeed)}
            </Typography>

          </Grid>

        </Grid>


        {/* POSITION ERROR */}

        <Grid
          container
          spacing={2}
          sx={{ mt: 0.5 }}
        >

          <Grid item xs={6}>

            <Typography className="small-label">
              POSITION ERROR
            </Typography>

            <Typography className="axis-value">
              {formatNumber(positionError)}
            </Typography>

          </Grid>

          <Grid item xs={6}>

            <Typography className="small-label">
              DISTANCE LEFT
            </Typography>

            <Typography className="axis-value">
              {formatNumber(distanceRemaining)}
            </Typography>

          </Grid>

        </Grid>


        {/* MOTION STATUS */}

        <Box sx={{ mt: 2 }}>

          <LiveRow
            label="Ready"
            value={Boolean(data.ready)}
          />

          <LiveRow
            label="Busy"
            value={Boolean(data.busy)}
          />

          <LiveRow
            label="Complete"
            value={Boolean(data.complete)}
          />

          <LiveRow
            label="Error"
            value={Boolean(data.error)}
            danger
          />

        </Box>

      </CardContent>

    </Card>
  );
}


/* ==========================================================
   TELEMETRY CARD
   ========================================================== */

function TelemetryCard({
  title,
  telemetry,
  field,
  unit = "",
}) {

  const axisData = {

    axis1:
      telemetry.length > 0
        ? telemetry[telemetry.length - 1]
            ?.axis1
        : {},

    axis2:
      telemetry.length > 0
        ? telemetry[telemetry.length - 1]
            ?.axis2
        : {},

    axis3:
      telemetry.length > 0
        ? telemetry[telemetry.length - 1]
            ?.axis3
        : {},
  };

  return (
    <Card className="live-card">

      <CardContent>

        <Typography className="card-title">
          {title}
        </Typography>

        <Divider sx={{ my: 2 }} />

        <TelemetryRow
          label="Axis 1"
          value={axisData.axis1?.[field]}
          unit={unit}
        />

        <TelemetryRow
          label="Axis 2"
          value={axisData.axis2?.[field]}
          unit={unit}
        />

        <TelemetryRow
          label="Axis 3"
          value={axisData.axis3?.[field]}
          unit={unit}
        />

        {/* MINI TREND */}

        <Box
          sx={{
            mt: 2,
            height: 90,
            overflow: "hidden",
            borderRadius: 1,
            background:
              "rgba(255,255,255,0.02)",
            p: 1,
          }}
        >

          <TelemetryTrend
            telemetry={telemetry}
            field={field}
          />

        </Box>

      </CardContent>

    </Card>
  );
}


/* ==========================================================
   TELEMETRY ROW
   ========================================================== */

function TelemetryRow({
  label,
  value,
  unit = "",
}) {

  return (
    <Box className="live-row">

      <Typography>
        {label}
      </Typography>

      <Typography
        sx={{
          fontWeight: 600,
        }}
      >
        {formatNumber(value)}
        {unit ? ` ${unit}` : ""}
      </Typography>

    </Box>
  );
}


/* ==========================================================
   TELEMETRY TREND
   ========================================================== */

function TelemetryTrend({
  telemetry,
  field,
}) {

  if (!telemetry || telemetry.length < 2) {

    return (
      <Typography className="small-label">
        Collecting telemetry...
      </Typography>
    );
  }

  const width = 600;
  const height = 70;
  const padding = 5;

  const series = [
    {
      key: "axis1",
      values: telemetry.map(
        (item) =>
          Number(
            item?.axis1?.[field]
          ) || 0
      ),
    },
    {
      key: "axis2",
      values: telemetry.map(
        (item) =>
          Number(
            item?.axis2?.[field]
          ) || 0
      ),
    },
    {
      key: "axis3",
      values: telemetry.map(
        (item) =>
          Number(
            item?.axis3?.[field]
          ) || 0
      ),
    },
  ];

  const allValues = series.flatMap(
    (item) => item.values
  );

  let min = Math.min(...allValues);
  let max = Math.max(...allValues);

  if (min === max) {
    min -= 1;
    max += 1;
  }

  const makePoints = (values) => {

    return values
      .map((value, index) => {

        const x =
          padding +
          (index /
            Math.max(
              1,
              values.length - 1
            )) *
            (width - padding * 2);

        const y =
          height -
          padding -
          ((value - min) /
            (max - min)) *
            (height - padding * 2);

        return `${x},${y}`;

      })
      .join(" ");
  };

  return (
    <svg
      width="100%"
      height="100%"
      viewBox={`0 0 ${width} ${height}`}
      preserveAspectRatio="none"
    >

      {/* GRID */}

      <line
        x1="0"
        y1="15"
        x2={width}
        y2="15"
        stroke="rgba(255,255,255,0.08)"
        strokeWidth="1"
      />

      <line
        x1="0"
        y1="35"
        x2={width}
        y2="35"
        stroke="rgba(255,255,255,0.08)"
        strokeWidth="1"
      />

      <line
        x1="0"
        y1="55"
        x2={width}
        y2="55"
        stroke="rgba(255,255,255,0.08)"
        strokeWidth="1"
      />


      {/* AXIS 1 */}

      <polyline
        points={makePoints(
          series[0].values
        )}
        fill="none"
        stroke="#42a5f5"
        strokeWidth="2"
      />


      {/* AXIS 2 */}

      <polyline
        points={makePoints(
          series[1].values
        )}
        fill="none"
        stroke="#66bb6a"
        strokeWidth="2"
      />


      {/* AXIS 3 */}

      <polyline
        points={makePoints(
          series[2].values
        )}
        fill="none"
        stroke="#ffa726"
        strokeWidth="2"
      />

    </svg>
  );
}


/* ==========================================================
   STATUS METRIC
   ========================================================== */

function StatusMetric({
  label,
  active,
  activeLabel = "ON",
  danger = false,
}) {

  return (
    <Box>

      <Typography className="small-label">
        {label}
      </Typography>

      <Chip
        label={
          active
            ? activeLabel
            : "OFF"
        }
        className={
          active
            ? danger
              ? "chip-danger"
              : "chip-success"
            : "chip-off"
        }
      />

    </Box>
  );
}


/* ==========================================================
   LIVE ROW
   ========================================================== */

function LiveRow({
  label,
  value,
  invert = false,
  danger = false,
}) {

  const active = Boolean(value);

  let labelText;

  if (invert) {
    labelText = active ? "ON" : "OFF";
  } else {
    labelText = active ? "ON" : "OFF";
  }

  let className = "chip-off";

  if (active) {

    if (danger) {
      className = "chip-danger";
    } else {
      className = "chip-success";
    }

  }

  return (
    <Box className="live-row">

      <Typography>
        {label}
      </Typography>

      <Chip
        label={labelText}
        className={className}
      />

    </Box>
  );
}


/* ==========================================================
   FORMAT NUMBER
   ========================================================== */

function formatNumber(value) {

  const number = Number(value);

  if (!Number.isFinite(number)) {
    return "0";
  }

  if (Number.isInteger(number)) {
    return number;
  }

  return number.toFixed(2);
}


/* ==========================================================
   FORMAT TIMESTAMP
   ========================================================== */

function formatTimestamp(timestamp) {

  if (!timestamp) {
    return "--";
  }

  try {

    return new Date(timestamp)
      .toLocaleTimeString();

  } catch {

    return "--";
  }
}