import { useEffect, useState } from "react";
import { Box, Card, CardContent, Chip, LinearProgress, Typography } from "@mui/material";

const API = "http://localhost:8000";

export default function AIHealthPanel() {
  const [data, setData] = useState(null);

  useEffect(() => {
    let alive = true;
    const load = async () => {
      try {
        const res = await fetch(`${API}/ai/snapshot`);
        const json = await res.json();
        if (alive) setData(json);
      } catch {}
    };
    load();
    const timer = setInterval(load, 1000);
    return () => { alive = false; clearInterval(timer); };
  }, []);

  if (!data) return <Card><CardContent><Typography>Loading AI engine...</Typography><LinearProgress sx={{mt:2}} /></CardContent></Card>;

  const health = data.health;
  const anomalies = data.anomalies?.anomalies || [];

  return (
    <Card>
      <CardContent>
        <Typography variant="h6">AI Machine Health</Typography>
        <Box sx={{mt:2, display:"flex", alignItems:"center", gap:2}}>
          <Typography variant="h3">{health.health_score}</Typography>
          <Chip label={health.status}
            color={health.status === "CRITICAL" ? "error" : health.status === "WARNING" ? "warning" : "success"} />
        </Box>
        <LinearProgress variant="determinate" value={health.health_score} sx={{mt:2, height:8}} />

        <Typography sx={{mt:2}}>Axis Health</Typography>
        {Object.entries(health.axis_health || {}).map(([axis, score]) => (
          <Box key={axis} sx={{mt:1}}>
            <Box sx={{display:"flex", justifyContent:"space-between"}}>
              <Typography variant="body2">{axis.toUpperCase()}</Typography>
              <Typography variant="body2">{score}</Typography>
            </Box>
            <LinearProgress variant="determinate" value={score} />
          </Box>
        ))}

        <Typography sx={{mt:2}}>AI Events</Typography>
        {anomalies.length === 0
          ? <Chip label="No active anomalies" color="success" sx={{mt:1}} />
          : anomalies.slice(0,5).map((item, i) => (
              <Box key={`${item.code}-${i}`} sx={{mt:1}}>
                <Chip size="small" label={item.severity}
                  color={item.severity === "CRITICAL" ? "error" : "warning"} />
                <Typography variant="body2" sx={{mt:.5}}>{item.message}</Typography>
              </Box>
            ))}
      </CardContent>
    </Card>
  );
}
