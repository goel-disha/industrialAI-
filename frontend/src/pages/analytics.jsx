import React, { useEffect, useMemo, useState } from "react";
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

import TrendingUpIcon from "@mui/icons-material/TrendingUp";
import SpeedIcon from "@mui/icons-material/Speed";
import WarningAmberIcon from "@mui/icons-material/WarningAmber";
import PrecisionManufacturingIcon from "@mui/icons-material/PrecisionManufacturing";
import TimerIcon from "@mui/icons-material/Timer";
import TimelineIcon from "@mui/icons-material/Timeline";

import "../styles/analytics.css";

const API = "http://localhost:8000";


export default function Analytics() {

  const [live, setLive] = useState({});
  const [history, setHistory] = useState([]);
  const [sequenceHistory, setSequenceHistory] = useState([]);
  const [cycleData, setCycleData] = useState({});
  const [alarms, setAlarms] = useState([]);
  const [events, setEvents] = useState([]);

  const [loading, setLoading] = useState(true);


  /* ==========================================================
     LOAD ANALYTICS DATA
     ========================================================== */

  const loadAnalytics = async () => {

    try {

      const [
        liveRes,
        historyRes,
        sequenceRes,
        cycleRes,
        alarmRes,
        eventRes,
      ] = await Promise.all([

        fetch(`${API}/live`),

        fetch(
          `${API}/telemetry/history?limit=300`
        ),

        fetch(
          `${API}/telemetry/sequence?limit=100`
        ),

        fetch(
          `${API}/telemetry/cycle`
        ),

        fetch(
          `${API}/alarms`
        ),

        fetch(
          `${API}/events`
        ),

      ]);


      const liveData =
        await liveRes.json();

      const historyData =
        await historyRes.json();

      const sequenceData =
        await sequenceRes.json();

      const cycleResult =
        await cycleRes.json();

      const alarmData =
        await alarmRes.json();

      const eventData =
        await eventRes.json();


      setLive(liveData || {});


      setHistory(
        Array.isArray(historyData?.data)
          ? historyData.data
          : []
      );


      setSequenceHistory(
        Array.isArray(sequenceData?.data)
          ? sequenceData.data
          : []
      );


      setCycleData(
        cycleResult?.data || {}
      );


      setAlarms(
        Array.isArray(alarmData)
          ? alarmData
          : alarmData?.alarms || []
      );


      setEvents(
        Array.isArray(eventData)
          ? eventData
          : eventData?.events || []
      );


      setLoading(false);

    } catch (error) {

      console.error(
        "Analytics error:",
        error
      );

      setLoading(false);
    }
  };


  /* ==========================================================
     REAL-TIME UPDATE
     ========================================================== */

  useEffect(() => {

    loadAnalytics();

    const timer =
      setInterval(
        loadAnalytics,
        1000
      );

    return () =>
      clearInterval(timer);

  }, []);


  /* ==========================================================
     BASIC DATA
     ========================================================== */

  const machine =
    live.machine || {};

  const production =
    live.production || {};

  const servo =
    live.servo || {};

  const axis1 =
    servo.axis1 || {};

  const axis2 =
    servo.axis2 || {};

  const axis3 =
    servo.axis3 || {};


  /* ==========================================================
     PRODUCTION
     ========================================================== */

  const total =
    Number(
      production.total ??
      production.total_cycles ??
      0
    );


  const completed =
    Number(
      production.completed ??
      production.completed_cycles ??
      0
    );


  const rejected =
    Number(
      production.rejected ??
      production.rejected_cycles ??
      0
    );


  const completionRate =
    total > 0
      ? (completed / total) * 100
      : 0;


  const rejectionRate =
    total > 0
      ? (rejected / total) * 100
      : 0;


  /* ==========================================================
     ALARMS
     ========================================================== */

  const activeAlarms =
    alarms.filter(
      (alarm) =>
        alarm.active === true ||
        alarm.status === "ACTIVE"
    ).length;


  /* ==========================================================
     CYCLE ANALYTICS
     ========================================================== */

  const cycleStats =
    useMemo(() => {

      const durations = [];

      /*
       * A completed cycle is represented by
       * a telemetry snapshot where the cycle
       * transitions back to IDLE.
       *
       * We use the backend's recorded duration
       * when available.
       */

      if (
        cycleData?.last_cycle_duration
      ) {

        durations.push(
          Number(
            cycleData.last_cycle_duration
          )
        );
      }


      /*
       * Look through telemetry for
       * completed cycle durations.
       */

      history.forEach((item) => {

        const duration =
          Number(
            item?.cycle?.duration
          );

        if (
          Number.isFinite(duration) &&
          duration > 0
        ) {

          durations.push(duration);

        }

      });


      if (!durations.length) {

        return {
          average: 0,
          minimum: 0,
          maximum: 0,
          samples: 0,
        };

      }


      return {

        average:
          durations.reduce(
            (sum, value) =>
              sum + value,
            0
          ) /
          durations.length,

        minimum:
          Math.min(...durations),

        maximum:
          Math.max(...durations),

        samples:
          durations.length,

      };

    }, [
      history,
      cycleData,
    ]);


  /* ==========================================================
     STATE DISTRIBUTION
     ========================================================== */

  const stateStats =
    useMemo(() => {

      const result = {};

      history.forEach(
        (item) => {

          const state =
            item?.state ||
            "IDLE";

          result[state] =
            (result[state] || 0) + 1;

        }
      );

      return result;

    }, [history]);


  /* ==========================================================
     SEQUENCE DURATION ANALYSIS
     ========================================================== */

  const sequenceStats =
    useMemo(() => {

      const result = {};

      for (
        let i = 0;
        i < sequenceHistory.length - 1;
        i++
      ) {

        const current =
          sequenceHistory[i];

        const next =
          sequenceHistory[i + 1];


        if (
          current.to_state !==
          next.from_state
        ) {
          continue;
        }


        const start =
          new Date(
            current.timestamp
          ).getTime();

        const end =
          new Date(
            next.timestamp
          ).getTime();


        if (
          !Number.isFinite(start) ||
          !Number.isFinite(end) ||
          end < start
        ) {
          continue;
        }


        const duration =
          (end - start) / 1000;


        if (
          !result[current.to_state]
        ) {

          result[current.to_state] = [];

        }


        result[current.to_state].push(
          duration
        );

      }


      return Object.entries(
        result
      ).map(
        ([state, durations]) => ({

          state,

          average:
            durations.reduce(
              (a, b) => a + b,
              0
            ) /
            durations.length,

          maximum:
            Math.max(...durations),

          samples:
            durations.length,

        })
      );

    }, [sequenceHistory]);


  /* ==========================================================
     SPEED ANALYTICS
     ========================================================== */

  const speedStats =
    useMemo(() => {

      const axes = [
        {
          name: "Axis 1",
          key: "axis1",
        },
        {
          name: "Axis 2",
          key: "axis2",
        },
        {
          name: "Axis 3",
          key: "axis3",
        },
      ];


      return axes.map(
        (axis) => {

          const values =
            history
              .map(
                (item) =>
                  Number(
                    item?.[
                      axis.key
                    ]?.speed
                  ) || 0
              )
              .filter(
                (value) =>
                  Number.isFinite(value)
              );


          const actualValues =
            history
              .map(
                (item) =>
                  Number(
                    item?.[
                      axis.key
                    ]?.actual_speed
                  ) || 0
              )
              .filter(
                (value) =>
                  Number.isFinite(value)
              );


          return {

            name: axis.name,

            maxCommand:
              values.length
                ? Math.max(...values)
                : 0,

            maxActual:
              actualValues.length
                ? Math.max(
                    ...actualValues
                  )
                : 0,

          };

        }
      );

    }, [history]);


  /* ==========================================================
     LOADING
     ========================================================== */

  if (loading) {

    return (

      <Box
        sx={{
          p: 3,
        }}
      >

        <Typography>
          Loading Analytics...
        </Typography>

        <LinearProgress
          sx={{ mt: 2 }}
        />

      </Box>

    );

  }


  /* ==========================================================
     RENDER
     ========================================================== */

  return (

    <Box className="analytics-page">


      {/* ======================================================
          HEADER
          ====================================================== */}

      <Box className="analytics-header">

        <Box>

          <Typography className="analytics-title">
            Analytics
          </Typography>

          <Typography className="analytics-subtitle">
            Machine performance, cycle analysis and
            telemetry intelligence
          </Typography>

        </Box>


        <Chip
          label="LIVE DATA"
          className="analytics-live-chip"
        />

      </Box>


      {/* ======================================================
          KPI CARDS
          ====================================================== */}

      <Grid container spacing={2}>


        <Grid item xs={12} sm={6} md={3}>

          <MetricCard
            title="Total Cycles"
            value={total}
            icon={<TrendingUpIcon />}
          />

        </Grid>


        <Grid item xs={12} sm={6} md={3}>

          <MetricCard
            title="Completed"
            value={completed}
            icon={
              <PrecisionManufacturingIcon />
            }
          />

        </Grid>


        <Grid item xs={12} sm={6} md={3}>

          <MetricCard
            title="Rejected"
            value={rejected}
            icon={
              <WarningAmberIcon />
            }
          />

        </Grid>


        <Grid item xs={12} sm={6} md={3}>

          <MetricCard
            title="Active Alarms"
            value={activeAlarms}
            icon={<SpeedIcon />}
          />

        </Grid>

      </Grid>


      {/* ======================================================
          CYCLE ANALYTICS
          ====================================================== */}

      <Typography
        className="analytics-section-title"
      >
        Cycle Performance
      </Typography>


      <Grid container spacing={2}>


        <Grid item xs={12} md={4}>

          <MetricCard
            title="Current Cycle"
            value={
              cycleData?.cycle_number ??
              production.current ??
              0
            }
            icon={<TimelineIcon />}
          />

        </Grid>


        <Grid item xs={12} md={4}>

          <MetricCard
            title="Average Cycle"
            value={
              `${cycleStats.average.toFixed(2)} s`
            }
            icon={<TimerIcon />}
          />

        </Grid>


        <Grid item xs={12} md={4}>

          <MetricCard
            title="Last Cycle"
            value={
              `${Number(
                cycleData?.last_cycle_duration ||
                0
              ).toFixed(2)} s`
            }
            icon={<TimerIcon />}
          />

        </Grid>

      </Grid>


      {/* ======================================================
          CYCLE STATISTICS
          ====================================================== */}

      <Grid
        container
        spacing={2}
        className="analytics-section"
      >

        <Grid item xs={12} md={6}>

          <Card className="analytics-card">

            <CardContent>

              <SectionTitle
                title="Cycle Time Statistics"
                subtitle="Recorded machine cycle performance"
              />


              <AnalyticsRow
                label="Average Cycle Time"
                value={
                  `${cycleStats.average.toFixed(2)} s`
                }
              />


              <AnalyticsRow
                label="Minimum Cycle Time"
                value={
                  `${cycleStats.minimum.toFixed(2)} s`
                }
              />


              <AnalyticsRow
                label="Maximum Cycle Time"
                value={
                  `${cycleStats.maximum.toFixed(2)} s`
                }
              />


              <AnalyticsRow
                label="Recorded Samples"
                value={cycleStats.samples}
              />


              <AnalyticsRow
                label="Current Cycle Time"
                value={
                  `${Number(
                    cycleData?.current_duration ||
                    0
                  ).toFixed(2)} s`
                }
              />

            </CardContent>

          </Card>

        </Grid>


        <Grid item xs={12} md={6}>

          <Card className="analytics-card">

            <CardContent>

              <SectionTitle
                title="Production Efficiency"
                subtitle="Current production performance"
              />


              <ProgressMetric
                label="Completion Rate"
                value={completionRate}
              />


              <ProgressMetric
                label="Rejection Rate"
                value={rejectionRate}
                danger
              />


              <Box
                className="analytics-stat-row"
                sx={{ mt: 3 }}
              >

                <Stat
                  label="Total"
                  value={total}
                />

                <Stat
                  label="Completed"
                  value={completed}
                />

                <Stat
                  label="Rejected"
                  value={rejected}
                />

              </Box>

            </CardContent>

          </Card>

        </Grid>

      </Grid>


      {/* ======================================================
          CURRENT MACHINE
          ====================================================== */}

      <Typography
        className="analytics-section-title"
      >
        Machine Performance
      </Typography>


      <Grid container spacing={2}>


        <Grid item xs={12} md={6}>

          <Card className="analytics-card">

            <CardContent>

              <SectionTitle
                title="Current Machine State"
                subtitle="Real-time machine condition"
              />


              <Box
                className="machine-performance"
              >

                <Typography
                  className="machine-state"
                >
                  {machine.state || "IDLE"}
                </Typography>

                <Typography
                  className="machine-state-label"
                >
                  CURRENT STATE
                </Typography>

              </Box>


              <Box
                className="analytics-stat-row"
              >

                <Stat
                  label="Model"
                  value={
                    machine.model || 1
                  }
                />


                <Stat
                  label="Auto"
                  value={
                    machine.auto_mode
                      ? "ON"
                      : "OFF"
                  }
                />


                <Stat
                  label="Running"
                  value={
                    machine.running
                      ? "YES"
                      : "NO"
                  }
                />

              </Box>

            </CardContent>

          </Card>

        </Grid>


        <Grid item xs={12} md={6}>

          <Card className="analytics-card">

            <CardContent>

              <SectionTitle
                title="Machine State Distribution"
                subtitle="Telemetry state history"
              />


              {Object.keys(
                stateStats
              ).length === 0 ? (

                <Typography className="empty-text">
                  Waiting for telemetry...
                </Typography>

              ) : (

                Object.entries(
                  stateStats
                ).map(
                  ([state, count]) => (

                    <Box
                      key={state}
                      className="state-stat-row"
                    >

                      <Typography>
                        {state}
                      </Typography>

                      <Chip
                        label={`${count} samples`}
                        size="small"
                        className="state-chip"
                      />

                    </Box>

                  )
                )

              )}

            </CardContent>

          </Card>

        </Grid>

      </Grid>


      {/* ======================================================
          SERVO PERFORMANCE
          ====================================================== */}

      <Typography
        className="analytics-section-title"
      >
        Servo Performance
      </Typography>


      <Grid container spacing={2}>


        <Grid item xs={12} md={4}>

          <ServoAnalytics
            name="Axis 1"
            axis={axis1}
            speed={
              speedStats[0]
            }
          />

        </Grid>


        <Grid item xs={12} md={4}>

          <ServoAnalytics
            name="Axis 2"
            axis={axis2}
            speed={
              speedStats[1]
            }
          />

        </Grid>


        <Grid item xs={12} md={4}>

          <ServoAnalytics
            name="Axis 3"
            axis={axis3}
            speed={
              speedStats[2]
            }
          />

        </Grid>

      </Grid>


      {/* ======================================================
          TELEMETRY CHARTS
          ====================================================== */}

      <Typography
        className="analytics-section-title"
      >
        Telemetry Trends
      </Typography>


      <Grid
        container
        spacing={2}
      >


        <Grid item xs={12} md={6}>

          <Card className="analytics-card">

            <CardContent>

              <SectionTitle
                title="Position vs Time"
                subtitle="Last 300 telemetry samples"
              />


              <TelemetryChart
                history={history}
                field="position"
              />

            </CardContent>

          </Card>

        </Grid>


        <Grid item xs={12} md={6}>

          <Card className="analytics-card">

            <CardContent>

              <SectionTitle
                title="Speed vs Time"
                subtitle="Axis motion speed history"
              />


              <TelemetryChart
                history={history}
                field="speed"
              />

            </CardContent>

          </Card>

        </Grid>

      </Grid>


      {/* ======================================================
          SPEED ANALYSIS
          ====================================================== */}

      <Typography
        className="analytics-section-title"
      >
        Speed Analysis
      </Typography>


      <Grid container spacing={2}>

        {speedStats.map(
          (item) => (

            <Grid
              item
              xs={12}
              md={4}
              key={item.name}
            >

              <Card className="analytics-card">

                <CardContent>

                  <SectionTitle
                    title={item.name}
                    subtitle="Recorded maximum speed"
                  />


                  <AnalyticsRow
                    label="Max Command Speed"
                    value={
                      formatNumber(
                        item.maxCommand
                      )
                    }
                  />


                  <AnalyticsRow
                    label="Max Actual Speed"
                    value={
                      formatNumber(
                        item.maxActual
                      )
                    }
                  />

                </CardContent>

              </Card>

            </Grid>

          )
        )}

      </Grid>


      {/* ======================================================
          SEQUENCE ANALYSIS
          ====================================================== */}

      <Typography
        className="analytics-section-title"
      >
        Sequence Analysis
      </Typography>


      <Grid
        container
        spacing={2}
      >

        <Grid item xs={12} md={7}>

          <Card className="analytics-card">

            <CardContent>

              <SectionTitle
                title="Machine Sequence"
                subtitle="Recent sequence transitions"
              />


              {sequenceHistory.length === 0 ? (

                <Typography className="empty-text">
                  No sequence history available.
                </Typography>

              ) : (

                <Box>

                  {[...sequenceHistory]
                    .reverse()
                    .slice(0, 15)
                    .map(
                      (item, index) => (

                        <Box
                          key={`${item.scan}-${index}`}
                          sx={{
                            display: "flex",
                            alignItems: "center",
                            gap: 2,
                            py: 1.2,
                            borderBottom:
                              "1px solid rgba(255,255,255,0.08)",
                          }}
                        >

                          <Typography
                            sx={{
                              minWidth: 35,
                              opacity: 0.5,
                            }}
                          >
                            {index + 1}
                          </Typography>


                          <Typography
                            sx={{
                              flex: 1,
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
                            className="state-chip"
                          />

                        </Box>

                      )
                    )}

                </Box>

              )}

            </CardContent>

          </Card>

        </Grid>


        <Grid item xs={12} md={5}>

          <Card className="analytics-card">

            <CardContent>

              <SectionTitle
                title="Sequence Timing"
                subtitle="Estimated state durations"
              />


              {sequenceStats.length === 0 ? (

                <Typography className="empty-text">
                  Collecting sequence data...
                </Typography>

              ) : (

                sequenceStats.map(
                  (item) => (

                    <AnalyticsRow
                      key={item.state}
                      label={item.state}
                      value={
                        `${item.average.toFixed(2)} s`
                      }
                    />

                  )
                )

              )}

            </CardContent>

          </Card>

        </Grid>

      </Grid>


      {/* ======================================================
          ALARM / EVENT ANALYTICS
          ====================================================== */}

      <Typography
        className="analytics-section-title"
      >
        Alarm & Event Analytics
      </Typography>


      <Grid container spacing={2}>


        <Grid item xs={12} md={4}>

          <MetricCard
            title="Active Alarms"
            value={activeAlarms}
            icon={
              <WarningAmberIcon />
            }
          />

        </Grid>


        <Grid item xs={12} md={4}>

          <MetricCard
            title="Total Alarm Records"
            value={alarms.length}
            icon={
              <WarningAmberIcon />
            }
          />

        </Grid>


        <Grid item xs={12} md={4}>

          <MetricCard
            title="Recorded Events"
            value={events.length}
            icon={
              <TimelineIcon />
            }
          />

        </Grid>


        <Grid item xs={12}>

          <Card className="analytics-card">

            <CardContent>

              <SectionTitle
                title="Recent Activity"
                subtitle="Latest machine events"
              />


              {events.length === 0 ? (

                <Typography className="empty-text">
                  No events available.
                </Typography>

              ) : (

                events
                  .slice(0, 10)
                  .map(
                    (event, index) => (

                      <Box
                        key={
                          event.id ||
                          index
                        }
                        className="analytics-event"
                      >

                        <Box
                          className="event-marker"
                        />

                        <Box>

                          <Typography>
                            {event.message ||
                              event.description ||
                              event.event ||
                              "Machine event"}
                          </Typography>

                          {event.timestamp && (

                            <Typography
                              className="small-label"
                            >
                              {formatTimestamp(
                                event.timestamp
                              )}
                            </Typography>

                          )}

                        </Box>

                      </Box>

                    )
                  )

              )}

            </CardContent>

          </Card>

        </Grid>

      </Grid>


      {/* ======================================================
          DIGITAL TWIN ENGINE
          ====================================================== */}

      <Typography
        className="analytics-section-title"
      >
        Digital Twin Engine
      </Typography>


      <Grid container spacing={2}>


        <Grid item xs={12} sm={4}>

          <MetricCard
            title="Scan Count"
            value={
              live.engine?.scan_count ??
              0
            }
            icon={<TimelineIcon />}
          />

        </Grid>


        <Grid item xs={12} sm={4}>

          <MetricCard
            title="Telemetry Samples"
            value={
              live.engine?.history_size ??
              history.length
            }
            icon={<SpeedIcon />}
          />

        </Grid>


        <Grid item xs={12} sm={4}>

          <MetricCard
            title="Engine Uptime"
            value={
              `${Number(
                live.engine?.uptime ||
                0
              ).toFixed(1)} s`
            }
            icon={<TimerIcon />}
          />

        </Grid>

      </Grid>


      {/* ======================================================
          FOOTER
          ====================================================== */}

      <Box
        sx={{
          textAlign: "right",
          mt: 3,
          mb: 2,
        }}
      >

        <Typography className="small-label">

          Last update:{" "}

          {formatTimestamp(
            live.timestamp
          )}

        </Typography>

      </Box>

    </Box>
  );
}


/* ============================================================
   METRIC CARD
   ============================================================ */

function MetricCard({
  title,
  value,
  icon,
}) {

  return (

    <Card className="metric-card">

      <CardContent>

        <Box className="metric-icon">
          {icon}
        </Box>

        <Typography className="metric-label">
          {title}
        </Typography>

        <Typography className="metric-value">
          {value}
        </Typography>

      </CardContent>

    </Card>
  );
}


/* ============================================================
   SECTION TITLE
   ============================================================ */

function SectionTitle({
  title,
  subtitle,
}) {

  return (

    <Box className="analytics-card-title">

      <Typography
        className="analytics-card-heading"
      >
        {title}
      </Typography>

      <Typography
        className="analytics-card-subheading"
      >
        {subtitle}
      </Typography>

    </Box>
  );
}


/* ============================================================
   PROGRESS METRIC
   ============================================================ */

function ProgressMetric({
  label,
  value,
  danger = false,
}) {

  const safeValue =
    Math.max(
      0,
      Math.min(
        Number(value) || 0,
        100
      )
    );


  return (

    <Box className="progress-metric">

      <Box className="progress-header">

        <Typography>
          {label}
        </Typography>

        <Typography>
          {safeValue.toFixed(1)}%
        </Typography>

      </Box>

      <LinearProgress
        variant="determinate"
        value={safeValue}
        className={
          danger
            ? "analytics-progress danger"
            : "analytics-progress"
        }
      />

    </Box>
  );
}


/* ============================================================
   STAT
   ============================================================ */

function Stat({
  label,
  value,
}) {

  return (

    <Box className="stat-box">

      <Typography className="stat-label">
        {label}
      </Typography>

      <Typography className="stat-value">
        {value}
      </Typography>

    </Box>
  );
}


/* ============================================================
   ANALYTICS ROW
   ============================================================ */

function AnalyticsRow({
  label,
  value,
}) {

  return (

    <Box
      sx={{
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        py: 1.3,
        borderBottom:
          "1px solid rgba(255,255,255,0.07)",
        gap: 2,
      }}
    >

      <Typography
        sx={{
          opacity: 0.8,
        }}
      >
        {label}
      </Typography>

      <Typography
        sx={{
          fontWeight: 600,
        }}
      >
        {value}
      </Typography>

    </Box>
  );
}


/* ============================================================
   SERVO ANALYTICS
   ============================================================ */

function ServoAnalytics({
  name,
  axis,
  speed,
}) {

  const position =
    Number(axis.position) || 0;

  const target =
    Number(axis.target) || 0;

  const positionError =
    Number(
      axis.position_error
    ) || 0;

  const actualSpeed =
    Number(
      axis.actual_speed
    ) || 0;

  const commandSpeed =
    Number(
      axis.speed
    ) || 0;


  let progress = 0;

  if (target !== 0) {

    progress =
      Math.min(
        100,
        Math.max(
          0,
          Math.abs(
            position / target
          ) * 100
        )
      );

  } else if (axis.complete) {

    progress = 100;

  }


  let status = "IDLE";
  let statusClass = "chip-off";


  if (axis.error) {

    status = "ERROR";
    statusClass = "chip-danger";

  } else if (axis.busy) {

    status = "MOVING";
    statusClass = "chip-active";

  } else if (axis.complete) {

    status = "COMPLETE";
    statusClass = "chip-success";

  }


  return (

    <Card className="servo-analytics-card">

      <CardContent>

        <Box
          className="servo-analytics-header"
        >

          <Typography>
            {name}
          </Typography>

          <Chip
            size="small"
            label={status}
            className={statusClass}
          />

        </Box>


        <Typography
          className="servo-analytics-position"
        >
          {formatNumber(position)}
        </Typography>


        <Typography
          className="servo-analytics-label"
        >
          POSITION
        </Typography>


        <Box className="servo-target-row">

          <span>
            Target
          </span>

          <strong>
            {formatNumber(target)}
          </strong>

        </Box>


        <LinearProgress
          variant="determinate"
          value={progress}
          className="analytics-progress"
        />


        <Divider sx={{ my: 2 }} />


        <AnalyticsRow
          label="Position Error"
          value={
            formatNumber(
              positionError
            )
          }
        />


        <AnalyticsRow
          label="Command Speed"
          value={
            formatNumber(
              commandSpeed
            )
          }
        />


        <AnalyticsRow
          label="Actual Speed"
          value={
            formatNumber(
              actualSpeed
            )
          }
        />


        <AnalyticsRow
          label="Max Recorded Speed"
          value={
            formatNumber(
              speed?.maxActual || 0
            )
          }
        />

      </CardContent>

    </Card>
  );
}


/* ============================================================
   TELEMETRY CHART
   ============================================================ */

function TelemetryChart({
  history,
  field,
}) {

  if (
    !history ||
    history.length < 2
  ) {

    return (

      <Box
        sx={{
          height: 220,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
        }}
      >

        <Typography className="empty-text">
          Collecting telemetry data...
        </Typography>

      </Box>

    );

  }


  const width = 900;
  const height = 220;
  const padding = 20;


  const axes = [
    {
      key: "axis1",
      label: "Axis 1",
    },
    {
      key: "axis2",
      label: "Axis 2",
    },
    {
      key: "axis3",
      label: "Axis 3",
    },
  ];


  const series =
    axes.map(
      (axis) => ({

        ...axis,

        values:
          history.map(
            (item) =>
              Number(
                item?.[
                  axis.key
                ]?.[field]
              ) || 0
          ),

      })
    );


  const allValues =
    series.flatMap(
      (item) =>
        item.values
    );


  let min =
    Math.min(
      ...allValues
    );

  let max =
    Math.max(
      ...allValues
    );


  if (min === max) {

    min -= 1;
    max += 1;

  }


  const makePoints =
    (values) => {

      return values
        .map(
          (value, index) => {

            const x =
              padding +
              (
                index /
                Math.max(
                  1,
                  values.length - 1
                )
              ) *
              (
                width -
                padding * 2
              );


            const y =
              height -
              padding -
              (
                (
                  value - min
                ) /
                (
                  max - min
                )
              ) *
              (
                height -
                padding * 2
              );


            return `${x},${y}`;

          }
        )
        .join(" ");

    };


  return (

    <Box>

      <svg
        width="100%"
        height="220"
        viewBox={`0 0 ${width} ${height}`}
        preserveAspectRatio="none"
      >

        {/* GRID */}

        {[40, 90, 140, 190].map(
          (y) => (

            <line
              key={y}
              x1="0"
              y1={y}
              x2={width}
              y2={y}
              stroke="rgba(255,255,255,0.08)"
              strokeWidth="1"
            />

          )
        )}


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


      <Box
        sx={{
          display: "flex",
          gap: 3,
          mt: 1,
          justifyContent: "center",
        }}
      >

        <Legend
          label="Axis 1"
          className="axis1"
        />

        <Legend
          label="Axis 2"
          className="axis2"
        />

        <Legend
          label="Axis 3"
          className="axis3"
        />

      </Box>

    </Box>
  );
}


/* ============================================================
   LEGEND
   ============================================================ */

function Legend({
  label,
  className,
}) {

  return (

    <Box
      sx={{
        display: "flex",
        alignItems: "center",
        gap: 0.8,
      }}
    >

      <Box
        className={`chart-legend-dot ${className}`}
        sx={{
          width: 9,
          height: 9,
          borderRadius: "50%",
          background:
            className === "axis1"
              ? "#42a5f5"
              : className === "axis2"
                ? "#66bb6a"
                : "#ffa726",
        }}
      />

      <Typography
        className="small-label"
      >
        {label}
      </Typography>

    </Box>
  );
}


/* ============================================================
   NUMBER FORMAT
   ============================================================ */

function formatNumber(value) {

  const number =
    Number(value);

  if (
    !Number.isFinite(number)
  ) {

    return "0";

  }


  if (
    Number.isInteger(number)
  ) {

    return number;

  }


  return number.toFixed(2);
}


/* ============================================================
   TIMESTAMP FORMAT
   ============================================================ */

function formatTimestamp(
  timestamp
) {

  if (!timestamp) {
    return "--";
  }


  try {

    return new Date(
      timestamp
    ).toLocaleTimeString();

  } catch {

    return "--";

  }
}