import React from 'react';
import './Admin.css';

const Admin = () => {
  const mockDispute = {
    summary: "Payment dispute regarding service delivery timeline",
    userA: {
      name: "User A",
      messages: ["I expected the delivery by last week", "This is unacceptable"],
      riskScore: 0.2,
    },
    userB: {
      name: "User B",
      messages: ["We clearly stated 2-3 weeks processing time", "Let me check the status"],
      riskScore: 0.1,
    },
    recommendations: [
      "Review service agreement terms",
      "Clarify delivery timeline expectations",
      "Consider partial refund as goodwill gesture",
    ],
  };

  return (
    <div className="admin-container">
      <div className="admin-content">
        <div className="card dispute-summary">
          <div className="card-header">
            <h2>Dispute Summary</h2>
            <button className="resolve-button">
              <span className="flag-icon">🚩</span>
              Mark as Resolved
            </button>
          </div>
          <p className="summary-text">{mockDispute.summary}</p>
        </div>

        <div className="users-grid">
          <div className="card user-card">
            <div className="user-header">
              <span className="user-icon">👤</span>
              <h3>{mockDispute.userA.name}</h3>
            </div>
            <div className="messages-container">
              {mockDispute.userA.messages.map((msg, i) => (
                <div key={i} className="message">
                  {msg}
                </div>
              ))}
            </div>
            <div className="risk-score">
              <span className="alert-icon">⚠️</span>
              Risk Score: {mockDispute.userA.riskScore * 100}%
            </div>
          </div>

          <div className="card user-card">
            <div className="user-header">
              <span className="user-icon">👤</span>
              <h3>{mockDispute.userB.name}</h3>
            </div>
            <div className="messages-container">
              {mockDispute.userB.messages.map((msg, i) => (
                <div key={i} className="message">
                  {msg}
                </div>
              ))}
            </div>
            <div className="risk-score">
              <span className="alert-icon">⚠️</span>
              Risk Score: {mockDispute.userB.riskScore * 100}%
            </div>
          </div>
        </div>

        <div className="card recommendations">
          <h3>Recommended Actions</h3>
          <ul className="recommendations-list">
            {mockDispute.recommendations.map((rec, i) => (
              <li key={i} className="recommendation-item">
                <span className="recommendation-number">{i + 1}</span>
                <span className="recommendation-text">{rec}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
};

export default Admin;