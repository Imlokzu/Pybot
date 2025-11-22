import { useState } from 'react'
import { Send } from 'lucide-react'
import { useTelegram } from '../context/TelegramContext'
import './AICommandInput.css'

export default function AICommandInput() {
  const [input, setInput] = useState('')
  const [isSending, setIsSending] = useState(false)
  const { sendCommand, showAlert } = useTelegram()

  const handleSend = async () => {
    if (!input.trim()) {
      showAlert('Please enter a command')
      return
    }

    setIsSending(true)
    try {
      sendCommand({
        type: 'ai_raw',
        text: input.trim()
      })
      setInput('')
      showAlert('Command sent!')
    } catch (error) {
      showAlert('Error sending command')
    } finally {
      setIsSending(false)
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <section className="ai-command-input">
      <h2>AI Command</h2>
      <div className="input-wrapper">
        <textarea
          className="command-input"
          placeholder="Type your command... (e.g., 'open firefox and go to youtube')"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
          rows={3}
        />
        <button
          className={`send-button ${isSending ? 'sending' : ''}`}
          onClick={handleSend}
          disabled={isSending || !input.trim()}
        >
          <Send size={20} />
        </button>
      </div>
      <p className="input-hint">
        💡 Describe what you want to do in natural language. The AI will interpret and execute it.
      </p>
    </section>
  )
}
