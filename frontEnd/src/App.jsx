import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { ChatProvider } from "./context/ChatContext";
import Navbar from "./components/Navbar";
import MainPage from "./MainPage";
import Admin from "./Admin";
import "./App.css";
import Alerts from "./Alerts";

function App() {
  return (
    <ChatProvider>
      <Router>
        <div className="app">
          <Navbar />
          <div className="content">
            <Routes>
              <Route path="/" element={<MainPage />} />
              <Route path="/admin" element={<Admin />} />
              <Route path="/alerts" element={<Alerts />} />
            </Routes>
          </div>
        </div>
      </Router>
    </ChatProvider>
  );
}

export default App;
