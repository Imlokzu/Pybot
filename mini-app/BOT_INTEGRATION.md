# Bot Integration Guide

## How to Connect the Mini App to Your Telegram Bot

### Step 1: Add Mini App Button to Your Bot

In your `main.py`, add this to your `/start` command:

```python
from aiogram.types import WebAppInfo, InlineKeyboardButton, InlineKeyboardMarkup

@dp.message(Command('start'))
async def cmd_start(message: Message):
    """Start command with Mini App button"""
    
    # Create Mini App button
    mini_app_button = InlineKeyboardButton(
        text="🎮 PC Control",
        web_app=WebAppInfo(url="https://your-deployed-app.vercel.app")
    )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[mini_app_button]])
    
    await message.answer(
        "Click the button to open PC Control Mini App:",
        reply_markup=keyboard
    )
```

### Step 2: Handle Mini App Commands

Add a handler for `web_app_data`:

```python
import json
from aiogram.types import Message

@dp.message()
async def handle_web_app_data(message: Message):
    """Handle data from Mini App"""
    
    if message.web_app_data:
        try:
            data = json.loads(message.web_app_data.data)
            
            # Handle different command types
            if data.get('type') == 'command':
                await handle_command(message, data)
            
            elif data.get('type') == 'ai_raw':
                await handle_ai_command(message, data)
            
            # Send confirmation
            await message.answer("✅ Command received!")
            
        except json.JSONDecodeError:
            await message.answer("❌ Invalid command format")
        except Exception as e:
            await message.answer(f"❌ Error: {str(e)}")


async def handle_command(message: Message, data: dict):
    """Handle structured commands from Mini App"""
    
    action = data.get('action')
    
    # Route to appropriate handler
    if action == 'open_url':
        url = data.get('url')
        await message.answer(f"Opening: {url}")
        # Your code to open URL on PC
    
    elif action == 'switch_tab':
        tab_num = data.get('number')
        await message.answer(f"Switching to tab {tab_num}")
        # Your code to switch tabs
    
    elif action == 'screenshot':
        await message.answer("📸 Taking screenshot...")
        # Your code to take screenshot
        # Then send back to user
    
    elif action == 'click_center':
        await message.answer("🖱️ Clicking center...")
        # Your code to click center
    
    elif action == 'write':
        text = data.get('text')
        await message.answer(f"Writing: {text}")
        # Your code to write text
    
    elif action == 'hotkey':
        keys = data.get('keys', [])
        await message.answer(f"Pressing: {' + '.join(keys)}")
        # Your code to press hotkey
    
    elif action == 'click':
        x = data.get('x')
        y = data.get('y')
        await message.answer(f"Clicking at ({x}, {y})")
        # Your code to click at coordinates
    
    elif action == 'move_mouse':
        x = data.get('x')
        y = data.get('y')
        await message.answer(f"Moving mouse by ({x}, {y})")
        # Your code to move mouse
    
    elif action == 'run_program':
        path = data.get('path')
        await message.answer(f"Running: {path}")
        # Your code to run program
    
    else:
        await message.answer(f"Unknown action: {action}")


async def handle_ai_command(message: Message, data: dict):
    """Handle AI natural language commands"""
    
    text = data.get('text')
    await message.answer(f"🤖 Processing: {text}")
    
    # Send to your TaskInterpreter
    from agents.task_interpreter import TaskInterpreter
    
    interpreter = TaskInterpreter()
    task = await interpreter.interpret(text)
    
    # Execute the task
    from agents.executor import Executor
    
    executor = Executor()
    result = await executor.execute(task)
    
    await message.answer(f"✅ Done: {result}")
```

### Step 3: Send Screenshots Back to Mini App

When user takes a screenshot, send it back:

```python
from aiogram.types import FSInputFile

async def send_screenshot_to_mini_app(message: Message, screenshot_path: str):
    """Send screenshot to user"""
    
    photo = FSInputFile(screenshot_path)
    
    await message.answer_photo(
        photo,
        caption="📸 Latest screenshot from your PC"
    )
```

### Step 4: Full Integration Example

Here's a complete example to add to your `main.py`:

```python
import json
from aiogram.types import WebAppInfo, InlineKeyboardButton, InlineKeyboardMarkup, Message

# Add Mini App button to start menu
@dp.message(Command('start'))
async def cmd_start_with_mini_app(message: Message):
    """Start command with Mini App button"""
    
    user_id = message.from_user.id
    
    if not auth_manager.is_authenticated(user_id):
        await message.answer("Please authenticate first")
        return
    
    # Create Mini App button
    mini_app_button = InlineKeyboardButton(
        text="🎮 PC Control",
        web_app=WebAppInfo(url="https://your-app.vercel.app")
    )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[mini_app_button]])
    
    await message.answer(
        "🎮 <b>PC Remote Control</b>\n\n"
        "Click the button below to open the Mini App:",
        reply_markup=keyboard,
        parse_mode="HTML"
    )


# Handle all Mini App data
@dp.message()
async def handle_mini_app_command(message: Message):
    """Handle commands from Mini App"""
    
    user_id = message.from_user.id
    
    if not auth_manager.is_authenticated(user_id):
        await message.answer("❌ Not authenticated")
        return
    
    if not message.web_app_data:
        return  # Not from Mini App
    
    try:
        data = json.loads(message.web_app_data.data)
        logger.info(f"Mini App command from {user_id}: {data}")
        
        if data.get('type') == 'command':
            action = data.get('action')
            
            if action == 'screenshot':
                screen = ScreenCapture()
                path = screen.capture()
                photo = FSInputFile(path)
                await message.answer_photo(photo, caption="📸 Screenshot")
            
            elif action == 'open_url':
                url = data.get('url')
                await message.answer(f"Opening: {url}")
                # Your code here
            
            elif action == 'hotkey':
                keys = data.get('keys', [])
                await message.answer(f"Hotkey: {' + '.join(keys)}")
                # Your code here
            
            # ... handle other actions
        
        elif data.get('type') == 'ai_raw':
            text = data.get('text')
            await message.answer(f"Processing: {text}")
            
            # Use your TaskInterpreter
            interpreter = TaskInterpreter()
            task = await interpreter.interpret(text)
            
            executor = Executor()
            result = await executor.execute(task)
            
            await message.answer(f"✅ {result}")
        
        else:
            await message.answer("❌ Unknown command type")
    
    except json.JSONDecodeError:
        await message.answer("❌ Invalid JSON")
    except Exception as e:
        logger.error(f"Error handling Mini App command: {e}")
        await message.answer(f"❌ Error: {str(e)}")
```

### Step 5: Update Your Menu

Add Mini App to your main menu:

```python
@dp.message(Command('menu'))
async def cmd_menu(message: Message):
    """Show main menu with Mini App"""
    
    mini_app_button = InlineKeyboardButton(
        text="🎮 PC Control",
        web_app=WebAppInfo(url="https://your-app.vercel.app")
    )
    
    other_buttons = [
        InlineKeyboardButton(text="📸 Screenshot", callback_data="screenshot"),
        InlineKeyboardButton(text="📋 Changes", callback_data="changes"),
    ]
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [mini_app_button],
        other_buttons,
    ])
    
    await message.answer("Choose an option:", reply_markup=keyboard)
```

## 🔄 Command Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    Telegram Mini App                         │
│  (React app running in Telegram WebView)                    │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ tg.sendData(JSON)
                         ↓
┌─────────────────────────────────────────────────────────────┐
│                   Telegram Bot API                           │
│  (Receives web_app_data in message)                         │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ Parse JSON
                         ↓
┌─────────────────────────────────────────────────────────────┐
│                   Your Bot Handler                           │
│  (Processes command and executes action)                    │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ Execute on PC
                         ↓
┌─────────────────────────────────────────────────────────────┐
│                   PC Agent/Executor                          │
│  (Performs actual action on computer)                       │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ Send result back
                         ↓
┌─────────────────────────────────────────────────────────────┐
│                   Telegram Mini App                          │
│  (Display result to user)                                   │
└─────────────────────────────────────────────────────────────┘
```

## 📝 JSON Command Examples

### Screenshot
```json
{
  "type": "command",
  "action": "screenshot"
}
```

### Open URL
```json
{
  "type": "command",
  "action": "open_url",
  "url": "https://youtube.com"
}
```

### Hotkey
```json
{
  "type": "command",
  "action": "hotkey",
  "keys": ["ctrl", "shift", "esc"]
}
```

### AI Command
```json
{
  "type": "ai_raw",
  "text": "open firefox and go to youtube"
}
```

## ✅ Testing Checklist

- [ ] Mini App button appears in /start
- [ ] Button opens Mini App in Telegram
- [ ] Commands send JSON to bot
- [ ] Bot receives web_app_data
- [ ] Commands execute on PC
- [ ] Results display in Mini App
- [ ] Screenshots display in Mini App
- [ ] AI commands work
- [ ] Error handling works

## 🚀 Deployment

1. Deploy Mini App to Vercel/Netlify
2. Get the URL
3. Update `WebAppInfo(url="...")` in your bot
4. Restart bot
5. Test in Telegram

Done! Your Mini App is now connected to your bot! 🎉
