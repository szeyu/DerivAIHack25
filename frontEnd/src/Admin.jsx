import React, { useState, useEffect } from "react";
import "./Admin.css";

const Admin = () => {
  const [summaryVisible, setSummaryVisible] = useState(false);
  const [fraudVisible, setFraudVisible] = useState(false);
  const [similarVisible, setSimilarVisible] = useState(false);

  const hardcodedData = {
    summary:
      "The buyer claims to have sent payment 30 minutes prior and provided proof, demanding immediate crypto release. The seller states the transaction is pending and not yet cleared, refusing to release funds until confirmed. The buyer escalates by accusing the seller of scamming, threatening disputes and negative feedback, while the seller insists on waiting for payment clearance to resolve the issue amicably. Core conflict revolves around payment verification timing and distrust.",
    fraudAnalysis: {
      userA: {
        name: "Buyer",
        analysis:
          'Highlighted Words: "proof already", "report", "scam", "dispute"\nSuspicious Patterns: The buyer aggressively escalates the situation by threatening negative feedback and disputes despite the seller acknowledging a pending transaction. Rapid accusations of "scam" and refusal to wait for transaction confirmation align with pressure tactics often seen in fraud (e.g., coercing release of crypto before confirming payment legitimacy).\nRisk Level: High',
      },
      userB: {
        name: "Seller",
        analysis:
          'Highlighted Words: "pending transaction", "not cleared", "wait for confirmation"\nSuspicious Patterns: While the seller follows a logical process (waiting for payment clearance), referencing a "pending transaction" without specifying the payment method or timing could be vague. However, the lack of defensive aggression and willingness to release after confirmation aligns with standard escrow practices.\nRisk Level: Low',
      },
    },
    similarCase: {
      case: "Buyer sent payment, but the seller claimed not to receive it. After investigation, funds were delayed due to bank processing. Crypto was released after confirmation.",
      reasoning:
        "Both cases center on delayed payment verification requiring confirmation before release, resolving once funds clear.",
    },
  };

  useEffect(() => {
    // Set timers for revealing sections
    const summaryTimer = setTimeout(() => setSummaryVisible(true), 5000);
    const fraudTimer = setTimeout(() => setFraudVisible(true), 10000);
    const similarTimer = setTimeout(() => setSimilarVisible(true), 15000);

    return () => {
      clearTimeout(summaryTimer);
      clearTimeout(fraudTimer);
      clearTimeout(similarTimer);
    };
  }, []);

  const parseAnalysis = (analysis) => {
    const lines = analysis.split("\n");
    return {
      highlightedWords: lines[0].replace("Highlighted Words: ", "").split(", "),
      suspiciousPatterns: lines[1].replace("Suspicious Patterns: ", ""),
      riskLevel: lines[2].replace("Risk Level: ", ""),
    };
  };

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
          {summaryVisible ? (
            <p className="summary-text">{hardcodedData.summary}</p>
          ) : (
            <div className="loading">Analyzing dispute summary...</div>
          )}
        </div>

        {/* Fraud Analysis Section */}
        <div className="users-grid">
          {fraudVisible ? (
            ["userA", "userB"].map((user) => {
              const analysis = parseAnalysis(
                hardcodedData.fraudAnalysis[user].analysis
              );
              return (
                <div key={user} className="card user-card">
                  <div className="user-header">
                    <span className="user-icon">👤</span>
                    <h3>{hardcodedData.fraudAnalysis[user].name}</h3>
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
                          {word.replace(/"/g, "")}
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
            })
          ) : (
            <div className="loading">Analyzing fraud signals...</div>
          )}
        </div>

        {/* Similar Cases Section */}
        <div className="card recommendations">
          <h3>Similar Case Analysis</h3>
          {similarVisible ? (
            <div className="similar-case-content">
              <div className="case-box">
                <h4>Most Similar Case:</h4>
                <p>{hardcodedData.similarCase.case}</p>
              </div>
              <div className="reasoning-box">
                <h4>Reasoning:</h4>
                <p>{hardcodedData.similarCase.reasoning}</p>
              </div>
            </div>
          ) : (
            <div className="loading">Finding similar cases...</div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Admin;
