import { useState } from 'react'
import './ButtonCard.css'

export default function ButtonCard({ icon: Icon, label, onClick }) {
  const [isPressed, setIsPressed] = useState(false)

  const handleMouseDown = () => setIsPressed(true)
  const handleMouseUp = () => setIsPressed(false)
  const handleTouchStart = () => setIsPressed(true)
  const handleTouchEnd = () => setIsPressed(false)

  const handleClick = () => {
    setIsPressed(false)
    onClick()
  }

  return (
    <button
      className={`button-card ${isPressed ? 'pressed' : ''}`}
      onClick={handleClick}
      onMouseDown={handleMouseDown}
      onMouseUp={handleMouseUp}
      onMouseLeave={handleMouseUp}
      onTouchStart={handleTouchStart}
      onTouchEnd={handleTouchEnd}
    >
      <div className="button-icon">
        <Icon size={24} />
      </div>
      <span className="button-label">{label}</span>
    </button>
  )
}
