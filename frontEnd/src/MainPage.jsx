import React, { useRef } from "react";
import { useChat } from "./context/ChatContext";
import "./MainPage.css";
import boyImage from "./assets/boy.png";
import girlImage from "./assets/girl.png";

const MainPage = () => {
  const {
    message,
    setMessage,
    chat,
    setChat,
    currentUser,
    setCurrentUser,
    isAIActive,
    setIsAIActive,
    formattedConversation,
    setFormattedConversation,
  } = useChat();

  const sendMessage = () => {
    if (message.trim() === "") return;

    // Add message to chat display
    const newMessage = { user: currentUser, text: message };
    setChat([...chat, newMessage]);

    // Format conversation
    const formattedMessage = `\n    ${currentUser}: ${message}\n`;
    console.log("Adding message:", formattedMessage); // Debug log
    setFormattedConversation((prev) => {
      const updated = prev + formattedMessage;
      console.log("Updated conversation:", updated); // Debug log
      return updated;
    });

    setMessage("");
    setCurrentUser(currentUser === "Buyer" ? "Seller" : "Buyer");
  };

  const activateAI = async () => {
    setIsAIActive(true);
    console.log("Activating AI with conversation:", formattedConversation); // Debug log

    try {
      // Call summary endpoint
      const summaryResponse = await fetch(
        "http://localhost:8000/api/dispute/summary",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ conversation: formattedConversation }),
        }
      );

      if (!summaryResponse.ok) {
        throw new Error(`Summary API error: ${summaryResponse.status}`);
      }

      const summaryData = await summaryResponse.json();
      console.log("Summary Response:", summaryData);

      // Call fraud analysis endpoint
      const fraudResponse = await fetch(
        "http://localhost:8000/api/dispute/fraud-analysis",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ conversation: formattedConversation }),
        }
      );

      if (!fraudResponse.ok) {
        throw new Error(`Fraud API error: ${fraudResponse.status}`);
      }

      const fraudData = await fraudResponse.json();
      console.log("Fraud Data:", fraudData); // Debug log

      // For similar cases, we need the summary first
      const similarResponse = await fetch(
        "http://localhost:8000/api/dispute/similar-cases",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            current_summary: summaryData.summary,
            past_cases: [
              "Buyer sent payment, but the seller claimed not to receive it. After investigation, funds were delayed due to bank processing. Crypto was released after confirmation.",
              "Buyer claimed they sent payment but provided fake proof. Seller reported fraud, and admin ruled in seller's favor.",
              "Seller promised instant release but delayed without reason. Buyer opened a dispute, and the admin forced release.",
              "Buyer disputed a trade because they changed their mind after payment. Admin rejected the refund request.",
              "A buyer and seller argued about a 1-minute price fluctuation in a volatile market.",
            ],
          }),
        }
      );

      const similarData = await similarResponse.json();
      console.log("Similar Data:", similarData); // Debug log

      // Store responses in localStorage for Admin.jsx to access
      const disputeData = {
        summary: summaryData.summary,
        fraudAnalysis: fraudData.fraud_analysis,
        similarCase: similarData.similar_cases,
      };

      console.log("Storing dispute data:", disputeData); // Debug log
      localStorage.setItem("disputeData", JSON.stringify(disputeData));

      // Add AI response to chat
      setChat([
        ...chat,
        {
          user: "AI",
          text: "I've analyzed your dispute. An admin will review the case shortly.",
        },
      ]);
    } catch (error) {
      console.error("Error calling APIs:", error);
      setChat([
        ...chat,
        {
          user: "AI",
          text: "There was an error processing your dispute. Please try again.",
        },
      ]);
    }
  };

  return (
    <div className="chat-container">
      <div className="chat-wrapper">
        <h1 className="chat-title">Two-Person Chat</h1>

        <div className="chat-messages">
          {chat.map((msg, index) => (
            <div
              key={index}
              className={`message-row ${
                msg.user === "Buyer"
                  ? ""
                  : msg.user === "Seller"
                  ? "reverse"
                  : "ai"
              }`}
            >
              <div className="profile-picture">
                <img
                  src={
                    msg.user === "Buyer"
                      ? boyImage
                      : msg.user === "Seller"
                      ? girlImage
                      : null
                  }
                  alt={
                    msg.user === "Buyer"
                      ? "Buyer"
                      : msg.user === "Seller"
                      ? "Seller"
                      : "AI"
                  }
                  className={`profile-circle ${
                    msg.user === "Buyer"
                      ? "user1"
                      : msg.user === "Seller"
                      ? "user2"
                      : "ai"
                  }`}
                />
              </div>

              <div
                className={`message-bubble ${
                  msg.user === "Buyer"
                    ? "user1"
                    : msg.user === "Seller"
                    ? "user2"
                    : "ai"
                }`}
              >
                <p>{msg.text}</p>
                {msg.type === "request-pdf" && (
                  <div className="pdf-upload-section">
                    <input
                      type="file"
                      accept=".pdf"
                      onChange={(e) => handleFileUpload(e, msg.forUser)}
                      style={{ display: "none" }}
                      ref={fileInputRef}
                    />
                    <button
                      className="upload-button"
                      onClick={() => fileInputRef.current.click()}
                    >
                      Upload PDF
                    </button>
                  </div>
                )}
                {msg.type === "pdf-upload" && (
                  <div className="pdf-preview">
                    <span>📄 {msg.text}</span>
                  </div>
                )}
                {msg.type === "upload-confirmation" && (
                  <button className="submit-button" onClick={handleSubmit}>
                    Submit
                  </button>
                )}
                {msg.type === "pdf-converted" && (
                  <div className="markdown-preview">
                    <span>Converted Markdown: </span>
                    <pre>{msg.text}</pre>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>

        <div className="input-section">
          <button className="ai-button" onClick={activateAI}>
            Activate AI
          </button>
          <input
            type="text"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder={`Message as ${currentUser}...`}
            onKeyPress={(e) => e.key === "Enter" && sendMessage()}
            disabled={isAIActive}
          />
          <button
            className="mic-button"
            onClick={() => {
              /* mic functionality */
            }}
          >
            🎤
          </button>
          <button
            className="attachment-button"
            onClick={() => {
              /* attachment functionality */
            }}
          >
            📎
          </button>
          <button className="send-button" onClick={sendMessage}>
            Send
          </button>
        </div>
      </div>
    </div>
  );
};

export default MainPage;
