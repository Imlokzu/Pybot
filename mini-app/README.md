# PC Remote Control - Telegram Mini App

A modern, responsive Telegram Mini App for controlling your PC remotely through Telegram.

## 🎯 Features

- **Quick Commands**: One-click buttons for common actions
  - Open URLs
  - Switch browser tabs
  - Take screenshots
  - Click center
  - Run programs
  - Write text
  - Custom hotkeys

- **Quick Actions**: Organized shortcuts
  - Browser controls (Back, Forward, Refresh)
  - Mouse controls (Move in 4 directions)
  - Keyboard shortcuts (Copy, Paste, Undo, Redo)

- **AI Command Input**: Natural language command support
  - Type commands in plain English
  - Bot interprets and executes

- **Screenshot Viewer**: Display PC screenshots in real-time

- **Theme Support**: Automatically adapts to Telegram's dark/light theme

- **Responsive Design**: Works on all device sizes

## 📁 Project Structure

```
mini-app/
├── index.html                 # Main HTML file
├── package.json              # Dependencies
├── vite.config.js            # Vite configuration
├── src/
│   ├── main.jsx              # React entry point
│   ├── index.css             # Global styles
│   ├── App.jsx               # Main app component
│   ├── App.css               # App styles
│   ├── context/
│   │   └── TelegramContext.jsx  # Telegram API context
│   └── components/
│       ├── Header.jsx        # Header component
│       ├── Header.css
│       ├── CommandPanel.jsx  # Command buttons
│       ├── CommandPanel.css
│       ├── ButtonCard.jsx    # Reusable button card
│       ├── ButtonCard.css
│       ├── QuickActions.jsx  # Quick action buttons
│       ├── QuickActions.css
│       ├── AICommandInput.jsx # AI command input
│       ├── AICommandInput.css
│       ├── ScreenshotViewer.jsx # Screenshot display
│       └── ScreenshotViewer.css
└── README.md
```

## 🚀 Installation & Setup

### Prerequisites
- Node.js 16+ and npm

### Local Development

1. **Install dependencies**:
```bash
cd mini-app
npm install
```

2. **Start development server**:
```bash
npm run dev
```

The app will be available at `http://localhost:5173`

3. **Build for production**:
```bash
npm run build
```

Output will be in the `dist/` folder.

## 🔌 Telegram WebApp Integration

The Mini App uses the official Telegram WebApp JavaScript API:

```javascript
const tg = window.Telegram.WebApp;
tg.ready();
tg.expand();
```

### Sending Commands to Bot

All commands are sent as JSON via:

```javascript
tg.sendData(JSON.stringify({
  type: "command",
  action: "open_url",
  url: "https://google.com"
}));
```

### Command Types

#### 1. **open_url**
```json
{
  "type": "command",
  "action": "open_url",
  "url": "https://example.com"
}
```

#### 2. **switch_tab**
```json
{
  "type": "command",
  "action": "switch_tab",
  "number": 1
}
```

#### 3. **write**
```json
{
  "type": "command",
  "action": "write",
  "text": "Hello World"
}
```

#### 4. **keypress**
```json
{
  "type": "command",
  "action": "keypress",
  "key": "enter"
}
```

#### 5. **hotkey**
```json
{
  "type": "command",
  "action": "hotkey",
  "keys": ["ctrl", "c"]
}
```

#### 6. **click_center**
```json
{
  "type": "command",
  "action": "click_center"
}
```

#### 7. **click**
```json
{
  "type": "command",
  "action": "click",
  "x": 100,
  "y": 200
}
```

#### 8. **move_mouse**
```json
{
  "type": "command",
  "action": "move_mouse",
  "x": 50,
  "y": 50
}
```

#### 9. **screenshot**
```json
{
  "type": "command",
  "action": "screenshot"
}
```

#### 10. **run_program**
```json
{
  "type": "command",
  "action": "run_program",
  "path": "notepad.exe"
}
```

#### 11. **AI Raw Command**
```json
{
  "type": "ai_raw",
  "text": "open firefox and go to youtube"
}
```

## 🌐 Deployment

### Option 1: Vercel (Recommended)

1. **Push to GitHub**:
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/yourusername/pc-remote-mini-app.git
git push -u origin main
```

2. **Deploy to Vercel**:
   - Go to https://vercel.com
   - Click "New Project"
   - Select your GitHub repository
   - Vercel will auto-detect Vite
   - Click "Deploy"

3. **Get your URL**: `https://your-project.vercel.app`

### Option 2: Netlify

1. **Build locally**:
```bash
npm run build
```

2. **Deploy**:
   - Go to https://netlify.com
   - Drag and drop the `dist/` folder
   - Or connect GitHub for auto-deployment

### Option 3: GitHub Pages

1. **Update vite.config.js**:
```javascript
export default defineConfig({
  base: '/pc-remote-mini-app/', // Your repo name
  // ... rest of config
})
```

2. **Build and push**:
```bash
npm run build
git add dist/
git commit -m "Build"
git push
```

3. **Enable GitHub Pages** in repository settings

## 🔗 Connecting to Telegram Bot

In your Telegram bot code, set the Mini App URL:

```python
# In your bot's /start command or menu button
from aiogram.types import WebAppInfo, InlineKeyboardButton, InlineKeyboardMarkup

button = InlineKeyboardButton(
    text="🎮 Open PC Control",
    web_app=WebAppInfo(url="https://your-deployed-app.vercel.app")
)
```

## 📱 Testing in Telegram

1. **Local Testing** (with ngrok):
```bash
# Install ngrok: https://ngrok.com
ngrok http 5173
# Use the ngrok URL in your bot
```

2. **Production Testing**:
   - Deploy to Vercel/Netlify
   - Set the URL in your bot
   - Open the Mini App from Telegram

## 🎨 Customization

### Colors
Edit the gradient colors in component CSS files:
```css
background: linear-gradient(135deg, #0096ff 0%, #64c8ff 100%);
```

### Commands
Add new buttons in `CommandPanel.jsx`:
```javascript
{
  icon: YourIcon,
  label: 'Your Command',
  action: () => sendCommand({
    type: 'command',
    action: 'your_action',
    // ... params
  })
}
```

### Theme
The app automatically adapts to Telegram's theme. To customize:
```javascript
const themeParams = tg.themeParams;
const bgColor = themeParams.bg_color;
const textColor = themeParams.text_color;
```

## 🐛 Debugging

Enable console logs:
```javascript
// In TelegramContext.jsx
console.log('Sending command:', jsonData)
```

View logs in Telegram:
- Open Developer Tools (F12)
- Check Console tab

## 📝 License

MIT

## 🤝 Support

For issues or questions, check:
- [Telegram WebApp Documentation](https://core.telegram.org/bots/webapps)
- [React Documentation](https://react.dev)
- [Vite Documentation](https://vitejs.dev)
