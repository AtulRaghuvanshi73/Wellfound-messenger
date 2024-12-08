import { useState } from 'react'
import axios from 'axios'
import './App.css'

function App() {
  const [message_url, setMessage_url] = useState('')
  const [message, setMessage] = useState('')
  const [status, setStatus] = useState({ type: '', message: '' })

  const transferCookies = async () => {
    try {
      // Get all cookies from the current domain
      const cookies = document.cookie.split(';').map(cookie => {
        const [name, value] = cookie.trim().split('=')
        return {
          name,
          value,
          domain: '.wellfound.com',
          path: '/'
        }
      })

      // Send cookies to backend
      const response = await axios.post('http://localhost:5000/set-cookies', {
        cookies
      })

      setStatus({ type: 'success', message: 'Browser session transferred successfully!' })
    } catch (error) {
      console.error('Error transferring cookies:', error)
      setStatus({
        type: 'error',
        message: 'Failed to transfer browser session. Please try again.'
      })
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setStatus({ type: 'info', message: 'Sending message...' })

    try {
      const formData = new FormData()
      formData.append('message_url', message_url)
      formData.append('message', message)

      const response = await axios.post('http://localhost:5000/send', formData, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        }
      })

      setStatus({ type: 'success', message: 'Message sent successfully!' })
      setMessage_url('')
      setMessage('')
    } catch (error) {
      console.error('Error:', error)
      const errorMessage = error.response?.data?.error || 'Failed to send message. Please try again.'
      
      // Handle different error types
      if (error.response?.status === 401) {
        setStatus({
          type: 'error',
          message: 'Authentication failed. Please check your browser cookies and try again.'
        })
      } else if (error.response?.status === 500) {
        setStatus({
          type: 'error',
          message: `Server error: ${errorMessage}. Check the console for more details.`
        })
      } else {
        setStatus({
          type: 'error',
          message: errorMessage
        })
      }
    }
  }

  return (
    <div className="container">
      <h1>Wellfound Messenger</h1>
      
      {status.message && (
        <div className={`alert alert-${status.type === 'error' ? 'danger' : 
          status.type === 'success' ? 'success' : 'info'}`}>
          {status.message}
        </div>
      )}

      <form onSubmit={handleSubmit} className="message-form">
        <div className="form-group">
          <label htmlFor="message_url">Message URL</label>
          <input
            type="url"
            id="message_url"
            className="form-control"
            value={message_url}
            onChange={(e) => setMessage_url(e.target.value)}
            placeholder="https://wellfound.com/u/username"
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="message">Message</label>
          <textarea
            id="message"
            className="form-control"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            rows="5"
            placeholder="Enter your message here..."
            required
          />
        </div>

        <button type="submit" className="btn btn-primary">
          Send Message
        </button>
        <button type="button" className="btn btn-secondary" onClick={transferCookies}>
          Transfer Browser Session
        </button>
      </form>
    </div>
  )
}

export default App
