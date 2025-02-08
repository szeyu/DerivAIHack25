import React, { useState, useEffect } from "react";
import "./Admin.css";

const Admin = () => {
  const [disputeData, setDisputeData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Check localStorage for new dispute data
    const checkForNewData = () => {
      const storedData = localStorage.getItem("disputeData");
      if (storedData) {
        try {
          setDisputeData(JSON.parse(storedData));
          // Clear the data after reading
          localStorage.removeItem("disputeData");
        } catch (e) {
          setError("Error parsing dispute data");
        }
      }
    };

    // Check immediately and set up interval
    checkForNewData();
    const interval = setInterval(checkForNewData, 1000);

    return () => clearInterval(interval);
  }, []);

  const parseAnalysis = (analysis) => {
    const lines = analysis.split("\n");
    return {
      highlightedWords: lines[0].replace("Highlighted Words: ", "").split(", "),
      suspiciousPatterns: lines[1].replace("Suspicious Patterns: ", ""),
      riskLevel: lines[2].replace("Risk Level: ", ""),
    };
  };

  if (!disputeData) {
    return (
      <div className="admin-container">
        <div className="admin-content">
          <div className="card dispute-summary">
            <h2>Waiting for Dispute Data...</h2>
            <p>No active disputes to review</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="admin-container">
      <div className="admin-content">
        {/* Dispute Summary Section */}
        <div className="card dispute-summary">
          <div className="card-header">
            <h2>Dispute Summary</h2>
            <button className="resolve-button">
              <span className="flag-icon">🚩</span>
              Mark as Resolved
            </button>
          </div>
          <p className="summary-text">{disputeData.summary}</p>
        </div>

        {/* Fraud Analysis Section */}
        <div className="users-grid">
          {["userA", "userB"].map((user) => {
            const analysis = parseAnalysis(
              disputeData.fraudAnalysis[user].analysis
            );
            return (
              <div key={user} className="card user-card">
                <div className="user-header">
                  <span className="user-icon">👤</span>
                  <h3>{disputeData.fraudAnalysis[user].name}</h3>
                  <span
                    className={`risk-badge ${analysis.riskLevel.toLowerCase()}`}
                  >
                    {analysis.riskLevel}
                  </span>
                </div>
                <div className="analysis-content">
                  <div className="highlighted-words">
                    {analysis.highlightedWords.map((word, i) => (
                      <span key={i} className="word-tag">
                        {word}
                      </span>
                    ))}
                  </div>
                  <div className="patterns-box">
                    <h4>Suspicious Patterns:</h4>
                    <p>{analysis.suspiciousPatterns}</p>
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        {/* Similar Cases Section */}
        <div className="card recommendations">
          <h3>Similar Case Analysis</h3>
          <div className="similar-case-content">
            <div className="case-box">
              <h4>Most Similar Case:</h4>
              <p>{disputeData.similarCase.case}</p>
            </div>
            <div className="reasoning-box">
              <h4>Reasoning:</h4>
              <p>{disputeData.similarCase.reasoning}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Admin;
