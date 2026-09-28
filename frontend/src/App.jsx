import React from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";

import Layout from "./components/layout";

import Dashboard from "./pages/dashboard";
import Live from "./pages/livemonitor";
import Analytics from "./pages/analytics";
import Engineering from "./pages/engineering";
import Explorer from "./pages/explorer";
import Alarms from "./pages/alarm";
import Search from "./pages/search";
import Assistant from "./pages/assistant";

function App() {
  return (
    <BrowserRouter>
      <Routes>

        <Route path="/" element={<Layout />}>

          <Route index element={<Navigate to="/dashboard" replace />} />

          <Route path="dashboard" element={<Dashboard />} />
          <Route path="live" element={<Live />} />
          <Route path="analytics" element={<Analytics />} />
          <Route path="engineering" element={<Engineering />} />
          <Route path="explorer" element={<Explorer />} />
          <Route path="alarms" element={<Alarms />} />
          <Route path="search" element={<Search />} />
          <Route path="assistant" element={<Assistant />} />

          <Route
            path="*"
            element={<Navigate to="/dashboard" replace />}
          />

        </Route>

      </Routes>
    </BrowserRouter>
  );
}

export default App;