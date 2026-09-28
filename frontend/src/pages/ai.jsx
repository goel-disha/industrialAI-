import React, { useEffect, useState } from "react";
import {
  Box, Card, CardContent, Chip, Divider, Grid, LinearProgress,
  List, ListItem, ListItemText, Typography,
} from "@mui/material";
import PsychologyIcon from "@mui/icons-material/Psychology";
import BuildCircleIcon from "@mui/icons-material/BuildCircle";
import WarningAmberIcon from "@mui/icons-material/WarningAmber";
import TimelineIcon from "@mui/icons-material/Timeline";
import "../styles/ai.css";

const API = "http://localhost:8000";

export default function AI() {
  const [prediction, setPrediction] = useState(null);
  const [maintenance, setMaintenance] = useState(null);
  const [lstm, setLstm] = useState(null);
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(true);

  const load = async () => {
    try {
      const [p, m, l, s] = await Promise.all([
        fetch(`${API}/ai/ml/predict`).then((r) => r.json()),
        fetch(`${API}/ai/ml/maintenance`).then((r) => r.json()),
        fetch(`${API}/ai/ml/lstm-predict`).then((r) => r.json()),
        fetch(`${API}/ai/ml/status`).then((r) => r.json()),
      ]);
      setPrediction(p);
      setMaintenance(m);
      setLstm(l);
      setStatus(s);
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
          <Typography className="ai-subtitle">Real-time anomaly detection, fault prediction, explainability and predictive maintenance</Typography>
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
            </List>
          </CardContent></Card>
        </Grid>
        <Grid item xs={12} md={5}>
          <Card className="ai-card"><CardContent>
            <Typography className="ai-card-title">Model Stack</Typography>
            <Divider sx={{ my: 2 }} />
            {Object.entries(status?.models || {}).map(([name, ready]) => <Row key={name} label={name.replaceAll("_", " ")} value={ready ? "READY" : "NOT READY"} />)}
          </CardContent></Card>
        </Grid>
      </Grid>
    </Box>
  );
}

function Kpi({ title, value }) { return <Card className="ai-kpi"><CardContent><Typography className="ai-label">{title}</Typography><Typography className="ai-value">{value}</Typography></CardContent></Card>; }
function Row({ label, value, danger }) { return <Box className="ai-row"><Typography>{label}</Typography><Chip label={value} className={danger ? "danger-chip" : "status-chip"} /></Box>; }
