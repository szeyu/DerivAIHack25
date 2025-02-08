import React, { createContext, useState, useContext } from 'react';

const ChatContext = createContext();

export const ChatProvider = ({ children }) => {
  const [message, setMessage] = useState("");
  const [chat, setChat] = useState([]);
  const [currentUser, setCurrentUser] = useState("Buyer");
  const [isAIActive, setIsAIActive] = useState(false);
  const [formattedConversation, setFormattedConversation] = useState("");

  return (
    <ChatContext.Provider value={{
      message,
      setMessage,
      chat,
      setChat,
      currentUser,
      setCurrentUser,
      isAIActive,
      setIsAIActive,
      formattedConversation,
      setFormattedConversation
    }}>
      {children}
    </ChatContext.Provider>
  );
};

export const useChat = () => useContext(ChatContext);