import React, { useState, useEffect } from 'react';
import './Alerts.css';

const Alerts = () => {
  const [selectedChat, setSelectedChat] = useState(null);
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Sample data for chat list
  const chatList = [
    {
      id: 1,
      name: 'Chat History 1',
      avatar: 'https://i.pravatar.cc/150?img=1',
    },
    {
      id: 2,
      name: 'Jane Smith',
      avatar: 'https://i.pravatar.cc/150?img=2',
    },
  ];

  // Function to fetch messages from backend
  const fetchMessages = async (chatId) => {
    setLoading(true);
    setError(null);
    try {
      // Replace 'YOUR_BACKEND_API_URL' with your actual API endpoint
      const response = await fetch(`YOUR_BACKEND_API_URL/messages/${chatId}`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      setMessages(data);
    } catch (e) {
      setError(e.message);
      setMessages([]); // clear any old messages
    } finally {
      setLoading(false);
    }
  };

  // Fetch messages when a chat is selected
  useEffect(() => {
    if (selectedChat) {
      fetchMessages(selectedChat.id);
    } else {
      setMessages([]); // Clear messages when no chat is selected
    }
  }, [selectedChat]);

  return (
    <div className="chat-list-container">
      <div className="chat-list">
        <div className="chat-list-header">
          <h2>Chat History</h2>
        </div>
        <div className="search-container">
          <div className="search-box">
            <i className="fas fa-search"></i>
            <input type="text" placeholder="Search or start new chat" />
          </div>
        </div>

        {chatList.map((chat) => (
          <div
            key={chat.id}
            className="chat-item"
            onClick={() => setSelectedChat(chat)}
          >
            <div className="chat-avatar">
              <img src={chat.avatar} alt={chat.name} />
            </div>
            <div className="chat-details">
              <div className="chat-header">
                <h3>{chat.name}</h3>
              </div>
            </div>
          </div>
        ))}
      </div>

      {selectedChat && (
        <div className="chat-message-space">
          <div className="chat-message-header">
            <div className="chat-contact-info">
              <img
                src={selectedChat.avatar}
                alt={selectedChat.name}
                className="contact-avatar"
              />
              <h3>{selectedChat.name}</h3>
            </div>
          </div>
          <div className="chat-message-content">
            {loading && <p>Loading messages...</p>}
            {error && <p>Error: {error}</p>}
            {!loading && !error && messages.length === 0 && <p>No messages yet. Start the conversation!</p>}
            {!loading && !error && messages.map((message) => (
              <div key={message.id} className={`message ${message.type}`}>
                <p>{message.text}</p>
                <span className="message-time">{message.time}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default Alerts;