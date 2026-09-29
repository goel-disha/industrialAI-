import React, { useEffect, useState } from "react";
import {
  Box,
  Card,
  CardContent,
  Typography,
  TextField,
  InputAdornment,
  List,
  ListItemButton,
  ListItemText,
  Chip,
  Divider,
  CircularProgress,
} from "@mui/material";

import SearchIcon from "@mui/icons-material/Search";
import MemoryIcon from "@mui/icons-material/Memory";
import SensorsIcon from "@mui/icons-material/Sensors";
import AccountTreeIcon from "@mui/icons-material/AccountTree";

import "../styles/explorer.css";

const API = import.meta.env.VITE_API_URL || "http://localhost:8000";

const GROUPS = [
  {
    key: "inputs",
    title: "Inputs",
    prefix: "X",
  },
  {
    key: "outputs",
    title: "Outputs",
    prefix: "Y",
  },
  {
    key: "markers",
    title: "Markers",
    prefix: "M",
  },
  {
    key: "internal",
    title: "Internal Relays",
    prefix: "L",
  },
  {
    key: "data",
    title: "Data Registers",
    prefix: "D",
  },
];

export default function Explorer() {
  const [devices, setDevices] = useState([]);
  const [selected, setSelected] = useState(null);
  const [relationships, setRelationships] = useState(null);

  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [detailLoading, setDetailLoading] = useState(false);

  // ==========================================================
  // LOAD DEVICES
  // ==========================================================

  const loadDevices = async () => {
    try {
      setLoading(true);

      const response = await fetch(`${API}/devices`);

      if (!response.ok) {
        throw new Error("Device API failed");
      }

      const data = await response.json();

      const list = normalizeDevices(data);

      setDevices(list);

      if (!selected && list.length) {
        setSelected(list[0]);
      }
    } catch (error) {
      console.error("Explorer device error:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDevices();
  }, []);

  // ==========================================================
  // DEVICE DETAIL
  // ==========================================================

  const selectDevice = async (device) => {
    setSelected(device);
    setRelationships(null);
    setDetailLoading(true);

    try {
      const response = await fetch(
        `${API}/devices/${encodeURIComponent(device.address)}`
      );

      if (response.ok) {
        const detail = await response.json();

        setSelected({
          ...device,
          ...detail,
        });
      }
    } catch (error) {
      console.error("Device detail error:", error);
    }

    try {
      const response = await fetch(
        `${API}/relationships/${encodeURIComponent(device.address)}`
      );

      if (response.ok) {
        const data = await response.json();
        setRelationships(data);
      }
    } catch (error) {
      console.error("Relationship error:", error);
    } finally {
      setDetailLoading(false);
    }
  };

  // ==========================================================
  // SEARCH
  // ==========================================================

  const filteredDevices = devices.filter((device) =>
    JSON.stringify(device)
      .toLowerCase()
      .includes(search.toLowerCase())
  );

  // ==========================================================
  // GROUP
  // ==========================================================

  const getGroupDevices = (prefix) => {
    return filteredDevices.filter((device) =>
      String(device.address || "")
        .toUpperCase()
        .startsWith(prefix)
    );
  };

  return (
    <Box className="explorer-page">

      {/* =====================================================
          HEADER
          ===================================================== */}

      <Box className="explorer-header">

        <Box>

          <Typography className="explorer-title">
            PLC Explorer
          </Typography>

          <Typography className="explorer-subtitle">
            Browse devices, registers and engineering relationships
          </Typography>

        </Box>

        <Chip
          icon={<MemoryIcon />}
          label={`${devices.length} DEVICES`}
          className="explorer-count"
        />

      </Box>

      {/* =====================================================
          SEARCH
          ===================================================== */}

      <Card className="explorer-search-card">

        <CardContent>

          <TextField
            fullWidth
            size="small"
            value={search}
            onChange={(event) =>
              setSearch(event.target.value)
            }
            placeholder="Search X20, Y46, M90, L501, D300..."
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
          MAIN EXPLORER
          ===================================================== */}

      <Box className="explorer-layout">

        {/* ===================================================
            TREE
            =================================================== */}

        <Card className="explorer-tree">

          <CardContent>

            <Typography className="explorer-panel-title">
              PLC Devices
            </Typography>

            {loading ? (

              <Box className="explorer-loading">
                <CircularProgress size={25} />
              </Box>

            ) : (

              <List disablePadding>

                {GROUPS.map((group) => {

                  const groupDevices =
                    getGroupDevices(group.prefix);

                  return (

                    <Box key={group.key}>

                      <Box className="device-group-title">

                        <Typography>
                          {group.title}
                        </Typography>

                        <Chip
                          size="small"
                          label={groupDevices.length}
                        />

                      </Box>

                      {groupDevices
                        .slice(0, 150)
                        .map((device) => (

                          <ListItemButton
                            key={device.address}
                            selected={
                              selected?.address ===
                              device.address
                            }
                            onClick={() =>
                              selectDevice(device)
                            }
                            className="device-item"
                          >

                            <Box
                              className={
                                device.active
                                  ? "device-led active"
                                  : "device-led"
                              }
                            />

                            <ListItemText
                              primary={
                                device.address
                              }
                              secondary={
                                device.name ||
                                device.description ||
                                ""
                              }
                            />

                            <Typography
                              className="device-value"
                            >
                              {device.value ?? "0"}
                            </Typography>

                          </ListItemButton>

                        ))}

                    </Box>
                  );
                })}

              </List>

            )}

          </CardContent>

        </Card>

        {/* ===================================================
            DETAIL PANEL
            =================================================== */}

        <Card className="explorer-detail">

          <CardContent>

            {!selected ? (

              <Box className="no-device">

                <SensorsIcon />

                <Typography>
                  Select a PLC device
                </Typography>

              </Box>

            ) : (

              <>

                <Box className="detail-header">

                  <Box>

                    <Typography className="detail-address">
                      {selected.address}
                    </Typography>

                    <Typography className="detail-name">
                      {selected.name ||
                        selected.description ||
                        "PLC Device"}
                    </Typography>

                  </Box>

                  <Chip
                    label={
                      selected.active
                        ? "ACTIVE"
                        : "INACTIVE"
                    }
                    className={
                      selected.active
                        ? "detail-active"
                        : "detail-inactive"
                    }
                  />

                </Box>

                <Divider sx={{ my: 2 }} />

                {/* VALUE */}

                <Box className="detail-value-box">

                  <Typography className="detail-label">
                    CURRENT VALUE
                  </Typography>

                  <Typography className="detail-value">
                    {selected.value ?? "0"}
                  </Typography>

                </Box>

                {/* DETAILS */}

                <Box className="detail-section">

                  <Typography className="detail-section-title">
                    Device Information
                  </Typography>

                  <DetailRow
                    label="Address"
                    value={selected.address}
                  />

                  <DetailRow
                    label="Value"
                    value={selected.value ?? "0"}
                  />

                  <DetailRow
                    label="Active"
                    value={
                      selected.active
                        ? "YES"
                        : "NO"
                    }
                  />

                  <DetailRow
                    label="Type"
                    value={
                      getDeviceType(
                        selected.address
                      )
                    }
                  />

                </Box>

                {/* RELATIONSHIPS */}

                <Box className="detail-section">

                  <Box className="relationship-heading">

                    <AccountTreeIcon />

                    <Typography className="detail-section-title">
                      Relationships
                    </Typography>

                  </Box>

                  {detailLoading ? (

                    <CircularProgress size={20} />

                  ) : (

                    <RelationshipList
                      relationships={
                        relationships
                      }
                    />

                  )}

                </Box>

              </>

            )}

          </CardContent>

        </Card>

      </Box>

    </Box>
  );
}


// ==========================================================
// NORMALIZE
// ==========================================================

function normalizeDevices(data) {

  if (Array.isArray(data)) {
    return data;
  }

  if (data?.devices &&
      Array.isArray(data.devices)) {
    return data.devices;
  }

  if (data?.data &&
      Array.isArray(data.data)) {
    return data.data;
  }

  return [];
}


// ==========================================================
// DEVICE TYPE
// ==========================================================

function getDeviceType(address) {

  const prefix =
    String(address || "")
      .toUpperCase()
      .replace(/[0-9]/g, "");

  const types = {
    X: "Digital Input",
    Y: "Digital Output",
    M: "Internal Relay",
    L: "Internal Logic",
    D: "Data Register",
    T: "Timer",
    C: "Counter",
  };

  return types[prefix] || "PLC Device";
}


// ==========================================================
// DETAIL ROW
// ==========================================================

function DetailRow({
  label,
  value,
}) {

  return (

    <Box className="detail-row">

      <Typography className="detail-row-label">
        {label}
      </Typography>

      <Typography className="detail-row-value">
        {String(value ?? "—")}
      </Typography>

    </Box>
  );
}


// ==========================================================
// RELATIONSHIP LIST
// ==========================================================

function RelationshipList({
  relationships,
}) {

  if (!relationships) {

    return (
      <Typography className="relationship-empty">
        No relationship data available.
      </Typography>
    );
  }

  const items = Array.isArray(relationships)
    ? relationships
    : relationships.relationships ||
      relationships.data ||
      [];

  if (!items.length) {

    return (
      <Typography className="relationship-empty">
        No related devices found.
      </Typography>
    );
  }

  return (

    <Box className="relationship-list">

      {items.slice(0, 20).map(
        (item, index) => {

          if (
            typeof item !== "object"
          ) {

            return (
              <Chip
                key={index}
                label={String(item)}
                className="relationship-chip"
              />
            );
          }

          const address =
            item.address ||
            item.device ||
            item.register ||
            item.source ||
            "Unknown";

          const description =
            item.description ||
            item.name ||
            item.type ||
            "";

          return (

            <Box
              key={index}
              className="relationship-item"
            >

              <Typography className="relationship-address">
                {address}
              </Typography>

              <Typography className="relationship-description">
                {description}
              </Typography>

            </Box>
          );
        }
      )}

    </Box>
  );
}