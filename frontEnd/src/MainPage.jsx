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
    console.log("Fetching test data from API");

    try {
      const response = await fetch('http://localhost:8000/api/test-dispute-data');
      if (!response.ok) {
        throw new Error('Failed to fetch test data');
      }

      const testData = await response.json();
      console.log("Received test data:", testData);
      
      // Store the data in localStorage for Admin.jsx
      localStorage.setItem("disputeData", JSON.stringify(testData));

      // Add AI response to chat
      setChat([
        ...chat,
        {
          user: "AI",
          text: "Analysis complete. Check admin panel for details.",
        },
      ]);

    } catch (error) {
      console.error("Error fetching test data:", error);
      setChat([
        ...chat,
        {
          user: "AI",
          text: "Error analyzing dispute. Please try again.",
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
