import { useEffect, useState } from 'react'
import './App.css'
import Header from './components/Header'
import CommandPanel from './components/CommandPanel'
import AICommandInput from './components/AICommandInput'
import QuickActions from './components/QuickActions'
import ScreenshotViewer from './components/ScreenshotViewer'
import { TelegramProvider } from './context/TelegramContext'

function App() {
  const [isDarkMode, setIsDarkMode] = useState(true)

  useEffect(() => {
    // Initialize Telegram WebApp
    const tg = window.Telegram.WebApp
    
    // Check if running in Telegram
    if (!tg) {
      console.error('Telegram WebApp not found!')
      return
    }
    
    console.log('Telegram WebApp initialized:', tg)
    
    tg.ready()
    tg.expand()

    // Set theme based on Telegram
    if (tg.themeParams) {
      const isDark = tg.colorScheme === 'dark'
      setIsDarkMode(isDark)
    }

    // Listen for theme changes
    const handleThemeChange = () => {
      if (tg.colorScheme === 'dark') {
        setIsDarkMode(true)
      } else {
        setIsDarkMode(false)
      }
    }

    tg.onEvent('themeChanged', handleThemeChange)

    return () => {
      tg.offEvent('themeChanged', handleThemeChange)
    }
  }, [])

  return (
    <TelegramProvider>
      <div className={`app ${isDarkMode ? 'dark' : 'light'}`}>
        <Header />
        <div className="app-content">
          <ScreenshotViewer />
          <CommandPanel />
          <QuickActions />
          <AICommandInput />
        </div>
      </div>
    </TelegramProvider>
  )
}

export default App
