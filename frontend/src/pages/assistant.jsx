import React, { useEffect, useRef, useState } from "react";
import {
  Box,
  Card,
  CardContent,
  Typography,
  TextField,
  IconButton,
  Chip,
  CircularProgress,
  Divider,
} from "@mui/material";

import SmartToyIcon from "@mui/icons-material/SmartToy";
import DeleteOutlineIcon from "@mui/icons-material/DeleteOutline";
import PersonIcon from "@mui/icons-material/Person";
import SendIcon from "@mui/icons-material/Send";

import "../styles/assistant.css";

const API = import.meta.env.VITE_API_URL || "http://localhost:8000";

export default function AIAssistant() {
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      text:
        "Hello! I am the IndustrialAI Assistant. Ask me about the machine, PLC, servo axes, alarms, registers, or current machine status.",
    },
  ]);

  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const [machine, setMachine] = useState(null);

  const messagesEndRef = useRef(null);

  // ==========================================================
  // LOAD MACHINE CONTEXT
  // ==========================================================

  const loadMachine = async () => {
    try {
      const response = await fetch(`${API}/machine`);

      if (!response.ok) {
        return;
      }

      const data = await response.json();

      setMachine(data);
    } catch (error) {
      console.error(
        "Machine context error:",
        error
      );
    }
  };

  useEffect(() => {
    loadMachine();

    const interval = setInterval(
      loadMachine,
      2000
    );

    return () => clearInterval(interval);
  }, []);

  // ==========================================================
  // AUTO SCROLL
  // ==========================================================

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({
      behavior: "smooth",
    });
  }, [messages]);

  // ==========================================================
  // SEND MESSAGE
  // ==========================================================

  const sendMessage = async () => {
    const message = input.trim();

    if (!message || sending) {
      return;
    }

    setInput("");

    setMessages((previous) => [
      ...previous,
      {
        role: "user",
        text: message,
      },
    ]);

    setSending(true);

    try {
      const response = await fetch(
        `${API}/chat`,
        {
          method: "POST",
          headers: {
            "Content-Type":
              "application/json",
          },
          body: JSON.stringify({
            message,
          }),
        }
      );

      if (!response.ok) {
        throw new Error(
          "Chat request failed"
        );
      }

      const data = await response.json();

      setMessages((previous) => [
        ...previous,
        {
          role: "assistant",
          text:
            data.response ||
            data.message ||
            "No response received.",
        },
      ]);
    } catch (error) {
      console.error(
        "Assistant error:",
        error
      );

      setMessages((previous) => [
        ...previous,
        {
          role: "assistant",
          text:
            "Unable to connect to the IndustrialAI backend.",
        },
      ]);
    } finally {
      setSending(false);
    }
  };

  // ==========================================================
  // ENTER KEY
  // ==========================================================

  const handleKeyDown = (event) => {
    if (
      event.key === "Enter" &&
      !event.shiftKey
    ) {
      event.preventDefault();
      sendMessage();
    }
  };

  // ==========================================================
  // CLEAR CHAT
  // ==========================================================

  const clearChat = () => {
    setMessages([
      {
        role: "assistant",
        text:
          "Chat cleared. How can I help with the machine?",
      },
    ]);
  };

  // ==========================================================
  // QUICK QUESTIONS
  // ==========================================================

  const quickQuestions = [
    "What is the current machine state?",
    "What is the status of the servo axes?",
    "Are there any active alarms?",
    "Explain the current PLC sequence.",
  ];

  return (
    <Box className="aiassistant-page">

      {/* =====================================================
          HEADER
          ===================================================== */}

      <Box className="aiassistant-header">

        <Box>

          <Typography className="aiassistant-title">
            AI Assistant
          </Typography>

          <Typography className="aiassistant-subtitle">
            Industrial machine diagnostics and engineering assistant
          </Typography>

        </Box>

        <Chip
          icon={<SmartToyIcon />}
          label="INDUSTRIAL AI"
          className="aiassistant-chip"
        />

      </Box>

      {/* =====================================================
          MAIN LAYOUT
          ===================================================== */}

      <Box className="aiassistant-layout">

        {/* ===================================================
            CHAT
            =================================================== */}

        <Card className="chat-card">

          <CardContent className="chat-card-content">

            <Box className="chat-header">

              <Box className="chat-agent">

                <Box className="assistant-icon">
                  <SmartToyIcon />
                </Box>

                <Box>

                  <Typography className="agent-name">
                    IndustrialAI
                  </Typography>

                  <Typography className="agent-status">
                    Machine Assistant
                  </Typography>

                </Box>

              </Box>

              <IconButton
                onClick={clearChat}
                title="Clear conversation"
              >
                <DeleteOutlineIcon />
              </IconButton>

            </Box>

            <Divider />

            {/* =================================================
                MESSAGES
                ================================================= */}

            <Box className="messages-container">

              {messages.map(
                (message, index) => (

                  <Message
                    key={index}
                    message={message}
                  />

                )
              )}

              {sending && (

                <Box className="typing-indicator">

                  <CircularProgress
                    size={16}
                  />

                  <Typography>
                    IndustrialAI is thinking...
                  </Typography>

                </Box>

              )}

              <div ref={messagesEndRef} />

            </Box>

            {/* =================================================
                QUICK QUESTIONS
                ================================================= */}

            {messages.length <= 1 && (

              <Box className="quick-questions">

                <Typography className="quick-title">
                  Quick questions
                </Typography>

                <Box className="quick-list">

                  {quickQuestions.map(
                    (question) => (

                      <Chip
                        key={question}
                        label={question}
                        onClick={() => {
                          setInput(
                            question
                          );
                        }}
                        className="quick-chip"
                      />

                    )
                  )}

                </Box>

              </Box>

            )}

            {/* =================================================
                INPUT
                ================================================= */}

            <Box className="chat-input-area">

              <TextField
                fullWidth
                multiline
                maxRows={4}
                value={input}
                onChange={(event) =>
                  setInput(
                    event.target.value
                  )
                }
                onKeyDown={handleKeyDown}
                placeholder="Ask about the machine..."
                disabled={sending}
              />

              <IconButton
                className="send-button"
                onClick={sendMessage}
                disabled={
                  !input.trim() ||
                  sending
                }
              >
                <SendIcon />
              </IconButton>

            </Box>

          </CardContent>

        </Card>

        {/* ===================================================
            MACHINE CONTEXT
            =================================================== */}

        <Card className="context-card">

          <CardContent>

            <Typography className="context-title">
              Machine Context
            </Typography>

            <Typography className="context-subtitle">
              Live machine information
            </Typography>

            <Divider sx={{ my: 2 }} />

            {machine ? (

              <>

                <ContextRow
                  label="State"
                  value={
                    machine.state ||
                    machine.machine?.state ||
                    "IDLE"
                  }
                />

                <ContextRow
                  label="Model"
                  value={
                    machine.model ??
                    machine.machine?.model ??
                    1
                  }
                />

                <ContextRow
                  label="Auto Mode"
                  value={
                    booleanText(
                      machine.auto_mode ??
                      machine.machine?.auto_mode
                    )
                  }
                />

                <ContextRow
                  label="Cycle Running"
                  value={
                    booleanText(
                      machine.cycle_running ??
                      machine.machine?.cycle_running
                    )
                  }
                />

                <ContextRow
                  label="Cycle Complete"
                  value={
                    booleanText(
                      machine.cycle_complete ??
                      machine.machine?.cycle_complete
                    )
                  }
                />

                <Divider sx={{ my: 2 }} />

                <Typography className="context-section">
                  Safety
                </Typography>

                <ContextRow
                  label="Emergency"
                  value={
                    booleanText(
                      machine.safety?.emergency
                    )
                  }
                />

                <ContextRow
                  label="Air Fault"
                  value={
                    booleanText(
                      machine.safety?.air_fault
                    )
                  }
                />

                <ContextRow
                  label="Safe"
                  value={
                    booleanText(
                      machine.safety?.safe
                    )
                  }
                />

                <Divider sx={{ my: 2 }} />

                <Typography className="context-section">
                  Sequence
                </Typography>

                <ContextRow
                  label="State"
                  value={
                    machine.sequence?.state ||
                    "IDLE"
                  }
                />

                <ContextRow
                  label="Center Timer"
                  value={
                    machine.sequence?.center_timer ??
                    0
                  }
                />

                <ContextRow
                  label="Center Travel"
                  value={
                    machine.sequence?.center_travel ??
                    0
                  }
                />

              </>

            ) : (

              <Box className="context-loading">

                <CircularProgress size={22} />

                <Typography>
                  Loading machine context...
                </Typography>

              </Box>

            )}

          </CardContent>

        </Card>

      </Box>

    </Box>
  );
}


// ==========================================================
// MESSAGE
// ==========================================================

function Message({ message }) {

  const isUser =
    message.role === "user";

  return (

    <Box
      className={
        isUser
          ? "message-row user-message"
          : "message-row assistant-message"
      }
    >

      <Box className="message-avatar">

        {isUser ? (
          <PersonIcon />
        ) : (
          <SmartToyIcon />
        )}

      </Box>

      <Box className="message-content">

        <Typography className="message-role">
          {isUser
            ? "You"
            : "IndustrialAI"}
        </Typography>

        <Typography className="message-text">
          {message.text}
        </Typography>

      </Box>

    </Box>
  );
}


// ==========================================================
// CONTEXT ROW
// ==========================================================

function ContextRow({
  label,
  value,
}) {

  const stringValue =
    String(value ?? "—");

  const isPositive =
    ["TRUE", "YES", "SAFE"]
      .includes(
        stringValue.toUpperCase()
      );

  return (

    <Box className="context-row">

      <Typography className="context-label">
        {label}
      </Typography>

      <Chip
        size="small"
        label={stringValue}
        className={
          isPositive
            ? "context-positive"
            : "context-value"
        }
      />

    </Box>
  );
}


// ==========================================================
// BOOLEAN FORMAT
// ==========================================================

function booleanText(value) {

  if (
    value === true ||
    value === 1 ||
    value === "1"
  ) {
    return "YES";
  }

  return "NO";
}