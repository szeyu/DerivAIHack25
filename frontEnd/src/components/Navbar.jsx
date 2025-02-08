import React from "react";
import { Link, useLocation } from "react-router-dom";
import "./Navbar.css";

const Navbar = () => {
  const location = useLocation();

  return (
    <nav className="navbar">
      <div className="navbar-container">
        <div /> {/* Empty div for grid balance */}
        <div className="navbar-links">
          <Link
            to="/"
            className={`nav-link ${location.pathname === "/" ? "active" : ""}`}
          >
            Home
          </Link>
          <Link
            to="/admin"
            className={`nav-link ${
              location.pathname === "/admin" ? "active" : ""
            }`}
          >
            Admin
          </Link>
        </div>
        <div /> {/* Empty div for grid balance */}
      </div>
    </nav>
  );
};

export default Navbar;