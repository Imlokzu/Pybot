# Quick Setup Guide

## 🚀 Get Started in 5 Minutes

### Step 1: Install Dependencies
```bash
cd mini-app
npm install
```

### Step 2: Run Development Server
```bash
npm run dev
```

Open `http://localhost:5173` in your browser.

### Step 3: Test with Telegram WebApp API

The app will automatically initialize the Telegram WebApp API. You can test by:

1. Opening DevTools (F12)
2. Going to Console tab
3. Typing:
```javascript
window.Telegram.WebApp.sendData(JSON.stringify({type: "test"}))
```

### Step 4: Build for Production
```bash
npm run build
```

This creates a `dist/` folder with optimized files.

### Step 5: Deploy

Choose one:

#### **Vercel** (Easiest)
```bash
npm install -g vercel
vercel
```

#### **Netlify**
```bash
npm install -g netlify-cli
netlify deploy --prod --dir=dist
```

#### **Manual Upload**
Upload the `dist/` folder to any web hosting.

## 🔗 Connect to Your Bot

In your Python bot code:

```python
from aiogram.types import WebAppInfo, InlineKeyboardButton, InlineKeyboardMarkup

# Create Mini App button
mini_app_button = InlineKeyboardButton(
    text="🎮 PC Control",
    web_app=WebAppInfo(url="https://your-app-url.vercel.app")
)

keyboard = InlineKeyboardMarkup(inline_keyboard=[[mini_app_button]])

await message.answer(
    "Click the button to open PC Control:",
    reply_markup=keyboard
)
```

## 📨 Handling Commands in Your Bot

When the Mini App sends data, your bot receives it in the `web_app_data` field:

```python
@dp.message()
async def handle_web_app_data(message: Message):
    if message.web_app_data:
        data = json.loads(message.web_app_data.data)
        
        if data.get('type') == 'command':
            action = data.get('action')
            # Handle the command
            if action == 'screenshot':
                # Take screenshot
                pass
            elif action == 'open_url':
                # Open URL
                pass
            # ... etc
        
        elif data.get('type') == 'ai_raw':
            # Handle AI command
            text = data.get('text')
            # Send to your AI interpreter
            pass
```

## 🎯 Command Flow

```
User clicks button in Mini App
    ↓
Mini App sends JSON via tg.sendData()
    ↓
Telegram sends to bot as web_app_data
    ↓
Bot parses JSON and executes command
    ↓
Bot sends result back to user
```

## 🌐 Environment Variables

Create `.env` file (optional):

```env
VITE_BOT_API_URL=https://your-bot-api.com
VITE_APP_NAME=PC Remote Control
```

Use in code:
```javascript
const apiUrl = import.meta.env.VITE_BOT_API_URL
```

## 📱 Testing on Mobile

### Using ngrok (Local Testing)

1. Install ngrok: https://ngrok.com/download

2. Run:
```bash
ngrok http 5173
```

3. Copy the URL (e.g., `https://abc123.ngrok.io`)

4. Set in your bot:
```python
WebAppInfo(url="https://abc123.ngrok.io")
```

5. Open in Telegram on mobile

### Production Testing

1. Deploy to Vercel/Netlify
2. Set URL in bot
3. Open Mini App from Telegram on mobile

## 🔧 Troubleshooting

### "Telegram is not defined"
- Make sure `<script src="https://telegram.org/js/telegram-web-app.js"></script>` is in `index.html`
- Reload the page

### Commands not sending
- Check DevTools Console for errors
- Verify `tg.sendData()` is being called
- Make sure bot is handling `web_app_data`

### Styling looks wrong
- Clear browser cache (Ctrl+Shift+Delete)
- Hard refresh (Ctrl+Shift+R)

### App not expanding
- Make sure `tg.expand()` is called in App.jsx
- Check Telegram WebApp API documentation

## 📚 Resources

- [Telegram WebApp Docs](https://core.telegram.org/bots/webapps)
- [React Docs](https://react.dev)
- [Vite Docs](https://vitejs.dev)
- [Lucide Icons](https://lucide.dev)

## ✅ Checklist

- [ ] Dependencies installed (`npm install`)
- [ ] Dev server running (`npm run dev`)
- [ ] App opens at localhost:5173
- [ ] Buttons work in console
- [ ] Built for production (`npm run build`)
- [ ] Deployed to hosting
- [ ] URL added to bot
- [ ] Bot handles `web_app_data`
- [ ] Mini App opens from Telegram
- [ ] Commands execute on PC

## 🎉 You're Done!

Your PC Remote Control Mini App is ready to use!

For questions, check the README.md or Telegram WebApp documentation.
