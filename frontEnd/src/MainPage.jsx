import React, { useState, useRef } from 'react';
import './MainPage.css';
import boyImage from './assets/boy.png';
import girlImage from './assets/girl.png';
import AudioRecording from './AudioRecording';  // Update the path if needed


const MainPage = () => {
  const [message, setMessage] = useState("");
  const [chat, setChat] = useState([]);
  const [currentUser, setCurrentUser] = useState("Buyer"); //start with Buyer
  const [isAIActive, setIsAIActive] = useState(false);
  const [user1PDF, setUser1PDF] = useState(null);
  const [user2PDF, setUser2PDF] = useState(null);
  const [buyerConversation, setBuyerConversation] = useState([]);  // New state for Buyer conversation
  const [sellerConversation, setSellerConversation] = useState([]); // New state for Seller conversation
  const [currentStep, setCurrentStep] = useState('initial');
  const fileInputRef = useRef(null);
  const [audioUrl, setAudioUrl] = useState(null); // Store the audio URL for playback
  const [isRecording, setIsRecording] = useState(false);


  const sendMessage = () => {
    if (message.trim() === "") return;

    const newMessage = { user: currentUser, text: message };
    setChat([...chat, newMessage]);

    // Add the message to the respective conversation packet
    if (currentUser === "Buyer") {
      setBuyerConversation([...buyerConversation, newMessage]);
    } else {
      setSellerConversation([...sellerConversation, newMessage]);
    }

    setMessage("");
  };

  const activateAI = () => {
    setIsAIActive(true);
    setChat([
      ...chat,
      { user: "AI", text: "Hello, since there's a conflict between both of you, I will help resolve it." },
      { user: "AI", text: "Buyer, please upload your PDF document for review.", type: "request-pdf", forUser: "Buyer" }
    ]);
    setCurrentStep('user1Upload');
    
    // Log the conversations when AI is activated
    console.log("Buyer Conversation:", buyerConversation);
    console.log("Seller Conversation:", sellerConversation);
    //sending to main.py, conversation_chain: str = Form(...), 
  };

  const handleFileUpload = (event, user) => {
    const file = event.target.files[0];
    if (file && file.type === 'application/pdf') {
      if (user === 'Buyer') {
        setUser1PDF(file);
        setChat([
          ...chat,
          { user: "Buyer", text: `Uploaded: ${file.name}`, type: "pdf-upload" },
          { user: "AI", text: "Please click Submit to confirm your upload.", type: "upload-confirmation" }
        ]);
      } else {
        setUser2PDF(file);
        setChat([
          ...chat,
          { user: "Seller", text: `Uploaded: ${file.name}`, type: "pdf-upload" },
          { user: "AI", text: "Please click Submit to confirm your upload.", type: "upload-confirmation" }
        ]);
      }
    }
  };

  const handleSubmit = async () => {
    if (currentStep === 'user1Upload' && user1PDF) {
      // Process User 1's PDF
      const formData = new FormData();
      formData.append('file', user1PDF);

      try {
        const response = await fetch('http://localhost:8000/markitdown', {
          method: 'POST',
          body: formData,
        });
        const result = await response.json();
        console.log(result);

        if (response.ok) {
          setChat([
            ...chat,
            { user: "AI", text: "Thank you, Buyer. Now, Seller, please upload your PDF document.", type: "request-pdf", forUser: "Seller" },
            { user: "AI", text: `Buyer’s document converted to Markdown: ${result.markdown}`, type: "pdf-converted" }
          ]);
          setCurrentStep('user2Upload');
        } else {
          throw new Error(result.detail);
        }
      } catch (error) {
        setChat([...chat, { user: "AI", text: "Error processing Buyer’s file." }]);
      }
    } else if (currentStep === 'user2Upload' && user2PDF) {
      // Process Seller's PDF
      const formData = new FormData();
      formData.append('file', user2PDF);

      try {
        const response = await fetch('http://localhost:8000/markitdown', {
          method: 'POST',
          body: formData,
        });
        const result = await response.json();
        console.log(result);

        if (response.ok) {
          setChat([
            ...chat,
            { user: "AI", text: "Thank you both for uploading your documents. I will now review them.", type: "confirmation" },
            { user: "AI", text: `Seller’s document converted to Markdown: ${result.markdown}`, type: "pdf-converted" }
          ]);
          setCurrentStep('complete');
        } else {
          throw new Error(result.detail);
        }
      } catch (error) {
        setChat([...chat, { user: "AI", text: "Error processing Seller’s file." }]);
      }
    }
  };

  const sendAudio = (audioBlob) => {
    const audioUrl = URL.createObjectURL(audioBlob);  // Create a URL from the audio blob
    
    // Create a new message with the audio URL
    const newMessage = { 
      user: currentUser, 
      type: "audio", 
      audioUrl  // Use the audio URL for playback
    };
  
    // Add the new message to the chat
    setChat([...chat, newMessage]);
  };
  

    // If you need to send the audio to a server, you can do it here.
    // const formData = new FormData();
    // formData.append('audio', audioBlob);

    // Example to send the audio to the server
    // fetch('http://localhost:8000/upload-audio', {
    //   method: 'POST',
    //   body: formData,
    // })
    //   .then(response => response.json())
    //   .then(result => {
    //     console.log('Audio uploaded successfully:', result);
    //   })
    //   .catch(error => {
    //     console.error('Error uploading audio:', error);
    //   });

  // Toggle user role manually
  const toggleUserRole = () => {
    setCurrentUser(currentUser === "Buyer" ? "Seller" : "Buyer");
  };

  return (
    <div className="chat-container">
      <div className="chat-wrapper">
        <h1 className="chat-title">Buyer-Seller Chat</h1>

        <div className="chat-messages">
          {chat.map((msg, index) => (
            <div key={index} className={`message-row ${msg.user === "Buyer" ? "" : msg.user === "Seller" ? "reverse" : "ai"}`}>
              <div className="profile-picture">
                <img 
                  src={msg.user === "Buyer" ? boyImage : msg.user === "Seller" ? girlImage : null} 
                  alt={msg.user === "Buyer" ? "Buyer" : msg.user === "Seller" ? "Seller" : "AI"} 
                  className={`profile-circle ${msg.user === "Buyer" ? "buyer" : msg.user === "Seller" ? "seller" : "ai"}`}
                />
              </div>

              <div className={`message-bubble ${msg.user === "Buyer" ? "buyer" : msg.user === "Seller" ? "seller" : "ai"}`}>
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
                {msg.type === "audio" && (
                  <div>
                    <audio controls src={msg.audioUrl} />
                  </div>
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
            onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
            disabled={isAIActive}
          />
             {/* <button className="mic-button">
            🎤
          </button> */}
          <AudioRecording onStopRecording={sendAudio} />

          <button className="attachment-button" onClick={() => { /* attachment functionality */ }}>
            📎
          </button>
          <button className="send-button" onClick={sendMessage}>
            Send
          </button>
          <button className={`role-button ${currentUser === "Buyer" ? "buyer" : "seller"}`} 
            onClick={toggleUserRole}
          >Switch to {currentUser === "Buyer" ? "Seller" : "Buyer"}</button>
        </div>
      </div>
    </div>
  );
};

export default MainPage;
