import React, { useState, useRef } from 'react';
import './MainPage.css';
import boyImage from './assets/boy.png';
import girlImage from './assets/girl.png';

const MainPage = () => {
  const [message, setMessage] = useState("");
  const [chat, setChat] = useState([]);
  const [currentUser, setCurrentUser] = useState("User 1");
  const [isAIActive, setIsAIActive] = useState(false);
  const [user1PDF, setUser1PDF] = useState(null);
  const [user2PDF, setUser2PDF] = useState(null);
  const [currentStep, setCurrentStep] = useState('initial'); // initial, user1Upload, user2Upload
  const fileInputRef = useRef(null);

  const sendMessage = () => {
    if (message.trim() === "") return;
    setChat([...chat, { user: currentUser, text: message }]);
    setMessage("");
    setCurrentUser(currentUser === "User 1" ? "User 2" : "User 1");
  };

  const activateAI = () => {
    setIsAIActive(true);
    setChat([...chat, { 
      user: "AI", 
      text: "Hello, since there's is a conflict between both of you. Let me help you to solve this problem" 
    }, {
      user: "AI",
      text: "User 1, please upload your PDF document for review.",
      type: "request-pdf",
      forUser: "User 1"
    }]);
    setCurrentStep('user1Upload');
  };

  const handleFileUpload = (event, user) => {
    const file = event.target.files[0];
    if (file && file.type === 'application/pdf') {
      if (user === 'User 1') {
        setUser1PDF(file);
        setChat([...chat, {
          user: "User 1",
          text: `Uploaded: ${file.name}`,
          type: "pdf-upload"
        }, {
          user: "AI",
          text: "Please click Submit to confirm your upload.",
          type: "upload-confirmation"
        }]);
      } else {
        setUser2PDF(file);
        setChat([...chat, {
          user: "User 2",
          text: `Uploaded: ${file.name}`,
          type: "pdf-upload"
        }, {
          user: "AI",
          text: "Please click Submit to confirm your upload.",
          type: "upload-confirmation"
        }]);
      }
    }
  };

  const handleSubmit = () => {
    if (currentStep === 'user1Upload' && user1PDF) {
      setChat([...chat, {
        user: "AI",
        text: "Thank you User 1. Now, User 2, please upload your PDF document.",
        type: "request-pdf",
        forUser: "User 2"
      }]);
      setCurrentStep('user2Upload');
    } else if (currentStep === 'user2Upload' && user2PDF) {
      setChat([...chat, {
        user: "AI",
        text: "Thank you both for uploading your documents. I will now review them.",
        type: "confirmation"
      }]);
      setCurrentStep('complete');
    }
  };

  const handleMicClick = () => {
    // console.log("Mic clicked");
  };

  const handleAttachmentClick = () => {
    // console.log("Attachment clicked");
  };

  return (
    <div className="chat-container">
      <div className="chat-wrapper">
        <h1 className="chat-title">Two-Person Chat</h1>
        
        <div className="chat-messages">
          {chat.map((msg, index) => (
            <div key={index} className={`message-row ${msg.user === "User 1" ? "" : msg.user === "User 2" ? "reverse" : "ai"}`}>
              <div className="profile-picture">
                <img 
                  src={msg.user === "User 1" ? boyImage : msg.user === "User 2" ? girlImage : ""} 
                  alt={msg.user === "User 1" ? "User 1" : msg.user === "User 2" ? "User 2" : "AI"} 
                  className={`profile-circle ${msg.user === "User 1" ? "user1" : msg.user === "User 2" ? "user2" : "ai"}`}
                />
              </div>
              
              <div className={`message-bubble ${msg.user === "User 1" ? "user1" : msg.user === "User 2" ? "user2" : "ai"}`}>
                <p>{msg.text}</p>
                {msg.type === "request-pdf" && (
                  <div className="pdf-upload-section">
                    <input
                      type="file"
                      accept=".pdf"
                      onChange={(e) => handleFileUpload(e, msg.forUser)}
                      style={{ display: 'none' }}
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
                  <button 
                    className="submit-button"
                    onClick={handleSubmit}
                  >
                    Submit
                  </button>
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
            onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
            disabled={isAIActive}
          />
          <button className="mic-button" onClick={handleMicClick}>
            🎤
          </button>
          <button className="attachment-button" onClick={handleAttachmentClick}>
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