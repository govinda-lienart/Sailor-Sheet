import React, { useState } from 'react';
import './App.css';

function App() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([
    { text: "Hello! I'm your AI Sailor Sheet assistant. I'm here to help you with your accounting questions. How can I assist you today?", sender: 'bot' }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  

  const handleSendMessage = () => {
    if (inputMessage.trim() === '') return;

    // Add user message
    const newMessages = [...messages, { text: inputMessage, sender: 'user' }];
    setMessages(newMessages);

    // Simple hardcoded responses
    let botResponse = "I'm still learning! Can you ask me something about accounting?";
    
    if (inputMessage.toLowerCase().includes('hello') || inputMessage.toLowerCase().includes('hi')) {
      botResponse = "Ahoy there! How are you doing today? I'm here to help with your accounting questions!";
    } else if (inputMessage.toLowerCase().includes('help')) {
      botResponse = "I can help you with accounting questions, transaction types, funds, and categories. What would you like to know?";
    } else if (inputMessage.toLowerCase().includes('transaction')) {
      botResponse = "Transactions can be donations, payments, transfers, or grants. Each type has different account requirements. What specific transaction are you working on?";
    } else if (inputMessage.toLowerCase().includes('fund')) {
      botResponse = "We have several funds including Unrestricted Funds, Internal Transfer, Conference Participation Fee, and Frankfurt Zoological Society. Which fund are you interested in?";
    } else if (inputMessage.toLowerCase().includes('account')) {
      botResponse = "We have accounts for both Vietnam (Indovina Bank, Wallets) and Belgium (Belfius). Each transaction needs debit and credit accounts. What type of account are you looking for?";
    }

    // Add bot response
    setTimeout(() => {
      setMessages([...newMessages, { text: botResponse, sender: 'bot' }]);
    }, 500);

    setInputMessage('');
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleSendMessage();
    }
  };

  return (
    <div className="App">
      {/* Robot Icon - Always visible */}
      <div 
        className={`robot-icon ${isOpen ? 'open' : ''}`}
        onClick={() => setIsOpen(!isOpen)}
      >
        <div className="robot">
          <div className="robot-head">
            <div className="robot-eyes">
              <div className="eye left-eye"></div>
              <div className="eye right-eye"></div>
            </div>
            <div className="robot-mouth"></div>
          </div>
          <div className="robot-body">
            <div className="robot-antenna"></div>
          </div>
        </div>
      </div>

      {/* Chat Window - Only visible when open */}
      {isOpen && (
        <div className="chat-window">
          <div className="chat-header">
            <h3>🤖 Sailor Sheet Assistant</h3>
            <button 
              className="close-btn"
              onClick={() => setIsOpen(false)}
            >
              ×
            </button>
          </div>
          
          <div className="chat-messages">
            {messages.map((message, index) => (
              <div key={index} className={`message ${message.sender}`}>
                <div className="message-bubble">
                  {message.text}
                </div>
              </div>
            ))}
          </div>
          
          <div className="chat-input">
            <input
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask me about accounting..."
              className="message-input"
            />
            <button 
              onClick={handleSendMessage}
              className="send-btn"
            >
              Send
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
