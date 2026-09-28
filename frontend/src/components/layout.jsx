import React from "react";
import { Outlet, NavLink } from "react-router-dom";
import "../styles/layout.css";

export default function Layout() {
  const links = [
    { name: "Dashboard", path: "/dashboard" },
    { name: "Live Monitor", path: "/live" },
    { name: "Analytics", path: "/analytics" },
    { name: "Engineering", path: "/engineering" },
    { name: "Explorer", path: "/explorer" },
    { name: "Alarms", path: "/alarms" },
    { name: "Search", path: "/search" },
    { name: "AI Assistant", path: "/assistant" },
  ];

  return (
    <div className="app-layout">

      <aside className="sidebar">

        <div className="sidebar-logo">
          <div className="logo-title">IndustrialAI</div>
          <div className="logo-subtitle">Digital Twin</div>
        </div>

        <nav className="sidebar-nav">
          {links.map((link) => (
            <NavLink
              key={link.path}
              to={link.path}
              className={({ isActive }) =>
                isActive ? "nav-link active" : "nav-link"
              }
            >
              {link.name}
            </NavLink>
          ))}
        </nav>

        <div className="sidebar-footer">
          <div>Mitsubishi</div>
          <div>MELSEC-Q</div>
        </div>

      </aside>

      <div className="main-area">

        <header className="topbar">
          <div>
            <div className="machine-name">
              Mitsubishi Auto Tapping Machine
            </div>
            <div className="machine-subtitle">
              IndustrialAI Digital Twin
            </div>
          </div>

          <div className="topbar-status">
            <span className="status-dot"></span>
            SYSTEM ONLINE
          </div>
        </header>

        <main className="page-content">
          <Outlet />
        </main>

      </div>

    </div>
  );
}