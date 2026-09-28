import { useEffect, useState } from "react";
import { Card, CardContent, Grid, Typography } from "@mui/material";

const API = "http://localhost:8000";

export default function AICyclePanel() {
  const [data, setData] = useState(null);

  useEffect(() => {
    let alive = true;
    const load = async () => {
      try {
        const res = await fetch(`${API}/ai/cycles?limit=100`);
        const json = await res.json();
        if (alive) setData(json);
      } catch {}
    };
    load();
    const timer = setInterval(load, 2000);
    return () => { alive = false; clearInterval(timer); };
  }, []);

  if (!data) return null;

  const items = [
    ["Average", `${data.average}s`], ["Median", `${data.median}s`],
    ["Best", `${data.best}s`], ["Worst", `${data.worst}s`],
    ["Std Dev", `${data.std}s`], ["Trend", `${data.trend}s`],
  ];

  return (
    <Card>
      <CardContent>
        <Typography variant="h6">Cycle Intelligence</Typography>
        <Grid container spacing={2} sx={{mt:1}}>
          {items.map(([label, value]) => (
            <Grid item xs={6} md={2} key={label}>
              <Typography variant="body2">{label}</Typography>
              <Typography variant="h6">{value}</Typography>
            </Grid>
          ))}
        </Grid>
      </CardContent>
    </Card>
  );
}
