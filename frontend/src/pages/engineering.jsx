import React, { useEffect, useState } from "react";
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Tabs,
  Tab,
  TextField,
  InputAdornment,
  Chip,
  CircularProgress,
} from "@mui/material";

import SearchIcon from "@mui/icons-material/Search";
import CodeIcon from "@mui/icons-material/Code";
import MemoryIcon from "@mui/icons-material/Memory";
import TimerIcon from "@mui/icons-material/Timer";
import SettingsIcon from "@mui/icons-material/Settings";

import "../styles/engineering.css";

const API = import.meta.env.VITE_API_URL || "http://localhost:8000";

export default function Engineering() {

  const [tab, setTab] = useState(0);
  const [search, setSearch] = useState("");

  const [data, setData] = useState({
    programs: [],
    statements: [],
    network: [],
    timers: [],
    constants: [],
    parameters: [],
    registers: [],
  });

  const [loading, setLoading] = useState(true);

  // ==========================================================
  // LOAD ENGINEERING DATA
  // ==========================================================

  const loadEngineering = async () => {

    setLoading(true);

    try {

      const responses = await Promise.all([
        fetch(`${API}/programs`),
        fetch(`${API}/statements`),
        fetch(`${API}/network`),
        fetch(`${API}/timers`),
        fetch(`${API}/servo/constants`),
        fetch(`${API}/motion/parameters`),
        fetch(`${API}/motion/registers`),
      ]);

      const results = await Promise.all(
        responses.map((response) =>
          response.ok
            ? response.json()
            : []
        )
      );

      setData({
        programs: normalize(results[0]),
        statements: normalize(results[1]),
        network: normalize(results[2]),
        timers: normalize(results[3]),
        constants: normalize(results[4]),
        parameters: normalize(results[5]),
        registers: normalize(results[6]),
      });

    } catch (error) {

      console.error(
        "Engineering loading error:",
        error
      );

    } finally {

      setLoading(false);

    }
  };

  useEffect(() => {
    loadEngineering();
  }, []);

  // ==========================================================
  // SEARCH
  // ==========================================================

  const filterData = (items) => {

    if (!search.trim()) {
      return items;
    }

    const query =
      search.toLowerCase();

    return items.filter((item) =>
      JSON.stringify(item)
        .toLowerCase()
        .includes(query)
    );
  };

  // ==========================================================
  // TAB CONTENT
  // ==========================================================

  const renderContent = () => {

    if (loading) {

      return (
        <Box className="engineering-loading">
          <CircularProgress />
          <Typography>
            Loading engineering database...
          </Typography>
        </Box>
      );
    }

    switch (tab) {

      case 0:
        return (
          <DataTable
            title="PLC Programs"
            data={filterData(data.programs)}
          />
        );

      case 1:
        return (
          <DataTable
            title="Program Statements"
            data={filterData(data.statements)}
          />
        );

      case 2:
        return (
          <DataTable
            title="Network"
            data={filterData(data.network)}
          />
        );

      case 3:
        return (
          <DataTable
            title="Timers"
            data={filterData(data.timers)}
          />
        );

      case 4:
        return (
          <DataTable
            title="Servo Constants"
            data={filterData(data.constants)}
          />
        );

      case 5:
        return (
          <DataTable
            title="Motion Parameters"
            data={filterData(data.parameters)}
          />
        );

      case 6:
        return (
          <DataTable
            title="Motion Registers"
            data={filterData(data.registers)}
          />
        );

      default:
        return null;
    }
  };

  return (

    <Box className="engineering-page">

      {/* =====================================================
          HEADER
          ===================================================== */}

      <Box className="engineering-header">

        <Box>

          <Typography className="engineering-title">
            Engineering
          </Typography>

          <Typography className="engineering-subtitle">
            PLC programs, motion configuration and servo data
          </Typography>

        </Box>

        <Chip
          icon={<SettingsIcon />}
          label="ENGINEERING DATABASE"
          className="engineering-chip"
        />

      </Box>

      {/* =====================================================
          SUMMARY
          ===================================================== */}

      <Grid
        container
        spacing={2}
        className="engineering-summary"
      >

        <SummaryCard
          icon={<CodeIcon />}
          title="Programs"
          value={data.programs.length}
        />

        <SummaryCard
          icon={<MemoryIcon />}
          title="Statements"
          value={data.statements.length}
        />

        <SummaryCard
          icon={<SettingsIcon />}
          title="Servo Constants"
          value={data.constants.length}
        />

        <SummaryCard
          icon={<TimerIcon />}
          title="Timers"
          value={data.timers.length}
        />

      </Grid>

      {/* =====================================================
          MAIN ENGINEERING CARD
          ===================================================== */}

      <Card className="engineering-card">

        <CardContent>

          {/* SEARCH */}

          <Box className="engineering-toolbar">

            <TextField
              value={search}
              onChange={(e) =>
                setSearch(e.target.value)
              }
              placeholder="Search address, device, register, instruction..."
              size="small"
              className="engineering-search"
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <SearchIcon />
                  </InputAdornment>
                ),
              }}
            />

          </Box>

          {/* TABS */}

          <Tabs
            value={tab}
            onChange={(_, value) =>
              setTab(value)
            }
            variant="scrollable"
            scrollButtons="auto"
            className="engineering-tabs"
          >

            <Tab label="Programs" />

            <Tab label="Statements" />

            <Tab label="Network" />

            <Tab label="Timers" />

            <Tab label="Servo Constants" />

            <Tab label="Motion Parameters" />

            <Tab label="Motion Registers" />

          </Tabs>

          {/* CONTENT */}

          <Box className="engineering-content">
            {renderContent()}
          </Box>

        </CardContent>

      </Card>

    </Box>
  );
}


// ==========================================================
// SUMMARY CARD
// ==========================================================

function SummaryCard({
  icon,
  title,
  value,
}) {

  return (

    <Grid item xs={12} sm={6} md={3}>

      <Card className="engineering-summary-card">

        <CardContent>

          <Box className="engineering-summary-icon">
            {icon}
          </Box>

          <Typography className="engineering-summary-label">
            {title}
          </Typography>

          <Typography className="engineering-summary-value">
            {value}
          </Typography>

        </CardContent>

      </Card>

    </Grid>
  );
}


// ==========================================================
// NORMALIZE API RESPONSE
// ==========================================================

function normalize(response) {

  if (Array.isArray(response)) {
    return response;
  }

  if (!response || typeof response !== "object") {
    return [];
  }

  if (Array.isArray(response.data)) {
    return response.data;
  }

  if (Array.isArray(response.items)) {
    return response.items;
  }

  if (Array.isArray(response.results)) {
    return response.results;
  }

  /*
   * Some endpoints may return:
   *
   * {
   *   "count": 10,
   *   "devices": [...]
   * }
   */

  const arrayKey = Object.keys(response).find(
    (key) =>
      Array.isArray(response[key])
  );

  if (arrayKey) {
    return response[arrayKey];
  }

  return [response];
}


// ==========================================================
// DATA TABLE
// ==========================================================

function DataTable({
  title,
  data,
}) {

  if (!data.length) {

    return (
      <Box className="engineering-empty">

        <MemoryIcon />

        <Typography>
          No {title.toLowerCase()} found.
        </Typography>

      </Box>
    );
  }

  /*
   * Build columns dynamically because your
   * engineering endpoints may return different
   * database structures.
   */

  const columns = Array.from(
    new Set(
      data.flatMap((item) =>
        typeof item === "object"
          ? Object.keys(item)
          : ["value"]
      )
    )
  ).slice(0, 8);

  return (

    <Box>

      <Box className="table-header">

        <Typography className="table-title">
          {title}
        </Typography>

        <Chip
          size="small"
          label={`${data.length} records`}
        />

      </Box>

      <Box className="engineering-table-wrapper">

        <table className="engineering-table">

          <thead>

            <tr>

              {columns.map((column) => (

                <th key={column}>
                  {formatColumn(column)}
                </th>

              ))}

            </tr>

          </thead>

          <tbody>

            {data.slice(0, 300).map(
              (item, rowIndex) => (

                <tr key={rowIndex}>

                  {columns.map((column) => {

                    const value =
                      typeof item === "object"
                        ? item[column]
                        : item;

                    return (
                      <td key={column}>
                        <TableValue
                          value={value}
                        />
                      </td>
                    );

                  })}

                </tr>

              )
            )}

          </tbody>

        </table>

      </Box>

      {data.length > 300 && (

        <Typography className="table-limit">
          Showing first 300 records of {data.length}.
        </Typography>

      )}

    </Box>
  );
}


// ==========================================================
// TABLE VALUE
// ==========================================================

function TableValue({ value }) {

  if (
    value === true ||
    value === false
  ) {

    return (
      <Chip
        size="small"
        label={value ? "TRUE" : "FALSE"}
        className={
          value
            ? "value-active"
            : "value-inactive"
        }
      />
    );
  }

  if (
    value === null ||
    value === undefined
  ) {

    return (
      <span className="null-value">
        —
      </span>
    );
  }

  return (
    <span>
      {String(value)}
    </span>
  );
}


// ==========================================================
// COLUMN FORMAT
// ==========================================================

function formatColumn(column) {

  return String(column)
    .replace(/_/g, " ")
    .replace(/\b\w/g, (char) =>
      char.toUpperCase()
    );
}