import { useState, useEffect } from 'react'
import { Image } from 'lucide-react'
import './ScreenshotViewer.css'

export default function ScreenshotViewer() {
  const [screenshot, setScreenshot] = useState(null)
  const [isLoading, setIsLoading] = useState(false)

  useEffect(() => {
    // Listen for messages from the bot
    const handleMessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        if (data.type === 'screenshot' && data.url) {
          setScreenshot(data.url)
          setIsLoading(false)
        }
      } catch (error) {
        console.error('Error parsing message:', error)
      }
    }

    window.addEventListener('message', handleMessage)
    return () => window.removeEventListener('message', handleMessage)
  }, [])

  if (!screenshot) {
    return (
      <div className="screenshot-viewer empty">
        <div className="screenshot-placeholder">
          <Image size={48} />
          <p>Screenshot will appear here</p>
          <span>Click "Screenshot" button to capture</span>
        </div>
      </div>
    )
  }

  return (
    <div className="screenshot-viewer">
      <div className="screenshot-header">
        <h3>Latest Screenshot</h3>
      </div>
      <div className="screenshot-container">
        <img src={screenshot} alt="PC Screenshot" />
      </div>
    </div>
  )
}
