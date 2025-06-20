import React, { useState } from 'react'
import axios from 'axios'
import { ClipLoader } from 'react-spinners'
import './style.css'
import logo from './images/logo_01.svg'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'

function App () {
  const [input, setInput] = useState('')
  const [open, setOpen] = useState(true)
  const [chat, setChat] = useState([])
  const [loading, setLoading] = useState(false)

  const sendQuestion = async () => {
    if (!input.trim()) return

    const userMsg = { sender: 'User', text: input }
    setChat(prev => [...prev, userMsg])
    setLoading(true)
    setInput('')

    try {
      const { data } = await axios.post('http://127.0.0.1:5000/api/query', {
        question: input,
        open_graph: open
      })

      const botMsg = { sender: 'Bot', text: data.response, isopen: open }
      setChat(prev => [...prev, botMsg])
    } catch (err) {
      console.error(err)
      setChat(prev => [...prev, { sender: 'Bot', text: '出错了，请稍后再试', isopen: open }])
    } finally {
      setLoading(false)
    }

    setInput('')
  }

  const handleKeyPress = e => {
    if (e.key === 'Enter') sendQuestion()
  }

  const isOpenGraph = () => {
    setOpen(prev => !prev)
  }

  return (
    <div className="chat-wrapper">
      <div className="chat-box">
        <div className="chat-header">
          <div className="chat-logo">
            <img src={logo} alt="logo" className="logo" />
          </div>
          <div className="chat-title">
            水稻知识检索系统
          </div>
        </div>

        <div className="chat-window">
          {chat.map((msg, idx) => (
            <div
              key={idx}
              className={`chat-bubble ${msg.sender === 'User' ? 'user' : msg.isopen ? 'bot-graph' : 'bot-model'}`}
            >
              <ReactMarkdown remarkPlugins={[remarkGfm]}>{msg.text}</ReactMarkdown>
            </div>
          ))}

          {loading && (
            <div className="spinner-container">
              <ClipLoader color="#009944" size={32} />
            </div>
          )}
        </div>

        <div className="chat-input-area">
          <div className='chat-model-choose'>
            <button
              className='chat-model-btn'
              onClick={isOpenGraph}
            >
              <div className={`chat-model-status ${open ? 'open' : 'close'}`}></div>
              <div className={`chat-model-text ${open ? 'open' : 'close'}`}>{open ? '关闭知识图谱' : '开启知识图谱'}</div>
            </button>
          </div>
          <div className="chat-input-container">
            <input
              className="chat-input"
              type="text"
              placeholder="请输入问题..."
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={handleKeyPress}
              disabled={loading}
            />
            <button className="chat-send" onClick={sendQuestion} disabled={loading}>
              发送
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default App
