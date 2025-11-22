import { Globe, RotateCw, Camera, MousePointer2, Play, Type, Keyboard } from 'lucide-react'
import { useTelegram } from '../context/TelegramContext'
import ButtonCard from './ButtonCard'
import './CommandPanel.css'

export default function CommandPanel() {
  const { sendCommand } = useTelegram()

  const testCommand = () => {
    console.log('Test button clicked!')
    sendCommand({
      type: 'command',
      action: 'screenshot'
    })
  }

  const commands = [
    {
      icon: Camera,
      label: 'TEST SCREENSHOT',
      action: testCommand
    },
    {
      icon: Globe,
      label: 'Open Google',
      action: () => sendCommand({
        type: 'command',
        action: 'open_url',
        url: 'https://google.com'
      })
    },
    {
      icon: RotateCw,
      label: 'Switch Tab 1',
      action: () => sendCommand({
        type: 'command',
        action: 'switch_tab',
        number: 1
      })
    },
    {
      icon: RotateCw,
      label: 'Switch Tab 2',
      action: () => sendCommand({
        type: 'command',
        action: 'switch_tab',
        number: 2
      })
    },
    {
      icon: Camera,
      label: 'Screenshot',
      action: () => sendCommand({
        type: 'command',
        action: 'screenshot'
      })
    },
    {
      icon: MousePointer2,
      label: 'Click Center',
      action: () => sendCommand({
        type: 'command',
        action: 'click_center'
      })
    },
    {
      icon: Play,
      label: 'Run Program',
      action: () => sendCommand({
        type: 'command',
        action: 'run_program',
        path: 'notepad.exe'
      })
    },
    {
      icon: Type,
      label: 'Write Text',
      action: () => sendCommand({
        type: 'command',
        action: 'write',
        text: 'Hello from Telegram!'
      })
    },
    {
      icon: Keyboard,
      label: 'Custom Hotkey',
      action: () => sendCommand({
        type: 'command',
        action: 'hotkey',
        keys: ['ctrl', 'c']
      })
    }
  ]

  return (
    <section className="command-panel">
      <h2>Quick Commands</h2>
      <div className="command-grid">
        {commands.map((cmd, idx) => (
          <ButtonCard
            key={idx}
            icon={cmd.icon}
            label={cmd.label}
            onClick={cmd.action}
          />
        ))}
      </div>
    </section>
  )
}
