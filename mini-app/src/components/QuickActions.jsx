import { ChevronRight, ArrowUp, ArrowDown, ArrowLeft, ArrowRight, Copy, Clipboard } from 'lucide-react'
import { useTelegram } from '../context/TelegramContext'
import './QuickActions.css'

export default function QuickActions() {
  const { sendCommand } = useTelegram()

  const actions = [
    {
      category: 'Browser',
      items: [
        { label: 'Back', action: () => sendCommand({ type: 'command', action: 'hotkey', keys: ['alt', 'left'] }) },
        { label: 'Forward', action: () => sendCommand({ type: 'command', action: 'hotkey', keys: ['alt', 'right'] }) },
        { label: 'Refresh', action: () => sendCommand({ type: 'command', action: 'hotkey', keys: ['f5'] }) },
      ]
    },
    {
      category: 'Mouse',
      items: [
        { label: '↑ Up', action: () => sendCommand({ type: 'command', action: 'move_mouse', x: 0, y: -50 }) },
        { label: '↓ Down', action: () => sendCommand({ type: 'command', action: 'move_mouse', x: 0, y: 50 }) },
        { label: '← Left', action: () => sendCommand({ type: 'command', action: 'move_mouse', x: -50, y: 0 }) },
        { label: '→ Right', action: () => sendCommand({ type: 'command', action: 'move_mouse', x: 50, y: 0 }) },
      ]
    },
    {
      category: 'Keyboard',
      items: [
        { label: 'Copy (Ctrl+C)', action: () => sendCommand({ type: 'command', action: 'hotkey', keys: ['ctrl', 'c'] }) },
        { label: 'Paste (Ctrl+V)', action: () => sendCommand({ type: 'command', action: 'hotkey', keys: ['ctrl', 'v'] }) },
        { label: 'Undo (Ctrl+Z)', action: () => sendCommand({ type: 'command', action: 'hotkey', keys: ['ctrl', 'z'] }) },
        { label: 'Redo (Ctrl+Y)', action: () => sendCommand({ type: 'command', action: 'hotkey', keys: ['ctrl', 'y'] }) },
      ]
    }
  ]

  return (
    <section className="quick-actions">
      <h2>Quick Actions</h2>
      <div className="actions-container">
        {actions.map((group, idx) => (
          <div key={idx} className="action-group">
            <h3>{group.category}</h3>
            <div className="action-buttons">
              {group.items.map((item, itemIdx) => (
                <button
                  key={itemIdx}
                  className="action-button"
                  onClick={item.action}
                >
                  {item.label}
                  <ChevronRight size={16} />
                </button>
              ))}
            </div>
          </div>
        ))}
      </div>
    </section>
  )
}
