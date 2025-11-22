# Quick Reference Card

## 🚀 Getting Started (5 Minutes)

```bash
# 1. Install
cd mini-app
npm install

# 2. Run
npm run dev

# 3. Build
npm run build

# 4. Deploy
vercel  # or netlify deploy --prod --dir=dist
```

---

## 📱 Mini App URL

Once deployed, you'll have a URL like:
```
https://your-app.vercel.app
```

Add to your bot:
```python
WebAppInfo(url="https://your-app.vercel.app")
```

---

## 📤 Sending Commands

### From Mini App
```javascript
// In any component
const { sendCommand } = useTelegram()

sendCommand({
  type: "command",
  action: "screenshot"
})
```

### To Bot
```python
# In your bot handler
if message.web_app_data:
    data = json.loads(message.web_app_data.data)
    # Process data...
```

---

## 🎯 Command Cheat Sheet

| Action | JSON |
|--------|------|
| Screenshot | `{type: "command", action: "screenshot"}` |
| Open URL | `{type: "command", action: "open_url", url: "..."}` |
| Hotkey | `{type: "command", action: "hotkey", keys: ["ctrl", "c"]}` |
| Write | `{type: "command", action: "write", text: "..."}` |
| Click | `{type: "command", action: "click_center"}` |
| AI Command | `{type: "ai_raw", text: "..."}` |

---

## 🎨 Customizing Buttons

### Add New Button

**File**: `src/components/CommandPanel.jsx`

```javascript
{
  icon: YourIcon,
  label: 'Your Label',
  action: () => sendCommand({
    type: 'command',
    action: 'your_action',
    // Add parameters here
  })
}
```

### Change Colors

**File**: `src/components/ButtonCard.css`

```css
background: linear-gradient(135deg, #YOUR_COLOR_1 0%, #YOUR_COLOR_2 100%);
```

---

## 📁 File Locations

| What | Where |
|------|-------|
| Main App | `src/App.jsx` |
| Telegram API | `src/context/TelegramContext.jsx` |
| Commands | `src/components/CommandPanel.jsx` |
| Quick Actions | `src/components/QuickActions.jsx` |
| AI Input | `src/components/AICommandInput.jsx` |
| Styles | `src/components/*.css` |

---

## 🔧 Common Tasks

### Add New Quick Action

**File**: `src/components/QuickActions.jsx`

```javascript
{
  category: 'New Category',
  items: [
    { 
      label: 'Action Name', 
      action: () => sendCommand({...}) 
    }
  ]
}
```

### Change Theme Colors

**File**: `src/App.css`

```css
.app.dark {
  background-color: #YOUR_COLOR;
  color: #YOUR_TEXT_COLOR;
}
```

### Add New Component

1. Create `src/components/YourComponent.jsx`
2. Create `src/components/YourComponent.css`
3. Import in `src/App.jsx`
4. Add to JSX

---

## 🐛 Debugging

### Check Console
```javascript
// In browser DevTools (F12)
// Console tab shows all logs
```

### Test Command
```javascript
// In browser console
window.Telegram.WebApp.sendData(JSON.stringify({
  type: "test"
}))
```

### View Telegram Logs
```python
# In bot code
logger.info(f"Received: {data}")
```

---

## 📊 Project Stats

| Metric | Value |
|--------|-------|
| Components | 7 |
| CSS Files | 7 |
| Dependencies | 3 |
| Bundle Size | ~70KB |
| Gzipped | ~20KB |
| Load Time | < 2s |

---

## ✅ Deployment Checklist

- [ ] `npm install` completed
- [ ] `npm run dev` works locally
- [ ] `npm run build` succeeds
- [ ] No console errors
- [ ] All buttons work
- [ ] Theme switches correctly
- [ ] Responsive on mobile
- [ ] Deploy to Vercel/Netlify
- [ ] Get public URL
- [ ] Add URL to bot
- [ ] Test in Telegram
- [ ] Commands execute on PC

---

## 🔗 Important Links

| Resource | URL |
|----------|-----|
| Telegram WebApp Docs | https://core.telegram.org/bots/webapps |
| React Docs | https://react.dev |
| Vite Docs | https://vitejs.dev |
| Lucide Icons | https://lucide.dev |
| Vercel | https://vercel.com |
| Netlify | https://netlify.com |

---

## 💡 Pro Tips

1. **Use ngrok for local testing**
   ```bash
   ngrok http 5173
   ```

2. **Enable source maps for debugging**
   ```javascript
   // vite.config.js
   sourcemap: true
   ```

3. **Test on real device**
   - Use ngrok URL
   - Open in Telegram
   - Test all features

4. **Monitor bundle size**
   ```bash
   npm run build
   # Check dist/ folder size
   ```

5. **Use React DevTools**
   - Install React DevTools extension
   - Debug component state
   - Check props

---

## 🚨 Common Issues

| Issue | Solution |
|-------|----------|
| "Telegram is not defined" | Check `index.html` has script tag |
| Commands not sending | Check console for errors |
| Styling looks wrong | Clear cache (Ctrl+Shift+Delete) |
| App not expanding | Call `tg.expand()` in App.jsx |
| Mobile buttons too small | Check responsive CSS |

---

## 📝 Bot Integration Template

```python
import json
from aiogram.types import WebAppInfo, InlineKeyboardButton, InlineKeyboardMarkup

# Add button
@dp.message(Command('start'))
async def cmd_start(message: Message):
    button = InlineKeyboardButton(
        text="🎮 PC Control",
        web_app=WebAppInfo(url="https://your-app.vercel.app")
    )
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button]])
    await message.answer("Open PC Control:", reply_markup=keyboard)

# Handle commands
@dp.message()
async def handle_web_app(message: Message):
    if message.web_app_data:
        data = json.loads(message.web_app_data.data)
        # Process command...
        await message.answer("✅ Done!")
```

---

## 🎯 Next Steps

1. **Deploy** → Get URL
2. **Connect** → Add to bot
3. **Test** → Click button in Telegram
4. **Customize** → Add your commands
5. **Enjoy** → Control PC from Telegram!

---

## 📞 Need Help?

1. Check **README.md** for full docs
2. Check **SETUP.md** for setup issues
3. Check **BOT_INTEGRATION.md** for bot help
4. Check **ARCHITECTURE.md** for design
5. Read **Telegram WebApp Docs**

---

**Version**: 1.0.0
**Last Updated**: November 21, 2025
**Status**: ✅ Ready to Use
