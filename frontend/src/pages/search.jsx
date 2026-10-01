import React, { useEffect, useState } from "react";
import {
  Box,
  Card,
  CardContent,
  Typography,
  TextField,
  InputAdornment,
  Chip,
  CircularProgress,
  Divider,
} from "@mui/material";

import SearchIcon from "@mui/icons-material/Search";
import MemoryIcon from "@mui/icons-material/Memory";
import CodeIcon from "@mui/icons-material/Code";
import SettingsIcon from "@mui/icons-material/Settings";
import WarningAmberIcon from "@mui/icons-material/WarningAmber";

import "../styles/search.css";

const API = import.meta.env.VITE_API_URL || (import.meta.env.VITE_API_HOST ? `https://${import.meta.env.VITE_API_HOST}` : "http://localhost:8000");

export default function SearchPage() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);

  // ==========================================================
  // SEARCH
  // ==========================================================

  const performSearch = async (value = query) => {
    const searchValue = value.trim();

    if (!searchValue) {
      setResults([]);
      setSearched(false);
      return;
    }

    try {
      setLoading(true);
      setSearched(true);

      const response = await fetch(
        `${API}/search?query=${encodeURIComponent(searchValue)}`
      );

      if (!response.ok) {
        throw new Error("Search request failed");
      }

      const data = await response.json();

      setResults(normalizeResults(data));
    } catch (error) {
      console.error("Search error:", error);
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  // ==========================================================
  // DEBOUNCED SEARCH
  // ==========================================================

  useEffect(() => {
    if (!query.trim()) {
      setResults([]);
      setSearched(false);
      return;
    }

    const timer = setTimeout(() => {
      performSearch(query);
    }, 400);

    return () => clearTimeout(timer);
  }, [query]);

  // ==========================================================
  // RENDER
  // ==========================================================

  return (
    <Box className="search-page">

      {/* =====================================================
          HEADER
          ===================================================== */}

      <Box className="search-header">

        <Box>
          <Typography className="search-title">
            Global Search
          </Typography>

          <Typography className="search-subtitle">
            Search PLC devices, programs, registers, alarms
            and engineering data
          </Typography>
        </Box>

        <Chip
          icon={<SearchIcon />}
          label="PLC DATABASE"
          className="search-chip"
        />

      </Box>

      {/* =====================================================
          SEARCH BOX
          ===================================================== */}

      <Card className="search-box-card">

        <CardContent>

          <TextField
            fullWidth
            autoFocus
            value={query}
            onChange={(event) =>
              setQuery(event.target.value)
            }
            onKeyDown={(event) => {
              if (event.key === "Enter") {
                performSearch();
              }
            }}
            placeholder="Search X20, L501, D300, servo, program, alarm..."
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon />
                </InputAdornment>
              ),
            }}
          />

        </CardContent>

      </Card>

      {/* =====================================================
          RESULTS
          ===================================================== */}

      <Card className="results-card">

        <CardContent>

          <Box className="results-header">

            <Box>

              <Typography className="results-title">
                Search Results
              </Typography>

              {searched && (
                <Typography className="results-subtitle">
                  {results.length} result
                  {results.length !== 1 ? "s" : ""} for "
                  {query}"
                </Typography>
              )}

            </Box>

            {searched && (
              <Chip
                label={`${results.length} Results`}
              />
            )}

          </Box>

          <Divider />

          {loading ? (

            <Box className="search-loading">

              <CircularProgress />

              <Typography>
                Searching engineering database...
              </Typography>

            </Box>

          ) : !searched ? (

            <SearchPlaceholder />

          ) : results.length === 0 ? (

            <NoResults query={query} />

          ) : (

            <Box className="results-list">

              {results.map(
                (result, index) => (
                  <SearchResult
                    key={index}
                    result={result}
                  />
                )
              )}

            </Box>

          )}

        </CardContent>

      </Card>

    </Box>
  );
}


// ==========================================================
// RESULT NORMALIZATION
// ==========================================================

function normalizeResults(data) {

  if (Array.isArray(data)) {
    return data;
  }

  if (!data || typeof data !== "object") {
    return [];
  }

  if (Array.isArray(data.results)) {
    return data.results;
  }

  if (Array.isArray(data.data)) {
    return data.data;
  }

  if (Array.isArray(data.devices)) {
    return data.devices;
  }

  if (Array.isArray(data.items)) {
    return data.items;
  }

  /*
   * If backend returns a single object,
   * display it as one result.
   */

  return [data];
}


// ==========================================================
// SEARCH RESULT
// ==========================================================

function SearchResult({ result }) {

  const address =
    result.address ||
    result.device ||
    result.register ||
    result.code ||
    "";

  const name =
    result.name ||
    result.title ||
    result.description ||
    result.message ||
    "Engineering Result";

  const type =
    result.type ||
    result.category ||
    result.table ||
    getType(address);

  const value =
    result.value ??
    result.current_value ??
    result.status ??
    "";

  return (

    <Box className="search-result">

      <Box className="result-icon">
        {getIcon(type)}
      </Box>

      <Box className="result-main">

        <Box className="result-top">

          <Typography className="result-name">
            {name}
          </Typography>

          <Chip
            size="small"
            label={String(type)}
            className="result-type"
          />

        </Box>

        <Typography className="result-address">
          {address || "No address"}
        </Typography>

        <Typography className="result-description">
          {getDescription(result)}
        </Typography>

      </Box>

      {value !== "" && (
        <Box className="result-value">
          {String(value)}
        </Box>
      )}

    </Box>
  );
}


// ==========================================================
// DESCRIPTION
// ==========================================================

function getDescription(result) {

  const ignored = [
    "address",
    "device",
    "register",
    "code",
    "name",
    "title",
    "description",
    "message",
    "type",
    "category",
    "table",
    "value",
    "current_value",
    "status",
  ];

  const entries = Object.entries(result);

  const useful = entries.filter(
    ([key, value]) =>
      !ignored.includes(key) &&
      value !== null &&
      value !== undefined &&
      value !== ""
  );

  if (!useful.length) {
    return "PLC engineering data";
  }

  return useful
    .slice(0, 3)
    .map(
      ([key, value]) =>
        `${formatKey(key)}: ${value}`
    )
    .join(" • ");
}


// ==========================================================
// TYPE
// ==========================================================

function getType(address) {

  const value =
    String(address || "")
      .toUpperCase();

  if (value.startsWith("X")) {
    return "Input";
  }

  if (value.startsWith("Y")) {
    return "Output";
  }

  if (value.startsWith("M")) {
    return "Marker";
  }

  if (value.startsWith("L")) {
    return "Logic";
  }

  if (value.startsWith("D")) {
    return "Register";
  }

  if (value.startsWith("T")) {
    return "Timer";
  }

  return "Engineering";
}


// ==========================================================
// ICON
// ==========================================================

function getIcon(type) {

  const value =
    String(type)
      .toLowerCase();

  if (
    value.includes("alarm") ||
    value.includes("fault")
  ) {
    return <WarningAmberIcon />;
  }

  if (
    value.includes("program") ||
    value.includes("statement")
  ) {
    return <CodeIcon />;
  }

  if (
    value.includes("servo") ||
    value.includes("motion")
  ) {
    return <SettingsIcon />;
  }

  return <MemoryIcon />;
}


// ==========================================================
// FORMAT KEY
// ==========================================================

function formatKey(key) {

  return String(key)
    .replace(/_/g, " ")
    .replace(/\b\w/g, (char) =>
      char.toUpperCase()
    );
}


// ==========================================================
// PLACEHOLDER
// ==========================================================

function SearchPlaceholder() {

  return (

    <Box className="search-placeholder">

      <SearchIcon />

      <Typography className="placeholder-title">
        Search the IndustrialAI database
      </Typography>

      <Typography className="placeholder-text">
        Search by PLC address, device name,
        program, register, alarm or engineering data.
      </Typography>

      <Box className="search-examples">

        <Chip label="D300" />
        <Chip label="L501" />
        <Chip label="X20" />
        <Chip label="Servo" />
        <Chip label="Alarm" />

      </Box>

    </Box>
  );
}


// ==========================================================
// NO RESULTS
// ==========================================================

function NoResults({ query }) {

  return (

    <Box className="search-placeholder">

      <SearchIcon />

      <Typography className="placeholder-title">
        No results found
      </Typography>

      <Typography className="placeholder-text">
        Nothing matched "{query}".
        Try a PLC address or engineering keyword.
      </Typography>

    </Box>
  );
}