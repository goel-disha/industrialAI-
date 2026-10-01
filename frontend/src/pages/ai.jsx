import React, { useEffect, useState } from "react";
import {
  Box, Button, Card, CardContent, Chip, Divider, Grid, LinearProgress,
  List, ListItem, ListItemText, MenuItem, Select, Typography,
} from "@mui/material";
import PsychologyIcon from "@mui/icons-material/Psychology";
import BuildCircleIcon from "@mui/icons-material/BuildCircle";
import WarningAmberIcon from "@mui/icons-material/WarningAmber";
import TimelineIcon from "@mui/icons-material/Timeline";
import ScienceIcon from "@mui/icons-material/Science";
import AutorenewIcon from "@mui/icons-material/Autorenew";
import "../styles/ai.css";

const API = import.meta.env.VITE_API_URL || (import.meta.env.VITE_API_HOST ? `https://${import.meta.env.VITE_API_HOST}` : "http://localhost:8000");

export default function AI() {
  const [prediction, setPrediction] = useState(null);
  const [maintenance, setMaintenance] = useState(null);
  const [rul, setRul] = useState(null);
  const [lstm, setLstm] = useState(null);
  const [status, setStatus] = useState(null);
  const [performance, setPerformance] = useState(null);
  const [injection, setInjection] = useState(null);
  const [fault, setFault] = useState("SERVO_LAG");
  const [axis, setAxis] = useState("a2");
  const [severity, setSeverity] = useState(0.6);
  const [loading, setLoading] = useState(true);

  const load = async () => {
    try {
      const [p, m, r, l, s, perf, fi] = await Promise.all([
        fetch(`${API}/ai/ml/predict`).then((x) => x.json()),
        fetch(`${API}/ai/ml/maintenance`).then((x) => x.json()),
        fetch(`${API}/ai/ml/rul`).then((x) => x.json()),
        fetch(`${API}/ai/ml/lstm-predict`).then((x) => x.json()),
        fetch(`${API}/ai/ml/status`).then((x) => x.json()),
        fetch(`${API}/ai/ml/performance`).then((x) => x.json()),
        fetch(`${API}/ai/ml/fault-injection`).then((x) => x.json()),
      ]);
      setPrediction(p);
      setMaintenance(m);
      setRul(r);
      setLstm(l);
      setStatus(s);
      setPerformance(perf);
      setInjection(fi);
      setLoading(false);
    } catch (error) {
      console.error("AI dashboard error:", error);
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
    const timer = setInterval(load, 1500);
    return () => clearInterval(timer);
  }, []);

  const injectFault = async () => {
    await fetch(`${API}/ai/ml/fault-injection`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ fault, axis, severity: Number(severity) }),
    });
    load();
  };

  const clearFault = async () => {
    await fetch(`${API}/ai/ml/fault-injection`, { method: "DELETE" });
    load();
  };

  if (loading) {
    return <Box className="ai-page"><Typography>Loading AI intelligence...</Typography><LinearProgress sx={{ mt: 2 }} /></Box>;
  }

  const confidence = Number(prediction?.fault_confidence || 0) * 100;
  const anomalyScore = Number(prediction?.anomaly_score || 0) * 100;
  const explanation = prediction?.explanation?.top_features || [];

  return (
    <Box className="ai-page">
      <Box className="ai-header">
        <Box>
          <Typography className="ai-title">Industrial AI Intelligence</Typography>
          <Typography className="ai-subtitle">Real-time anomaly detection, fault diagnosis, prediction, explainability and predictive maintenance</Typography>
        </Box>
        <Chip icon={<PsychologyIcon />} label={status?.ready ? "AI ONLINE" : "AI OFFLINE"} className={status?.ready ? "ai-online" : "ai-offline"} />
      </Box>

      <Grid container spacing={2}>
        <Grid item xs={12} md={3}><Kpi title="Predicted Fault" value={prediction?.predicted_fault || "N/A"} /></Grid>
        <Grid item xs={12} md={3}><Kpi title="Fault Confidence" value={`${confidence.toFixed(1)}%`} /></Grid>
        <Grid item xs={12} md={3}><Kpi title="Anomaly Score" value={`${anomalyScore.toFixed(1)}%`} /></Grid>
        <Grid item xs={12} md={3}><Kpi title="Next Cycle" value={`${Number(prediction?.predicted_next_cycle_duration || 0).toFixed(2)} s`} /></Grid>
      </Grid>

      <Grid container spacing={2} className="ai-section">
        <Grid item xs={12} md={6}>
          <Card className="ai-card"><CardContent>
            <Typography className="ai-card-title"><WarningAmberIcon /> Detection & Model Agreement</Typography>
            <Divider sx={{ my: 2 }} />
            <Row label="Anomaly detected" value={prediction?.anomaly ? "YES" : "NO"} danger={prediction?.anomaly} />
            <Row label="Random Forest / XGBoost" value={prediction?.model_agreement || "RF_ONLY"} />
            <Row label="LSTM prediction" value={lstm?.predicted_fault || (lstm?.status || "NOT TRAINED")} />
            <Row label="Machine state" value={prediction?.machine_state || "IDLE"} />
            <Row label="Cycle" value={prediction?.cycle_number ?? 0} />
          </CardContent></Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card className="ai-card"><CardContent>
            <Typography className="ai-card-title"><BuildCircleIcon /> Predictive Maintenance</Typography>
            <Divider sx={{ my: 2 }} />
            <Chip label={maintenance?.status || "NO_ACTION"} className="maintenance-chip" />
            <Typography className="maintenance-priority">Priority: {maintenance?.priority || "LOW"}</Typography>
            <Typography className="maintenance-message">{maintenance?.message || "No maintenance action is currently indicated."}</Typography>
            {(maintenance?.systems_to_inspect || []).map((item) => <Chip key={item} label={item} sx={{ mr: 1, mt: 1 }} />)}
          </CardContent></Card>
        </Grid>
      </Grid>

      <Grid container spacing={2} className="ai-section">
        <Grid item xs={12} md={5}>
          <Card className="ai-card"><CardContent>
            <Typography className="ai-card-title"><AutorenewIcon /> Degradation / RUL</Typography>
            <Divider sx={{ my: 2 }} />
            <Row label="Status" value={rul?.status || "INSUFFICIENT_HISTORY"} />
            <Row label="Health" value={rul?.health_percent != null ? `${rul.health_percent}%` : "N/A"} />
            <Row label="Estimated remaining cycles" value={rul?.estimated_remaining_cycles ?? "N/A"} />
            <Row label="Maintenance risk" value={rul?.maintenance_risk || "N/A"} />
            <Typography className="maintenance-message" sx={{ mt: 2 }}>{rul?.note || "Collect more completed cycles for a degradation estimate."}</Typography>
          </CardContent></Card>
        </Grid>

        <Grid item xs={12} md={7}>
          <Card className="ai-card"><CardContent>
            <Typography className="ai-card-title"><ScienceIcon /> Controlled Fault Injection Lab</Typography>
            <Divider sx={{ my: 2 }} />
            <Grid container spacing={1}>
              <Grid item xs={12} md={4}>
                <Select fullWidth size="small" value={fault} onChange={(e) => setFault(e.target.value)}>
                  <MenuItem value="SERVO_LAG">Servo Lag</MenuItem>
                  <MenuItem value="VIBRATION">Vibration</MenuItem>
                  <MenuItem value="STUCK_AXIS">Stuck Axis</MenuItem>
                  <MenuItem value="SENSOR_NOISE">Sensor Noise</MenuItem>
                  <MenuItem value="CYCLE_DEGRADATION">Cycle Degradation</MenuItem>
                </Select>
              </Grid>
              <Grid item xs={12} md={3}>
                <Select fullWidth size="small" value={axis} onChange={(e) => setAxis(e.target.value)}>
                  <MenuItem value="a1">Axis 1</MenuItem>
                  <MenuItem value="a2">Axis 2</MenuItem>
                  <MenuItem value="a3">Axis 3</MenuItem>
                </Select>
              </Grid>
              <Grid item xs={12} md={5}>
                <Select fullWidth size="small" value={severity} onChange={(e) => setSeverity(e.target.value)}>
                  <MenuItem value={0.25}>25% severity</MenuItem>
                  <MenuItem value={0.5}>50% severity</MenuItem>
                  <MenuItem value={0.75}>75% severity</MenuItem>
                  <MenuItem value={1}>100% severity</MenuItem>
                </Select>
              </Grid>
            </Grid>
            <Box sx={{ mt: 2, display: "flex", gap: 1, flexWrap: "wrap" }}>
              <Button variant="contained" onClick={injectFault}>INJECT FAULT</Button>
              <Button variant="outlined" onClick={clearFault}>CLEAR</Button>
              <Chip label={injection?.active ? `ACTIVE: ${injection.injection.fault}` : "NO INJECTION"} />
            </Box>
            <Typography className="maintenance-message" sx={{ mt: 2 }}>
              Fault injection changes only the AI feature vector for controlled validation. It does not write PLC commands or alter machine control.
            </Typography>
          </CardContent></Card>
        </Grid>
      </Grid>

      <Grid container spacing={2} className="ai-section">
        <Grid item xs={12} md={7}>
          <Card className="ai-card"><CardContent>
            <Typography className="ai-card-title"><TimelineIcon /> Explainable AI — Top Features</Typography>
            <Divider sx={{ my: 2 }} />
            <List dense>
              {explanation.map((item) => (
                <ListItem key={item.feature}>
                  <ListItemText primary={item.feature} secondary={`Impact: ${item.impact} • Value: ${item.value}`} />
                  <Chip label={item.direction} />
                </ListItem>
              ))}
              {!explanation.length && <ListItem><ListItemText primary="No explanation available yet." /></ListItem>}
            </List>
          </CardContent></Card>
        </Grid>
        <Grid item xs={12} md={5}>
          <Card className="ai-card"><CardContent>
            <Typography className="ai-card-title">Model Stack</Typography>
            <Divider sx={{ my: 2 }} />
            {Object.entries(status?.models || {}).map(([name, ready]) => <Row key={name} label={name.replaceAll("_", " ")} value={ready ? "READY" : "NOT READY"} />)}
            <Divider sx={{ my: 2 }} />
            <Typography className="ai-card-title">Evaluation</Typography>
            <Typography className="maintenance-message" sx={{ mt: 1 }}>
              RF F1: {performance?.core_models?.fault_classification?.f1_weighted ?? "N/A"} •
              XGBoost F1: {performance?.xgboost?.metrics?.f1_weighted ?? "N/A"} •
              LSTM F1: {performance?.lstm?.f1_weighted ?? "N/A"}
            </Typography>
          </CardContent></Card>
        </Grid>
      </Grid>
    </Box>
  );
}

function Kpi({ title, value }) {
  return <Card className="ai-kpi"><CardContent><Typography className="ai-label">{title}</Typography><Typography className="ai-value">{value}</Typography></CardContent></Card>;
}

function Row({ label, value, danger }) {
  return <Box className="ai-row"><Typography>{label}</Typography><Chip label={value} className={danger ? "danger-chip" : "status-chip"} /></Box>;
}
