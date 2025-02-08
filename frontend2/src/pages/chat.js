import { useState } from 'react';
import { FaMicrophone, FaPaperclip, FaPaperPlane, FaExclamationTriangle } from 'react-icons/fa';

export default function ChatWindow() {
  const [messages, setMessages] = useState([]);
  const [inputText, setInputText] = useState('');
  const [currentUser, setCurrentUser] = useState('A');
  const [isDisputed, setIsDisputed] = useState(false);
  const [waitingForUpload, setWaitingForUpload] = useState(false);

  const handleSend = () => {
    if (!inputText.trim() || isDisputed) return;
    
    const newMessage = {
      text: inputText,
      user: currentUser,
      timestamp: new Date().toISOString()
    };
    
    setMessages([...messages, newMessage]);
    setInputText('');
    setCurrentUser(currentUser === 'A' ? 'B' : 'A');
  };

  const createDispute = async () => {
    setIsDisputed(true);
    const aiMessage = {
      text: "⚠️ Dispute created. Please upload relevant documentation for review.",
      user: 'AI',
      timestamp: new Date().toISOString()
    };
    setMessages([...messages, aiMessage]);
    setWaitingForUpload(true);
  };

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (file && file.type === 'application/pdf') {
      // Simulate API call
      setTimeout(() => {
        const aiResponse = {
          text: "Document received and analyzed. Processing dispute resolution...",
          user: 'AI',
          timestamp: new Date().toISOString()
        };
        setMessages([...messages, aiResponse]);
        setWaitingForUpload(false);
      }, 1500);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 flex flex-col">
      <div className="flex-1 p-4 container mx-auto max-w-4xl">
        <div className="bg-white rounded-lg shadow-lg h-[calc(100vh-2rem)] flex flex-col">
          {/* Chat Header */}
          <div className="p-4 border-b">
            <h1 className="text-xl font-semibold text-gray-800">Dispute Resolution Chat</h1>
          </div>

          {/* Messages Area */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {messages.map((message, index) => (
              <div
                key={index}
                className={`flex ${message.user === 'AI' ? 'justify-center' : 
                  message.user === currentUser ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[70%] p-3 rounded-lg ${
                    message.user === 'AI'
                      ? 'bg-yellow-100 text-center'
                      : message.user === 'A'
                      ? 'bg-blue-500 text-white'
                      : 'bg-gray-200 text-gray-800'
                  }`}
                >
                  {message.text}
                </div>
              </div>
            ))}
          </div>

          {/* Input Area */}
          <div className="p-4 border-t">
            <div className="flex items-center space-x-2">
              <input
                type="text"
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                disabled={isDisputed}
                placeholder={isDisputed ? "Chat disabled during dispute" : "Type your message..."}
                className="flex-1 p-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                onKeyPress={(e) => e.key === 'Enter' && handleSend()}
              />
              
              <button
                onClick={() => document.getElementById('file-upload').click()}
                disabled={!isDisputed || !waitingForUpload}
                className="p-2 text-gray-600 hover:text-gray-800 disabled:opacity-50"
              >
                <FaPaperclip className="w-5 h-5" />
              </button>
              
              <button
                className="p-2 text-gray-600 hover:text-gray-800 disabled:opacity-50"
                disabled={isDisputed}
              >
                <FaMicrophone className="w-5 h-5" />
              </button>
              
              <button
                onClick={handleSend}
                disabled={!inputText.trim() || isDisputed}
                className="p-2 text-blue-600 hover:text-blue-800 disabled:opacity-50"
              >
                <FaPaperPlane className="w-5 h-5" />
              </button>
              
              <button
                onClick={createDispute}
                disabled={isDisputed || messages.length === 0}
                className="px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 disabled:opacity-50 flex items-center"
              >
                <FaExclamationTriangle className="mr-2" />
                Create Dispute
              </button>
            </div>
          </div>
        </div>
      </div>
      <input
        id="file-upload"
        type="file"
        accept=".pdf"
        className="hidden"
        onChange={handleFileUpload}
      />
    </div>
  );
}