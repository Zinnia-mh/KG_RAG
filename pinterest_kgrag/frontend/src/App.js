import { useState } from 'react';
import axios from 'axios';
import { ClipLoader } from 'react-spinners';

function App() {
  const [question, setQuestion] = useState('');
  const [chat, setChat] = useState([]);
  const [loading, setLoading] = useState(false);

  const sendQuestion = async () => {
    if (!input.trim()) return;
    const userMsg = { sender: 'User', text: input };
    setChat(prev => [...prev, userMsg]);
    setInput('');
    setLoading(true); // Start loading
  
    try {
      const { data } = await axios.post('http://127.0.0.1:5000/api/query', { question: input });
      const botMsg = { sender: 'Bot', text: data.response };
      setChat(prev => [...prev, botMsg]);
    } catch (err) {
      console.error(err);
      setChat(prev => [...prev, { sender: 'Bot', text: 'Error connecting to server.' }]);
    } finally {
      setLoading(false); // Done loading
    }
  };

  return (
    <div className="app-container">
      <header className="app-header">Pinterest Help Center</header>
      <div className="chat-window">
        {chat.map((msg, i) => (
          <div key={i} className={`message ${msg.sender === 'You' ? 'user' : 'bot'}`}>
            <strong>{msg.sender}:</strong> {msg.text}
          </div>
        ))}
        {loading && (
          <div style={{ display: 'flex', justifyContent: 'center', marginTop: '1rem' }}>
            <ClipLoader color="#E60023" size={40} />
          </div>
        )}
      </div>
      <div className="input-area">
        <input
          type="text"
          value={question}
          onChange={e => setQuestion(e.target.value)}
          placeholder="Ask me anything…"
          onKeyDown={e => e.key === 'Enter' && sendQuestion()}
          disabled={loading}
        />
        <button onClick={sendQuestion}>Send</button>
      </div>
    </div>
  );
}

export default App;