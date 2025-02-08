import React, { useState, useRef } from 'react';
import './MainPage.css';
import boyImage from './assets/boy.png';
import girlImage from './assets/girl.png';
import AudioRecording from './AudioRecording';  


const MainPage = () => {
  const [message, setMessage] = useState("");
  const [chat, setChat] = useState([]);
  const [currentUser, setCurrentUser] = useState("Buyer"); //start with Buyer
  const [isAIActive, setIsAIActive] = useState(false);
  const [pdfBuyer, setPdfBuyer] = useState(null); 
  const [pdfSeller, setPdfSeller] = useState(null); 
  const [buyerConversation, setBuyerConversation] = useState([]);  // New state for Buyer conversation
  const [sellerConversation, setSellerConversation] = useState([]); // New state for Seller conversation
  const [currentStep, setCurrentStep] = useState('initial');
  const fileInputRef = useRef(null);
  const [audioUrl, setAudioUrl] = useState(null); // Store the audio URL for playback
  const [isRecording, setIsRecording] = useState(false);
  const [fraudDetected, setFraudDetected] = useState(false);

  const checkFraud = async (text, currentWarningCount = 0) => {
    const payload = { 
        text,
        warning_count: currentWarningCount // Use passed warning count instead of hardcoding
    };
    
    try {
        const response = await fetch('http://localhost:8000/fraud_detection_firewall', { 
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        console.log("Fraud check result:", result);

        // Return both the status and updated warning count
        return {
            status: result.status === 'ALERT' ? 'Fraud Detected' : 'No Fraud',
            warningCount: result.warning_count,
            escalate: result.escalate,
            message: result.message
        };

    } catch (error) {
        console.error("Fraud check error:", error);
        return {
            status: 'Error',
            message: error.message,
            warningCount: currentWarningCount,
            escalate: false
        };
    }
  };
  

  const formatAIText = (text) => {
    // Replace **text** with <strong>text</strong>
    let formattedText = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    
    // Replace \n with <br /> for line breaks
    formattedText = formattedText.replace(/\n/g, '<br />');
  
    return formattedText;
  };

  const sendMessage = async () => {
    if (message.trim() === "") return;
  
    // Check if a fraud issue is already flagged
    if (fraudDetected) {
      // Optionally, you might show a toast or alert here
      return;
    }
  
    // Call the fraud firewall before sending the message
    const fraudResult = await checkFraud(message);
    if (fraudResult.status === "Fraud Detected") {
      setChat([
        ...chat,
        { user: "AI", text: "Warning: Fraud detected. Session terminated." }
      ]);
      // Prevent further input
      setFraudDetected(true);
      return;
    }
  
    // Proceed normally if no fraud is detected
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

  const activateAI = async () => { // Make this async
    setIsAIActive(true);
    
    // Create conversation chain string
    const conversationChain = JSON.stringify([
        ...buyerConversation,
        ...sellerConversation
    ]);

    try {
        // Call conversation analysis endpoint
        const analysisResponse = await fetch('http://localhost:8000/analyze_conversation', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ context: conversationChain }),
        });

        if (!analysisResponse.ok) {
            throw new Error('Analysis failed');
        }

        const analysisResult = await analysisResponse.json();

        let aiMessages = [];
        switch(analysisResult.selected_tool) {
            case 'refundBuyer':
                aiMessages = [
                    { 
                        user: "AI", 
                        text: "Based on our conversation analysis, a refund will be processed for the buyer. The order will be cancelled."
                    }
                ];
                break;

            case 'transactionIssues':
                aiMessages = [
                    { 
                        user: "AI", 
                        text: "Hello, since there's a conflict between both of you, I will help resolve it." 
                    },
                    { 
                        user: "AI", 
                        text: "Buyer, please upload your PDF document for review.", 
                        type: "request-pdf", 
                        forUser: "Buyer" 
                    }
                ];
                setCurrentStep('buyerUpload');
                break;

            case 'neutralIssue':
                aiMessages = [
                    { 
                        user: "AI", 
                        text: "No discernible dispute found. Returning to normal chat mode." 
                    }
                ];
                // Disable AI mode for neutral issues
                setIsAIActive(false);
                break;
                
        }

        setChat(prevChat => [
            ...prevChat,
            ...aiMessages
        ]);

    } catch (error) {
        console.error("AI activation error:", error);
        setChat(prevChat => [
            ...prevChat,
            { 
                user: "AI", 
                text: "Error analyzing conversation. Please try again." 
            }
        ]);
    }
  };

  const handleFileUpload = (event, user) => {
    const file = event.target.files[0];
    if (file && file.type === 'application/pdf') {
      if (user === 'Buyer') {
        setPdfBuyer(file); 
        setChat([
          ...chat,
          { user: "Buyer", text: `Uploaded: ${file.name}`, type: "pdf-upload" },
          { user: "AI", text: "Please click Submit to confirm your upload.", type: "upload-confirmation" }
        ]);
      } else {
        setPdfSeller(file); // Renamed from user2PDF to pdfSeller
        setChat([
          ...chat,
          { user: "Seller", text: `Uploaded: ${file.name}`, type: "pdf-upload" },
          { user: "AI", text: "Please click Submit to confirm your upload.", type: "upload-confirmation" }
        ]);
      }
    }
  };

// In the component's top variables, replace:
// const formData = new FormData();
// With:
const formDataRef = useRef(new FormData());

// Update handleSubmit function:
const handleSubmit = async () => {
  // Check if both PDFs have been submitted.
  if (pdfBuyer && pdfSeller) {
    // Both files are available—proceed to send the data to the server.
    setCurrentStep('sendingDataToServer');
    // Add a chat message indicating that data is being sent (you can display a loading circle in your UI when currentStep is "sendingDataToServer")
    setChat([
      ...chat,
      { 
        user: "AI", 
        text: "Sending data to the server, please wait...", 
        type: "loading" 
      }
    ]);

    // Append both PDFs and conversation chain to the FormData.
    formDataRef.current.append('pdf_file_buyer', pdfBuyer);
    formDataRef.current.append('pdf_file_seller', pdfSeller);
    formDataRef.current.append('conversation_chain', JSON.stringify([...buyerConversation, ...sellerConversation]));

    // Debug: Log FormData entries.
    for (let [key, value] of formDataRef.current.entries()) {
      console.log(key, value);
    }

    try {
      console.log("Sending form data to the server...");
      const response = await fetch('http://localhost:8000/resolve_dispute', {
        method: 'POST',
        body: formDataRef.current,
      });

      if (response.ok) {
        const result = await response.json();
        console.log("Server response:", result);

        // Process the response based on the selected tool.
        if (result.selected_tool === "getBuyerBankStatement") {
          setChat([
            ...chat,
            { 
              user: "AI", 
              text: "Buyer, your bank statement info is insufficient. Please upload your bank statement PDF again.", 
              type: "request-pdf", 
              forUser: "Buyer" 
            }
          ]);
          setCurrentStep('buyerUpload');
        } else if (result.selected_tool === "getSellerBankStatement") {
          setChat([
            ...chat,
            { 
              user: "AI", 
              text: formatAIText(result.resolution), 
              type: "resolution" 
            },
            { 
              user: "AI", 
              text: "Seller, your bank statement info is insufficient. Please upload your bank statement PDF again.", 
              type: "request-pdf", 
              forUser: "Seller" 
            }
          ]);
          setCurrentStep('sellerUpload');
        } else if (result.selected_tool === "notifyAndEscalate") {
          setChat([
            ...chat,
            { 
              user: "AI", 
              text: formatAIText(result.resolution), 
              type: "resolution" 
            },
            { 
              user: "AI", 
              text: "The case is being escalated and a human administrator has been notified." 
            }
          ]);
          setCurrentStep('complete');
        } else if (result.selected_tool === "allGood") {
          setChat([
            ...chat,
            { 
              user: "AI", 
              text: "Both parties are all good and the transaction is completed successfully." 
            }
          ]);
          setCurrentStep('complete');
        } else {
          // Default resolution if no specific tool is selected.
          setChat([
            ...chat,
            { 
              user: "AI", 
              text: "Thank you both for uploading your documents. I will now review them.", 
              type: "confirmation" 
            },
            { 
              user: "AI", 
              text: formatAIText(result.resolution), 
              type: "resolution" 
            }
          ]);
          setCurrentStep('complete');
        }
      } else {
        throw new Error(await response.text());
      }
    } catch (error) {
      console.error("Error processing Seller’s file:", error);
      setChat([...chat, { user: "AI", text: "Error processing Seller’s file." }]);
    }
  } else {
    // If one or both PDFs are missing, prompt the respective party to upload the missing file.
    if (!pdfBuyer) {
      setChat([
        ...chat,
        { 
          user: "AI", 
          text: "Buyer, please upload your PDF document.", 
          type: "request-pdf", 
          forUser: "Buyer" 
        }
      ]);
      setCurrentStep('buyerUpload');
    }
    if (!pdfSeller) {
      setChat([
        ...chat,
        { 
          user: "AI", 
          text: "Seller, please upload your PDF document.", 
          type: "request-pdf", 
          forUser: "Seller" 
        }
      ]);
      setCurrentStep('sellerUpload');
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
  
  // Toggle user role manually
  const toggleUserRole = () => {
    setCurrentUser(currentUser === "Buyer" ? "Seller" : "Buyer");
  };

  return (
    <div className="chat-container">
      <div className="chat-wrapper">
        <h1 className="chat-title">SwiftSettle Chat</h1>

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
                <p dangerouslySetInnerHTML={{ __html: msg.text }}></p>
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
            disabled={isAIActive || fraudDetected}
          />
          <AudioRecording onStopRecording={sendAudio} />

          <button className="attachment-button" onClick={() => { /* attachment functionality */ }}>
            📎
          </button>
          <button className="send-button" onClick={sendMessage} disabled={isAIActive || fraudDetected}>
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
