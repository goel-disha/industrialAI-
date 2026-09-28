import React, { useEffect, useState } from "react";
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Chip,
  Button,
  CircularProgress,
  Divider,
} from "@mui/material";

import WarningAmberIcon from "@mui/icons-material/WarningAmber";
import ErrorIcon from "@mui/icons-material/Error";
import CheckCircleIcon from "@mui/icons-material/CheckCircle";
import RefreshIcon from "@mui/icons-material/Refresh";
import RestartAltIcon from "@mui/icons-material/RestartAlt";

import "../styles/alarm.css";

const API = "http://localhost:8000";

export default function Alarms() {
  const [alarms, setAlarms] = useState([]);
  const [activeAlarms, setActiveAlarms] = useState([]);
  const [summary, setSummary] = useState({});
  const [loading, setLoading] = useState(true);
  const [resetting, setResetting] = useState(false);

  // ==========================================================
  // LOAD ALARMS
  // ==========================================================

  const loadAlarms = async () => {
    try {
      setLoading(true);

      const [
        alarmsResponse,
        activeResponse,
        summaryResponse,
      ] = await Promise.all([
        fetch(`${API}/alarms`),
        fetch(`${API}/alarms/active`),
        fetch(`${API}/alarms/summary`),
      ]);

      const alarmsData = alarmsResponse.ok
        ? await alarmsResponse.json()
        : [];

      const activeData = activeResponse.ok
        ? await activeResponse.json()
        : [];

      const summaryData = summaryResponse.ok
        ? await summaryResponse.json()
        : {};

      setAlarms(normalize(alarmsData));
      setActiveAlarms(normalize(activeData));
      setSummary(summaryData || {});
    } catch (error) {
      console.error("Alarm loading error:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAlarms();

    const interval = setInterval(
      loadAlarms,
      2000
    );

    return () => clearInterval(interval);
  }, []);

  // ==========================================================
  // RESET ALARMS
  // ==========================================================

  const resetAlarms = async () => {
    try {
      setResetting(true);

      const response = await fetch(
        `${API}/alarms/reset`,
        {
          method: "POST",
        }
      );

      if (!response.ok) {
        throw new Error("Alarm reset failed");
      }

      await loadAlarms();
    } catch (error) {
      console.error("Alarm reset error:", error);
    } finally {
      setResetting(false);
    }
  };

  // ==========================================================
  // SUMMARY VALUES
  // ==========================================================

  const total =
    summary.total ??
    summary.count ??
    alarms.length;

  const active =
    summary.active ??
    summary.active_count ??
    activeAlarms.length;

  const critical =
    summary.critical ??
    summary.critical_count ??
    countSeverity(
      activeAlarms,
      "critical"
    );

  const warnings =
    summary.warning ??
    summary.warnings ??
    summary.warning_count ??
    countSeverity(
      activeAlarms,
      "warning"
    );

  return (
    <Box className="alarms-page">

      {/* =====================================================
          HEADER
          ===================================================== */}

      <Box className="alarms-header">

        <Box>

          <Typography className="alarms-title">
            Alarms
          </Typography>

          <Typography className="alarms-subtitle">
            Machine alarms, faults and diagnostic events
          </Typography>

        </Box>

        <Box className="alarms-actions">

          <Button
            variant="outlined"
            startIcon={<RefreshIcon />}
            onClick={loadAlarms}
            disabled={loading}
          >
            Refresh
          </Button>

          <Button
            variant="contained"
            color="error"
            startIcon={<RestartAltIcon />}
            onClick={resetAlarms}
            disabled={resetting}
          >
            {resetting
              ? "Resetting..."
              : "Reset Alarms"}
          </Button>

        </Box>

      </Box>

      {/* =====================================================
          SUMMARY
          ===================================================== */}

      <Grid
        container
        spacing={2}
        className="alarm-summary"
      >

        <SummaryCard
          title="Total Alarms"
          value={total}
          icon={<WarningAmberIcon />}
        />

        <SummaryCard
          title="Active"
          value={active}
          icon={<ErrorIcon />}
          danger
        />

        <SummaryCard
          title="Critical"
          value={critical}
          icon={<ErrorIcon />}
          critical
        />

        <SummaryCard
          title="Warnings"
          value={warnings}
          icon={<WarningAmberIcon />}
          warning
        />

      </Grid>

      {/* =====================================================
          ACTIVE ALARMS
          ===================================================== */}

      <Card className="alarm-card">

        <CardContent>

          <Box className="section-header">

            <Box>

              <Typography className="section-title">
                Active Alarms
              </Typography>

              <Typography className="section-subtitle">
                Currently active machine conditions
              </Typography>

            </Box>

            <Chip
              label={`${activeAlarms.length} Active`}
              className={
                activeAlarms.length
                  ? "active-chip"
                  : "normal-chip"
              }
            />

          </Box>

          <Divider />

          {loading ? (

            <Box className="alarm-loading">
              <CircularProgress />
            </Box>

          ) : activeAlarms.length === 0 ? (

            <EmptyState />

          ) : (

            <AlarmTable
              alarms={activeAlarms}
              active
            />

          )}

        </CardContent>

      </Card>

      {/* =====================================================
          ALARM HISTORY
          ===================================================== */}

      <Card className="alarm-card">

        <CardContent>

          <Box className="section-header">

            <Box>

              <Typography className="section-title">
                Alarm History
              </Typography>

              <Typography className="section-subtitle">
                Recorded machine alarm events
              </Typography>

            </Box>

            <Chip
              label={`${alarms.length} Records`}
            />

          </Box>

          <Divider />

          {loading ? (

            <Box className="alarm-loading">
              <CircularProgress />
            </Box>

          ) : alarms.length === 0 ? (

            <EmptyState
              text="No alarm history available"
            />

          ) : (

            <AlarmTable
              alarms={alarms}
            />

          )}

        </CardContent>

      </Card>

    </Box>
  );
}


// ==========================================================
// SUMMARY CARD
// ==========================================================

function SummaryCard({
  title,
  value,
  icon,
  danger,
  critical,
  warning,
}) {

  let className =
    "alarm-summary-card";

  if (danger) {
    className += " alarm-danger";
  }

  if (critical) {
    className += " alarm-critical";
  }

  if (warning) {
    className += " alarm-warning";
  }

  return (
    <Grid
      item
      xs={12}
      sm={6}
      md={3}
    >

      <Card className={className}>

        <CardContent>

          <Box className="summary-icon">
            {icon}
          </Box>

          <Typography className="summary-label">
            {title}
          </Typography>

          <Typography className="summary-value">
            {value}
          </Typography>

        </CardContent>

      </Card>

    </Grid>
  );
}


// ==========================================================
// ALARM TABLE
// ==========================================================

function AlarmTable({
  alarms,
  active = false,
}) {

  return (

    <Box className="alarm-table-wrapper">

      <table className="alarm-table">

        <thead>

          <tr>
            <th>Alarm</th>
            <th>Address</th>
            <th>Severity</th>
            <th>Status</th>
            <th>Time</th>
            <th>Description</th>
          </tr>

        </thead>

        <tbody>

          {alarms.map(
            (alarm, index) => {

              const severity =
                getSeverity(alarm);

              const status =
                alarm.status ||
                alarm.state ||
                (active
                  ? "ACTIVE"
                  : "CLEARED");

              return (

                <tr key={index}>

                  <td className="alarm-code">
                    {alarm.code ||
                      alarm.alarm_code ||
                      alarm.id ||
                      `ALM-${index + 1}`}
                  </td>

                  <td className="alarm-address">
                    {alarm.address ||
                      alarm.device ||
                      alarm.register ||
                      "—"}
                  </td>

                  <td>
                    <SeverityChip
                      severity={severity}
                    />
                  </td>

                  <td>

                    <Chip
                      size="small"
                      label={String(
                        status
                      ).toUpperCase()}
                      className={
                        String(status)
                          .toLowerCase()
                          .includes("active")
                          ? "status-active"
                          : "status-cleared"
                      }
                    />

                  </td>

                  <td>
                    {alarm.timestamp ||
                      alarm.time ||
                      alarm.created_at ||
                      "—"}
                  </td>

                  <td>
                    {alarm.message ||
                      alarm.description ||
                      alarm.name ||
                      "—"}
                  </td>

                </tr>
              );
            }
          )}

        </tbody>

      </table>

    </Box>
  );
}


// ==========================================================
// SEVERITY
// ==========================================================

function SeverityChip({
  severity,
}) {

  const value =
    String(severity || "warning")
      .toLowerCase();

  let className =
    "severity-warning";

  if (value === "critical") {
    className = "severity-critical";
  } else if (value === "error") {
    className = "severity-error";
  } else if (value === "info") {
    className = "severity-info";
  }

  return (
    <Chip
      size="small"
      label={value.toUpperCase()}
      className={className}
    />
  );
}


// ==========================================================
// EMPTY
// ==========================================================

function EmptyState({
  text = "No active alarms",
}) {

  return (

    <Box className="alarm-empty">

      <CheckCircleIcon />

      <Typography>
        {text}
      </Typography>

    </Box>
  );
}


// ==========================================================
// HELPERS
// ==========================================================

function normalize(data) {

  if (Array.isArray(data)) {
    return data;
  }

  if (!data || typeof data !== "object") {
    return [];
  }

  if (Array.isArray(data.alarms)) {
    return data.alarms;
  }

  if (Array.isArray(data.active)) {
    return data.active;
  }

  if (Array.isArray(data.data)) {
    return data.data;
  }

  if (Array.isArray(data.results)) {
    return data.results;
  }

  return [];
}


function getSeverity(alarm) {

  return (
    alarm.severity ||
    alarm.level ||
    alarm.priority ||
    "warning"
  );
}


function countSeverity(
  alarms,
  severity
) {

  return alarms.filter(
    (alarm) =>
      String(
        getSeverity(alarm)
      ).toLowerCase() === severity
  ).length;
}