import React, { useState } from 'react';
import axios from 'axios';
import { ClipLoader } from 'react-spinners';
import './style.css';

function App() {
  const [input, setInput] = useState('');
  const [chat, setChat] = useState([]);
  const [loading, setLoading] = useState(false);

  const sendQuestion = async () => {
    if (!input.trim()) return;

    const userMsg = { sender: 'User', text: input };
    setChat(prev => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      const { data } = await axios.post('http://127.0.0.1:5000/api/query', {
        question: input,
      });

      const botMsg = { sender: 'Bot', text: data.response };
      setChat(prev => [...prev, botMsg]);
    } catch (err) {
      console.error(err);
      setChat(prev => [...prev, { sender: 'Bot', text: 'Oops, error connecting to server.' }]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = e => {
    if (e.key === 'Enter') sendQuestion();
  };

  return (
    <div className="chat-wrapper">
      <div className="chat-box">
        <div className="chat-header">Pinterest Support Chat</div>

        <div className="chat-window">
          {chat.map((msg, idx) => (
            <div
              key={idx}
              className={`chat-bubble ${msg.sender === 'User' ? 'user' : 'bot'}`}
            >
              {msg.text}
            </div>
          ))}

          {loading && (
            <div className="spinner-container">
              <ClipLoader color="#E60023" size={32} />
            </div>
          )}
        </div>

        <div className="chat-input-area">
          <input
            className="chat-input"
            type="text"
            placeholder="Ask me anything..."
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={handleKeyPress}
            disabled={loading}
          />
          <button className="chat-send" onClick={sendQuestion} disabled={loading}>
            Send
          </button>
        </div>
      </div>
    </div>
  );
}

export default App;
