import React from "react";
import { NavLink } from "react-router-dom";

export default function Sidebar() {
  return (
    <aside className="sidebar">

      <NavLink to="/dashboard">
        Dashboard
      </NavLink>

      <NavLink to="/live">
        Live Monitor
      </NavLink>

      <NavLink to="/analytics">
        Analytics
      </NavLink>

      <NavLink to="/engineering">
        Engineering
      </NavLink>

      <NavLink to="/explorer">
        Explorer
      </NavLink>

      <NavLink to="/alarms">
        Alarms
      </NavLink>

      <NavLink to="/search">
        Search
      </NavLink>

      <NavLink to="/assistant">
        AI Assistant
      </NavLink>

    </aside>
  );
}