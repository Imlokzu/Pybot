# Architecture & Data Flow

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      TELEGRAM USER                              │
│                   (Mobile/Desktop)                              │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ Opens Mini App
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│                   TELEGRAM MINI APP                             │
│                  (React + Vite)                                 │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Header                                                   │  │
│  │ "PC Remote Control"                                      │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Screenshot Viewer                                        │  │
│  │ [Display PC screenshot]                                  │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Command Panel (8 buttons)                                │  │
│  │ [Open Google] [Switch Tab] [Screenshot] [Click Center]  │  │
│  │ [Run Program] [Write Text] [Hotkey] [...]               │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Quick Actions                                            │  │
│  │ [Browser] [Mouse] [Keyboard] shortcuts                  │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ AI Command Input                                         │  │
│  │ [Text input] [Send button]                              │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  TelegramContext (API Wrapper)                                 │
│  - sendCommand()                                               │
│  - showAlert()                                                 │
│  - getThemeParams()                                            │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ tg.sendData(JSON)
                         │ {type: "command", action: "..."}
                         │ {type: "ai_raw", text: "..."}
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│                    TELEGRAM BOT API                             │
│                  (Receives web_app_data)                        │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ Parse JSON
                         │ Extract command/action
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│                   YOUR TELEGRAM BOT                             │
│                  (Python + aiogram)                             │
│                                                                 │
│  @dp.message()                                                 │
│  async def handle_web_app_data(message):                       │
│      data = json.loads(message.web_app_data.data)              │
│      if data['type'] == 'command':                             │
│          action = data['action']                               │
│          # Route to handler                                    │
│      elif data['type'] == 'ai_raw':                            │
│          text = data['text']                                   │
│          # Send to AI interpreter                              │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ Execute command
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│                   PC AGENT/EXECUTOR                             │
│                                                                 │
│  - ScreenCapture()                                             │
│  - ClickController()                                           │
│  - KeyboardController()                                        │
│  - WindowController()                                          │
│  - TaskInterpreter()                                           │
│                                                                 │
│  Performs actual actions on PC:                                │
│  - Takes screenshots                                           │
│  - Clicks mouse                                                │
│  - Types text                                                  │
│  - Presses hotkeys                                             │
│  - Opens programs                                              │
│  - Switches windows                                            │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ Send result back
                         │ (screenshot, status, etc.)
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│                   TELEGRAM BOT                                  │
│                                                                 │
│  await message.answer_photo(screenshot)                        │
│  await message.answer("✅ Command executed")                   │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ Send to user
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│                   TELEGRAM MINI APP                             │
│                                                                 │
│  Display result:                                               │
│  - Show screenshot                                             │
│  - Show status message                                         │
│  - Update UI                                                   │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ Display to user
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│                      TELEGRAM USER                              │
│                   (Sees result)                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Component Hierarchy

```
App
├── Header
│   └── Monitor Icon
├── ScreenshotViewer
│   └── Image Display
├── CommandPanel
│   └── ButtonCard (×8)
│       ├── Icon
│       └── Label
├── QuickActions
│   ├── ActionGroup (Browser)
│   │   └── ActionButton (×3)
│   ├── ActionGroup (Mouse)
│   │   └── ActionButton (×4)
│   └── ActionGroup (Keyboard)
│       └── ActionButton (×4)
└── AICommandInput
    ├── Textarea
    └── SendButton
```

---

## Data Flow - Command Example

### Example 1: Screenshot Command

```
User clicks "Screenshot" button
    ↓
ButtonCard onClick handler triggered
    ↓
sendCommand({
  type: "command",
  action: "screenshot"
})
    ↓
TelegramContext.sendCommand()
    ↓
tg.sendData(JSON.stringify({...}))
    ↓
Telegram API sends to bot as web_app_data
    ↓
Bot receives message.web_app_data
    ↓
Parse JSON: action = "screenshot"
    ↓
ScreenCapture().capture()
    ↓
Save screenshot to file
    ↓
Send to user: message.answer_photo(screenshot)
    ↓
User sees screenshot in Mini App
```

### Example 2: AI Command

```
User types: "open firefox and go to youtube"
    ↓
Click Send button
    ↓
sendCommand({
  type: "ai_raw",
  text: "open firefox and go to youtube"
})
    ↓
tg.sendData(JSON.stringify({...}))
    ↓
Bot receives web_app_data
    ↓
Parse JSON: type = "ai_raw", text = "..."
    ↓
TaskInterpreter.interpret(text)
    ↓
Generate task: {action: "open_app", target: "firefox"}
                {action: "open_url", url: "youtube.com"}
    ↓
Executor.execute(task)
    ↓
Execute on PC
    ↓
Send result: "✅ Firefox opened and navigated to YouTube"
    ↓
User sees confirmation
```

---

## State Management

### App State
```javascript
// App.jsx
const [isDarkMode, setIsDarkMode] = useState(true)
// Tracks theme preference
```

### Component State
```javascript
// AICommandInput.jsx
const [input, setInput] = useState('')
const [isSending, setIsSending] = useState(false)

// ButtonCard.jsx
const [isPressed, setIsPressed] = useState(false)

// ScreenshotViewer.jsx
const [screenshot, setScreenshot] = useState(null)
const [isLoading, setIsLoading] = useState(false)
```

### Context State
```javascript
// TelegramContext.jsx
const tg = window.Telegram.WebApp
// Global Telegram API access
```

---

## Event Flow

### User Interaction
```
User Input
    ↓
Event Handler (onClick, onChange, etc.)
    ↓
State Update
    ↓
Component Re-render
    ↓
Send Command via Telegram API
    ↓
Bot Receives Command
    ↓
Execute Action
    ↓
Send Result Back
    ↓
Update UI
```

---

## Command Types & Routing

```
JSON Command
    ↓
    ├─ type: "command"
    │   ├─ action: "open_url" → Open URL
    │   ├─ action: "screenshot" → Take screenshot
    │   ├─ action: "hotkey" → Press hotkey
    │   ├─ action: "click_center" → Click center
    │   ├─ action: "write" → Write text
    │   ├─ action: "switch_tab" → Switch tab
    │   ├─ action: "run_program" → Run program
    │   ├─ action: "move_mouse" → Move mouse
    │   ├─ action: "click" → Click at coords
    │   └─ action: "keypress" → Press key
    │
    └─ type: "ai_raw"
        └─ text: "natural language command"
            → TaskInterpreter
            → Executor
            → Result
```

---

## Theme System

```
Telegram App
    ↓
tg.colorScheme (dark/light)
    ↓
App.jsx detects theme
    ↓
setIsDarkMode(isDark)
    ↓
className: app dark/light
    ↓
CSS applies theme colors
    ├─ Dark: #0f0f0f background
    └─ Light: #ffffff background
```

---

## Responsive Design

```
Screen Size
    ↓
    ├─ < 480px (Mobile)
    │   └─ 2 columns
    ├─ 481-768px (Tablet)
    │   └─ 3 columns
    └─ > 768px (Desktop)
        └─ 4 columns
```

---

## Error Handling

```
User Action
    ↓
Try {
    Execute Command
    Send via Telegram API
} Catch {
    Log error
    Show alert to user
    tg.showAlert("Error message")
}
```

---

## Performance Considerations

### Bundle Size
- React: ~40KB
- Vite: ~10KB
- Lucide Icons: ~5KB
- CSS: ~15KB
- **Total**: ~70KB (uncompressed)
- **Gzipped**: ~20KB

### Optimization
- Code splitting (Vite)
- CSS minification
- Icon tree-shaking
- Lazy loading (if needed)

### Load Time
- Initial load: < 1s
- Interactive: < 2s
- Fully loaded: < 3s

---

## Security Flow

```
User Input
    ↓
Validate (not empty, etc.)
    ↓
Create JSON
    ↓
Send via Telegram API
    ↓
Telegram validates
    ↓
Bot receives (authenticated)
    ↓
Bot validates command
    ↓
Execute on PC
    ↓
Return result
```

---

## Deployment Architecture

```
Development
├── npm run dev
└── http://localhost:5173

Production
├── npm run build
├── dist/ folder created
└── Upload to:
    ├── Vercel
    ├── Netlify
    └── Any web host

Telegram Bot
├── Set WebAppInfo URL
└── User clicks button
    └── Opens Mini App
```

---

## Integration Points

### 1. Telegram WebApp API
```javascript
window.Telegram.WebApp
├── ready()
├── expand()
├── sendData()
├── showAlert()
├── showConfirm()
├── themeParams
└── colorScheme
```

### 2. Bot Handler
```python
message.web_app_data
├── data (JSON string)
└── button_text
```

### 3. PC Agent
```python
ScreenCapture()
ClickController()
KeyboardController()
WindowController()
TaskInterpreter()
Executor()
```

---

## Summary

The Mini App follows a clean, modular architecture:

1. **Frontend** (React) - User interface
2. **API Layer** (Telegram WebApp) - Communication
3. **Bot** (Python) - Command processing
4. **Agent** (PC Control) - Execution

Each layer is independent and can be modified without affecting others.

**Result**: A scalable, maintainable, and user-friendly PC control system! 🚀
