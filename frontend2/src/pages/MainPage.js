import React, { useState, useRef } from "react";
import Image from "next/image"; // Add Next.js Image component
// Import CSS module instead of direct CSS
import styles from "../styles/MainPage.module.css";
// Update image imports to use public directory
import boyImage from "../../assets/boy.png";
import girlImage from "../../assets/girl.png";

const MainPage = () => {
  const [message, setMessage] = useState("");
  const [chat, setChat] = useState([]);
  const [currentUser, setCurrentUser] = useState("User 1");
  const [isAIActive, setIsAIActive] = useState(false);
  const [user1PDF, setUser1PDF] = useState(null);
  const [user2PDF, setUser2PDF] = useState(null);
  const [currentStep, setCurrentStep] = useState("initial"); // initial, user1Upload, user2Upload, complete
  const fileInputRef = useRef(null);

  const sendMessage = () => {
    if (message.trim() === "") return;
    setChat([...chat, { user: currentUser, text: message }]);
    setMessage("");
    setCurrentUser(currentUser === "User 1" ? "User 2" : "User 1");
  };

  const activateAI = () => {
    setIsAIActive(true);
    setChat([
      ...chat,
      {
        user: "AI",
        text: "Hello, since there's a conflict between both of you, I will help resolve it.",
      },
      {
        user: "AI",
        text: "User 1, please upload your PDF document for review.",
        type: "request-pdf",
        forUser: "User 1",
      },
    ]);
    setCurrentStep("user1Upload");
  };

  const handleFileUpload = (event, user) => {
    const file = event.target.files[0];
    if (file && file.type === "application/pdf") {
      if (user === "User 1") {
        setUser1PDF(file);
        setChat([
          ...chat,
          {
            user: "User 1",
            text: `Uploaded: ${file.name}`,
            type: "pdf-upload",
          },
          {
            user: "AI",
            text: "Please click Submit to confirm your upload.",
            type: "upload-confirmation",
          },
        ]);
      } else {
        setUser2PDF(file);
        setChat([
          ...chat,
          {
            user: "User 2",
            text: `Uploaded: ${file.name}`,
            type: "pdf-upload",
          },
          {
            user: "AI",
            text: "Please click Submit to confirm your upload.",
            type: "upload-confirmation",
          },
        ]);
      }
    }
  };

  const handleSubmit = async () => {
    if (currentStep === "user1Upload" && user1PDF) {
      // Process User 1's PDF
      const formData = new FormData();
      formData.append("file", user1PDF);

      try {
        const response = await fetch("http://localhost:8000/markitdown", {
          method: "POST",
          body: formData,
        });
        const result = await response.json();
        console.log(result);

        if (response.ok) {
          setChat([
            ...chat,
            {
              user: "AI",
              text: "Thank you, User 1. Now, User 2, please upload your PDF document.",
              type: "request-pdf",
              forUser: "User 2",
            },
            {
              user: "AI",
              text: `User 1's document converted to Markdown: ${result.markdown}`,
              type: "pdf-converted",
            },
          ]);
          setCurrentStep("user2Upload");
        } else {
          throw new Error(result.detail);
        }
      } catch (error) {
        setChat([
          ...chat,
          { user: "AI", text: "Error processing User 1's file." },
        ]);
      }
    } else if (currentStep === "user2Upload" && user2PDF) {
      // Process User 2's PDF
      const formData = new FormData();
      formData.append("file", user2PDF);

      try {
        const response = await fetch("http://localhost:8000/markitdown", {
          method: "POST",
          body: formData,
        });
        const result = await response.json();
        console.log(result);

        if (response.ok) {
          setChat([
            ...chat,
            {
              user: "AI",
              text: "Thank you both for uploading your documents. I will now review them.",
              type: "confirmation",
            },
            {
              user: "AI",
              text: `User 2's document converted to Markdown: ${result.markdown}`,
              type: "pdf-converted",
            },
          ]);
          setCurrentStep("complete");
        } else {
          throw new Error(result.detail);
        }
      } catch (error) {
        setChat([
          ...chat,
          { user: "AI", text: "Error processing User 2's file." },
        ]);
      }
    }
  };

  return (
    <div className={styles["chat-container"]}>
      <div className={styles["chat-wrapper"]}>
        <h1 className={styles["chat-title"]}>Two-Person Chat</h1>

        <div className={styles["chat-messages"]}>
          {chat.map((msg, index) => (
            <div
              key={index}
              className={`${styles["message-row"]} ${
                msg.user === "User 1"
                  ? ""
                  : msg.user === "User 2"
                  ? styles.reverse
                  : styles.ai
              }`}
            >
              <div className={styles["profile-picture"]}>
                <Image
                  src={
                    msg.user === "User 1"
                      ? boyImage
                      : msg.user === "User 2"
                      ? girlImage
                      : null
                  }
                  alt={
                    msg.user === "User 1"
                      ? "User 1"
                      : msg.user === "User 2"
                      ? "User 2"
                      : "AI"
                  }
                  className={`${styles["profile-circle"]} ${
                    msg.user === "User 1"
                      ? styles.user1
                      : msg.user === "User 2"
                      ? styles.user2
                      : styles.ai
                  }`}
                  width={40}
                  height={40}
                />
              </div>

              <div
                className={`${styles["message-bubble"]} ${
                  msg.user === "User 1"
                    ? styles.user1
                    : msg.user === "User 2"
                    ? styles.user2
                    : styles.ai
                }`}
              >
                <p>{msg.text}</p>
                {msg.type === "request-pdf" && (
                  <div className={styles["pdf-upload-section"]}>
                    <input
                      type="file"
                      accept=".pdf"
                      onChange={(e) => handleFileUpload(e, msg.forUser)}
                      style={{ display: "none" }}
                      ref={fileInputRef}
                    />
                    <button
                      className={styles["upload-button"]}
                      onClick={() => fileInputRef.current.click()}
                    >
                      Upload PDF
                    </button>
                  </div>
                )}
                {msg.type === "pdf-upload" && (
                  <div className={styles["pdf-preview"]}>
                    <span>📄 {msg.text}</span>
                  </div>
                )}
                {msg.type === "upload-confirmation" && (
                  <button
                    className={styles["submit-button"]}
                    onClick={handleSubmit}
                  >
                    Submit
                  </button>
                )}
                {msg.type === "pdf-converted" && (
                  <div className={styles["markdown-preview"]}>
                    <span>Converted Markdown: </span>
                    <pre>{msg.text}</pre>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>

        <div className={styles["input-section"]}>
          <button className={styles["ai-button"]} onClick={activateAI}>
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
            className={styles["mic-button"]}
            onClick={() => {
              /* mic functionality */
            }}
          >
            🎤
          </button>
          <button
            className={styles["attachment-button"]}
            onClick={() => {
              /* attachment functionality */
            }}
          >
            📎
          </button>
          <button className={styles["send-button"]} onClick={sendMessage}>
            Send
          </button>
        </div>
      </div>
    </div>
  );
};

export default MainPage;
