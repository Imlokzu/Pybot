import { createContext, useContext, useCallback } from 'react'

const TelegramContext = createContext()

export const TelegramProvider = ({ children }) => {
  const tg = window.Telegram.WebApp

  const sendCommand = useCallback((payload) => {
    try {
      const jsonData = JSON.stringify(payload)
      console.log('Sending command:', jsonData)
      tg.sendData(jsonData)
    } catch (error) {
      console.error('Error sending command:', error)
    }
  }, [tg])

  const showAlert = useCallback((message) => {
    tg.showAlert(message)
  }, [tg])

  const showConfirm = useCallback((message) => {
    return new Promise((resolve) => {
      tg.showConfirm(message, (ok) => {
        resolve(ok)
      })
    })
  }, [tg])

  const getThemeParams = useCallback(() => {
    return tg.themeParams || {}
  }, [tg])

  const value = {
    tg,
    sendCommand,
    showAlert,
    showConfirm,
    getThemeParams,
  }

  return (
    <TelegramContext.Provider value={value}>
      {children}
    </TelegramContext.Provider>
  )
}

export const useTelegram = () => {
  const context = useContext(TelegramContext)
  if (!context) {
    throw new Error('useTelegram must be used within TelegramProvider')
  }
  return context
}
