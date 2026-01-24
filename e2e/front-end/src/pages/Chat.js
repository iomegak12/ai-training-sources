import React, { useState, useEffect, useRef } from 'react';
import apiService from '../services/api';
import '../styles/Chat.css';

function Chat() {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [isBackendHealthy, setIsBackendHealthy] = useState(null);
  const messagesEndRef = useRef(null);

  // Check backend health on mount
  useEffect(() => {
    checkBackendHealth();
  }, []);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const checkBackendHealth = async () => {
    const healthy = await apiService.healthCheck();
    setIsBackendHealthy(healthy);
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!inputValue.trim() || isLoading) {
      return;
    }

    const userMessage = inputValue.trim();
    setInputValue('');
    setError(null);

    // Add user message to chat
    const userMsg = {
      id: Date.now(),
      text: userMessage,
      sender: 'user',
      timestamp: new Date()
    };
    setMessages(prev => [...prev, userMsg]);

    // Start loading
    setIsLoading(true);

    try {
      // Call API
      const answer = await apiService.query(userMessage);

      // Add AI response to chat
      const aiMsg = {
        id: Date.now() + 1,
        text: answer,
        sender: 'ai',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, aiMsg]);
    } catch (err) {
      setError(err.message);
      
      // Add error message to chat
      const errorMsg = {
        id: Date.now() + 1,
        text: `Sorry, I encountered an error: ${err.message}`,
        sender: 'error',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMsg]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleInputChange = (e) => {
    setInputValue(e.target.value);
  };

  const handleClearChat = () => {
    if (window.confirm('Are you sure you want to clear the chat history?')) {
      setMessages([]);
      setError(null);
    }
  };

  return (
    <div className="chat-page">
      <div className="chat-container">
        <div className="chat-header">
          <div className="chat-header-content">
            <h1>Chat with Agent Query</h1>
            <p>Ask me anything! I can search Wikipedia, Google, Arxiv, and more.</p>
          </div>
          <div className="chat-header-actions">
            {isBackendHealthy === false && (
              <div className="backend-status error">
                ⚠️ Backend offline
              </div>
            )}
            {isBackendHealthy === true && (
              <div className="backend-status healthy">
                ✓ Connected
              </div>
            )}
            {messages.length > 0 && (
              <button onClick={handleClearChat} className="clear-chat-btn">
                Clear Chat
              </button>
            )}
          </div>
        </div>

        <div className="chat-messages">
          {messages.length === 0 ? (
            <div className="message-placeholder">
              <div className="placeholder-icon">💬</div>
              <p>Start a conversation by typing a message below</p>
              <div className="example-queries">
                <p className="example-title">Try asking:</p>
                <button 
                  className="example-query"
                  onClick={() => setInputValue("What is LangSmith?")}
                >
                  "What is LangSmith?"
                </button>
                <button 
                  className="example-query"
                  onClick={() => setInputValue("Tell me about machine learning")}
                >
                  "Tell me about machine learning"
                </button>
                <button 
                  className="example-query"
                  onClick={() => setInputValue("What is quantum computing?")}
                >
                  "What is quantum computing?"
                </button>
              </div>
            </div>
          ) : (
            <>
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={`message ${message.sender}`}
                >
                  <div className="message-avatar">
                    {message.sender === 'user' ? '👤' : message.sender === 'error' ? '⚠️' : '🤖'}
                  </div>
                  <div className="message-content">
                    <div className="message-text">{message.text}</div>
                    <div className="message-timestamp">
                      {message.timestamp.toLocaleTimeString()}
                    </div>
                  </div>
                </div>
              ))}
              {isLoading && (
                <div className="message ai loading">
                  <div className="message-avatar">🤖</div>
                  <div className="message-content">
                    <div className="message-text">
                      <div className="typing-indicator">
                        <span></span>
                        <span></span>
                        <span></span>
                      </div>
                    </div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </>
          )}
        </div>

        <div className="chat-input-container">
          <form className="chat-input-form" onSubmit={handleSubmit}>
            <input
              type="text"
              className="chat-input"
              placeholder="Type your question here..."
              value={inputValue}
              onChange={handleInputChange}
              disabled={isLoading}
            />
            <button 
              type="submit" 
              className="chat-send-btn"
              disabled={isLoading || !inputValue.trim()}
            >
              {isLoading ? 'Sending...' : 'Send'}
            </button>
          </form>
          <p className="chat-hint">
            Press Enter to send • {messages.length} message{messages.length !== 1 ? 's' : ''} in conversation
          </p>
        </div>
      </div>
    </div>
  );
}

export default Chat;
