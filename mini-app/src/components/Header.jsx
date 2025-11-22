import { Monitor } from 'lucide-react'
import './Header.css'

export default function Header() {
  return (
    <header className="header">
      <div className="header-content">
        <div className="header-icon">
          <Monitor size={24} />
        </div>
        <div className="header-text">
          <h1>PC Remote Control</h1>
          <p>Control your computer from Telegram</p>
        </div>
      </div>
    </header>
  )
}
