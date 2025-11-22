import logging
import json
import os
import google.generativeai as genai
from dotenv import load_dotenv

logger = logging.getLogger(__name__)
load_dotenv()

# Configure Gemini API
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)


class GeminiTaskInterpreter:
    """AI-powered task interpreter using Google Gemini"""
    
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-pro')
        self.system_prompt = """You are a PC control command interpreter. 
        
Your job is to parse natural language commands and convert them to structured JSON commands.

Available actions:
- click: Click on screen (can specify coordinates or element name)
- type: Write text
- screenshot: Take screenshot
- open_app: Open application
- close_app: Close application
- hotkey: Press keyboard shortcut (ctrl, alt, shift, etc.)
- wait: Wait for seconds
- drag: Drag mouse
- move_mouse: Move mouse to coordinates
- keypress: Press single key
- open_url: Open URL in browser
- switch_tab: Switch browser tab
- run_program: Run program/executable

IMPORTANT: Always respond with valid JSON only, no markdown, no explanations.

Example input: "take a screenshot"
Example output: {"action": "screenshot"}

Example input: "open firefox and go to youtube"
Example output: {"action": "sequence", "tasks": [{"action": "open_app", "target": "firefox"}, {"action": "open_url", "url": "https://youtube.com"}]}

Example input: "write hello world"
Example output: {"action": "type", "target": "hello world"}

Example input: "click on the button"
Example output: {"action": "click", "target": "button"}

Example input: "press ctrl+c"
Example output: {"action": "hotkey", "keys": ["ctrl", "c"]}

Parse the following command and respond ONLY with JSON:"""
    
    async def interpret(self, task_text: str) -> dict:
        """Interpret task using Gemini AI"""
        try:
            if not GEMINI_API_KEY:
                logger.warning("Gemini API key not found, using fallback interpreter")
                return self._fallback_interpret(task_text)
            
            # Send to Gemini
            prompt = f"{self.system_prompt}\n\n{task_text}"
            response = self.model.generate_content(prompt)
            
            # Parse response
            response_text = response.text.strip()
            
            # Remove markdown code blocks if present
            if response_text.startswith('```'):
                response_text = response_text.split('```')[1]
                if response_text.startswith('json'):
                    response_text = response_text[4:]
            
            response_text = response_text.strip()
            
            # Parse JSON
            result = json.loads(response_text)
            
            # Add description
            result['description'] = task_text
            
            logger.info(f"Gemini interpreted: {result}")
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON parse error: {e}, response: {response_text}")
            return self._fallback_interpret(task_text)
        except Exception as e:
            logger.error(f"Gemini interpretation error: {e}")
            return self._fallback_interpret(task_text)
    
    def _fallback_interpret(self, task_text: str) -> dict:
        """Fallback to simple keyword matching"""
        task_lower = task_text.lower()
        
        if 'screenshot' in task_lower or 'screen' in task_lower:
            return {
                "action": "screenshot",
                "description": task_text
            }
        elif 'type' in task_lower or 'write' in task_lower or 'напиши' in task_lower:
            return {
                "action": "type",
                "target": task_text.replace('type', '').replace('write', '').replace('напиши', '').strip(),
                "description": task_text
            }
        elif 'click' in task_lower or 'натисни' in task_lower:
            return {
                "action": "click",
                "target": "center",
                "description": task_text
            }
        elif 'open' in task_lower or 'відкрий' in task_lower:
            return {
                "action": "open_app",
                "target": task_text,
                "description": task_text
            }
        else:
            return {
                "action": "type",
                "target": task_text,
                "description": task_text
            }
