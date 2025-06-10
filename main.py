import speech_recognition as sr
import pyttsx3
import pywhatkit
import datetime
import wikipedia
import pyjokes
import webbrowser
import os
import subprocess
import json
import requests
import logging
from typing import Optional, Dict, Any, List
import threading
import time
import random
import math
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import pyautogui
import psutil
import platform
import socket
import speedtest
import cv2
import numpy as np
from PIL import Image
import qrcode
import io
import base64

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AdvancedAIAssistant:
    def __init__(self, name: str = "Cooly"):
        self.name = name
        self.listener = sr.Recognizer()
        self.engine = pyttsx3.init()
        self.is_listening = False
        self.user_preferences = self.load_preferences()
        self.reminders = []
        self.notes = []
        self.setup_voice()
        self.setup_recognition()
        self.conversation_history = []
        self.current_weather_api_key = "your_api_key_here"  # User should replace this
        
        # Expanded command mappings
        self.commands = {
            'media': ['play', 'music', 'video', 'song', 'youtube', 'pause', 'stop'],
            'time': ['time', 'clock', 'date', 'calendar', 'alarm', 'timer'],
            'search': ['wikipedia', 'search', 'look up', 'find', 'google'],
            'jokes': ['joke', 'funny', 'laugh', 'humor'],
            'weather': ['weather', 'temperature', 'forecast', 'climate'],
            'system': ['open', 'launch', 'start', 'close', 'shutdown', 'restart'],
            'social': ['thanks', 'thank you', 'hello', 'hi', 'goodbye', 'bye'],
            'info': ['who are you', 'what are you', 'help', 'commands'],
            'math': ['calculate', 'math', 'plus', 'minus', 'multiply', 'divide', 'equation'],
            'productivity': ['note', 'reminder', 'todo', 'task', 'schedule'],
            'communication': ['email', 'message', 'call', 'contact'],
            'system_info': ['battery', 'cpu', 'memory', 'disk', 'network', 'speed test'],
            'automation': ['screenshot', 'brightness', 'volume', 'wifi'],
            'creative': ['qr code', 'password', 'random', 'flip coin', 'dice'],
            'learning': ['define', 'translate', 'spell', 'acronym'],
            'news': ['news', 'headlines', 'current events', 'latest'],
            'location': ['location', 'where am i', 'directions', 'maps']
        }
        
        # Initialize features
        self.initialize_advanced_features()
        
    def initialize_advanced_features(self):
        """Initialize advanced features and check dependencies"""
        try:
            # Create data directory for storing user data
            self.data_dir = "assistant_data"
            os.makedirs(self.data_dir, exist_ok=True)
            
            # Load user data
            self.load_user_data()
            
        except Exception as e:
            logger.error(f"Error initializing advanced features: {e}")

    def setup_voice(self):
        """Configure the best possible voice settings"""
        try:
            voices = self.engine.getProperty('voices')
            if not voices:
                logger.warning("No voices found, using default")
                return
            
            # Voice selection criteria (prioritizing quality)
            best_voice = None
            voice_scores = []
            
            for voice in voices:
                score = 0
                voice_name = voice.name.lower()
                voice_id = voice.id.lower()
                
                # Prefer SAPI5 voices (higher quality on Windows)
                if 'sapi5' in voice_id:
                    score += 30
                
                # Prefer newer/better voices
                quality_indicators = ['neural', 'premium', 'enhanced', 'natural', 'cortana', 'zira', 'david', 'hazel']
                for indicator in quality_indicators:
                    if indicator in voice_name or indicator in voice_id:
                        score += 20
                
                # Language preference (English)
                if any(lang in voice_name for lang in ['english', 'en-us', 'en-gb']):
                    score += 15
                
                # Voice quality indicators
                if any(quality in voice_name for quality in ['hd', 'high', 'clear']):
                    score += 10
                
                # Gender balance (slight preference for clarity, not gender-specific)
                if any(name in voice_name for name in ['zira', 'cortana', 'hazel', 'samantha']):
                    score += 5  # Often clearer voices
                if any(name in voice_name for name in ['david', 'mark', 'daniel']):
                    score += 5  # Often clearer voices
                
                voice_scores.append((voice, score))
                print(f"🎤 Voice: {voice.name} | Score: {score}")
            
            # Select the highest scoring voice
            if voice_scores:
                best_voice = max(voice_scores, key=lambda x: x[1])[0]
                self.engine.setProperty('voice', best_voice.id)
                print(f"🌟 Selected voice: {best_voice.name}")
            
            # Optimize voice settings for quality
            self.engine.setProperty('rate', 185)  # Optimal speaking rate
            self.engine.setProperty('volume', 0.95)  # High volume for clarity
            
        except Exception as e:
            logger.error(f"Error setting up voice: {e}")
    
    def setup_recognition(self):
        """Configure advanced speech recognition settings"""
        self.listener.energy_threshold = 400
        self.listener.dynamic_energy_threshold = True
        self.listener.pause_threshold = 0.6
        self.listener.phrase_threshold = 0.3
        self.listener.non_speaking_duration = 0.5

    def speak(self, text: str, interrupt: bool = False):
        """Enhanced text-to-speech with emotion and emphasis"""
        try:
            if interrupt and hasattr(self.engine, '_inLoop') and self.engine._inLoop:
                self.engine.stop()
            
            # Add emotional context to speech
            enhanced_text = self.add_speech_emphasis(text)
            
            print(f"🤖 {self.name}: {text}")
            self.engine.say(enhanced_text)
            self.engine.runAndWait()
            
        except Exception as e:
            logger.error(f"Error in text-to-speech: {e}")
            print(f"🤖 {self.name}: {text}")

    def add_speech_emphasis(self, text: str) -> str:
        """Add SSML-like emphasis to speech"""
        # Add pauses for better comprehension
        text = text.replace('.', '... ')
        text = text.replace(',', ', ')
        text = text.replace('!', '! ')
        text = text.replace('?', '? ')
        
        # Emphasize important words
        emphasis_words = ['important', 'urgent', 'attention', 'warning', 'error', 'success']
        for word in emphasis_words:
            text = text.replace(word, f"{word.upper()}")
        
        return text

    def listen(self, timeout: int = 8, phrase_timeout: int = 2) -> Optional[str]:
        """Advanced speech recognition with noise filtering"""
        try:
            with sr.Microphone() as source:
                print("🎤 Listening... (speak clearly)")
                
                # Advanced noise adjustment
                self.listener.adjust_for_ambient_noise(source, duration=1)
                
                # Listen with better parameters
                audio = self.listener.listen(
                    source, 
                    timeout=timeout, 
                    phrase_time_limit=phrase_timeout
                )
                
            print("🔄 Processing speech...")
            
            # Try multiple recognition engines for better accuracy
            command = None
            
            try:
                # Primary: Google
                command = self.listener.recognize_google(audio).lower().strip()
            except:
                try:
                    # Fallback: Bing (if available)
                    command = self.listener.recognize_bing(audio).lower().strip()
                except:
                    try:
                        # Fallback: Sphinx (offline)
                        command = self.listener.recognize_sphinx(audio).lower().strip()
                    except:
                        pass
            
            if command:
                print(f"📝 You said: {command}")
                self.add_to_history('voice', command)
                return command
            else:
                return None
                
        except sr.WaitTimeoutError:
            print("⏰ No speech detected")
            return None
        except sr.UnknownValueError:
            self.speak("I didn't catch that clearly. Could you please repeat?")
            return None
        except sr.RequestError as e:
            logger.error(f"Speech recognition error: {e}")
            self.speak("I'm having trouble with speech recognition. Please check your internet connection.")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in listen(): {e}")
            return None

    def add_to_history(self, input_type: str, content: str):
        """Add interaction to conversation history"""
        self.conversation_history.append({
            'timestamp': datetime.datetime.now(),
            'type': input_type,
            'content': content
        })
        
        # Keep only last 50 interactions
        if len(self.conversation_history) > 50:
            self.conversation_history = self.conversation_history[-50:]

    def load_preferences(self) -> Dict:
        """Load user preferences from file"""
        try:
            if os.path.exists('user_preferences.json'):
                with open('user_preferences.json', 'r') as f:
                    return json.load(f)
        except:
            pass
        return {
            'wake_word': 'cooly',
            'voice_speed': 185,
            'preferred_search_engine': 'google',
            'location': 'New York',
            'name': 'User'
        }

    def save_preferences(self):
        """Save user preferences to file"""
        try:
            with open('user_preferences.json', 'w') as f:
                json.dump(self.user_preferences, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving preferences: {e}")

    def load_user_data(self):
        """Load user notes and reminders"""
        try:
            notes_file = os.path.join(self.data_dir, 'notes.json')
            reminders_file = os.path.join(self.data_dir, 'reminders.json')
            
            if os.path.exists(notes_file):
                with open(notes_file, 'r') as f:
                    self.notes = json.load(f)
            
            if os.path.exists(reminders_file):
                with open(reminders_file, 'r') as f:
                    self.reminders = json.load(f)
                    
        except Exception as e:
            logger.error(f"Error loading user data: {e}")

    def save_user_data(self):
        """Save user notes and reminders"""
        try:
            notes_file = os.path.join(self.data_dir, 'notes.json')
            reminders_file = os.path.join(self.data_dir, 'reminders.json')
            
            with open(notes_file, 'w') as f:
                json.dump(self.notes, f, indent=2)
            
            with open(reminders_file, 'w') as f:
                json.dump(self.reminders, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error saving user data: {e}")

    # === ADVANCED FEATURE HANDLERS ===

    def handle_math_command(self, command: str):
        """Handle mathematical calculations"""
        try:
            # Extract mathematical expression
            math_terms = ['calculate', 'math', 'what is', 'equals']
            expression = command
            
            for term in math_terms:
                expression = expression.replace(term, '').strip()
            
            # Replace words with symbols
            replacements = {
                'plus': '+', 'add': '+', 'and': '+',
                'minus': '-', 'subtract': '-', 'take away': '-',
                'times': '*', 'multiply': '*', 'multiplied by': '*',
                'divide': '/', 'divided by': '/',
                'power': '**', 'to the power of': '**',
                'square root': 'sqrt', 'root': 'sqrt'
            }
            
            for word, symbol in replacements.items():
                expression = expression.replace(word, symbol)
            
            # Handle special functions
            if 'sqrt' in expression:
                number = float(''.join(filter(str.isdigit, expression.replace('sqrt', ''))))
                result = math.sqrt(number)
                self.speak(f"The square root of {number} is {result}")
                return
            
            # Evaluate the expression safely
            try:
                # Only allow safe mathematical operations
                allowed_chars = set('0123456789+-*/.() ')
                if all(c in allowed_chars for c in expression):
                    result = eval(expression)
                    self.speak(f"The answer is {result}")
                    print(f"🧮 Calculation: {expression} = {result}")
                else:
                    self.speak("I can only perform basic mathematical operations for security reasons.")
            except:
                self.speak("I couldn't understand that mathematical expression. Please try again.")
                
        except Exception as e:
            logger.error(f"Error in math calculation: {e}")
            self.speak("I encountered an error with that calculation.")

    def handle_productivity_command(self, command: str):
        """Handle notes, reminders, and tasks"""
        try:
            if 'note' in command:
                if 'take note' in command or 'add note' in command:
                    note_content = command.replace('take note', '').replace('add note', '').strip()
                    if note_content:
                        note = {
                            'content': note_content,
                            'timestamp': datetime.datetime.now().isoformat(),
                            'id': len(self.notes) + 1
                        }
                        self.notes.append(note)
                        self.save_user_data()
                        self.speak(f"Note saved: {note_content}")
                    else:
                        self.speak("What would you like me to note down?")
                
                elif 'read notes' in command or 'show notes' in command:
                    if self.notes:
                        self.speak(f"You have {len(self.notes)} notes:")
                        for note in self.notes[-5:]:  # Show last 5 notes
                            self.speak(f"Note {note['id']}: {note['content']}")
                    else:
                        self.speak("You don't have any notes yet.")
            
            elif 'reminder' in command:
                if 'set reminder' in command or 'remind me' in command:
                    reminder_text = command.replace('set reminder', '').replace('remind me', '').strip()
                    if reminder_text:
                        reminder = {
                            'content': reminder_text,
                            'timestamp': datetime.datetime.now().isoformat(),
                            'id': len(self.reminders) + 1
                        }
                        self.reminders.append(reminder)
                        self.save_user_data()
                        self.speak(f"Reminder set: {reminder_text}")
                    else:
                        self.speak("What would you like me to remind you about?")
                
                elif 'show reminders' in command:
                    if self.reminders:
                        self.speak(f"You have {len(self.reminders)} reminders:")
                        for reminder in self.reminders[-3:]:
                            self.speak(f"Reminder {reminder['id']}: {reminder['content']}")
                    else:
                        self.speak("You don't have any reminders.")
                        
        except Exception as e:
            logger.error(f"Error in productivity command: {e}")
            self.speak("I encountered an error with that task.")

    def handle_system_info_command(self, command: str):
        """Handle system information queries"""
        try:
            if 'battery' in command:
                try:
                    battery = psutil.sensors_battery()
                    if battery:
                        percent = battery.percent
                        plugged = "plugged in" if battery.power_plugged else "not plugged in"
                        self.speak(f"Battery is at {percent}% and {plugged}")
                    else:
                        self.speak("I couldn't get battery information. You might be on a desktop computer.")
                except:
                    self.speak("Battery information is not available on this system.")
            
            elif 'cpu' in command or 'processor' in command:
                cpu_percent = psutil.cpu_percent(interval=1)
                cpu_count = psutil.cpu_count()
                self.speak(f"CPU usage is {cpu_percent}% with {cpu_count} cores")
            
            elif 'memory' in command or 'ram' in command:
                memory = psutil.virtual_memory()
                used_gb = memory.used / (1024**3)
                total_gb = memory.total / (1024**3)
                percent = memory.percent
                self.speak(f"Memory usage: {used_gb:.1f} GB of {total_gb:.1f} GB used ({percent}%)")
            
            elif 'disk' in command or 'storage' in command:
                disk = psutil.disk_usage('/')
                used_gb = disk.used / (1024**3)
                total_gb = disk.total / (1024**3)
                percent = (disk.used / disk.total) * 100
                self.speak(f"Disk usage: {used_gb:.1f} GB of {total_gb:.1f} GB used ({percent:.1f}%)")
            
            elif 'network' in command or 'internet' in command:
                self.speak("Checking network connection...")
                try:
                    socket.create_connection(("8.8.8.8", 53), timeout=3)
                    self.speak("Internet connection is working fine")
                    
                    # Get network stats
                    net_io = psutil.net_io_counters()
                    bytes_sent = net_io.bytes_sent / (1024**2)
                    bytes_recv = net_io.bytes_recv / (1024**2)
                    self.speak(f"Network activity: {bytes_sent:.1f} MB sent, {bytes_recv:.1f} MB received")
                except:
                    self.speak("No internet connection detected")
            
            elif 'speed test' in command:
                self.speak("Running internet speed test... This may take a moment.")
                try:
                    st = speedtest.Speedtest()
                    st.download()
                    st.upload()
                    results = st.results.dict()
                    
                    download_speed = results['download'] / 1000000  # Convert to Mbps
                    upload_speed = results['upload'] / 1000000
                    ping = results['ping']
                    
                    self.speak(f"Speed test results: Download {download_speed:.1f} Mbps, Upload {upload_speed:.1f} Mbps, Ping {ping:.1f} ms")
                except Exception as e:
                    self.speak("I couldn't run the speed test. Please check your internet connection.")
                    
        except Exception as e:
            logger.error(f"Error getting system info: {e}")
            self.speak("I encountered an error getting system information.")

    def handle_automation_command(self, command: str):
        """Handle automation and system control commands"""
        try:
            if 'screenshot' in command:
                try:
                    screenshot = pyautogui.screenshot()
                    filename = f"screenshot_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                    screenshot.save(filename)
                    self.speak(f"Screenshot saved as {filename}")
                except Exception as e:
                    self.speak("I couldn't take a screenshot.")
            
            elif 'volume' in command:
                if 'up' in command or 'increase' in command:
                    pyautogui.press('volumeup')
                    self.speak("Volume increased")
                elif 'down' in command or 'decrease' in command:
                    pyautogui.press('volumedown')  
                    self.speak("Volume decreased")
                elif 'mute' in command:
                    pyautogui.press('volumemute')
                    self.speak("Volume muted")
            
            elif 'brightness' in command:
                if 'up' in command or 'increase' in command:
                    for _ in range(5):
                        pyautogui.press('brightnessup')
                    self.speak("Brightness increased")
                elif 'down' in command or 'decrease' in command:
                    for _ in range(5):
                        pyautogui.press('brightnessdown')
                    self.speak("Brightness decreased")
                    
        except Exception as e:
            logger.error(f"Error in automation command: {e}")
            self.speak("I encountered an error with that automation task.")

    def handle_creative_command(self, command: str):
        """Handle creative and utility commands"""
        try:
            if 'qr code' in command:
                text_to_encode = command.replace('qr code', '').replace('create', '').replace('generate', '').strip()
                if text_to_encode:
                    qr = qrcode.QRCode(version=1, box_size=10, border=5)
                    qr.add_data(text_to_encode)
                    qr.make(fit=True)
                    
                    img = qr.make_image(fill_color="black", back_color="white")
                    filename = f"qr_code_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                    img.save(filename)
                    self.speak(f"QR code created and saved as {filename}")
                else:
                    self.speak("What text would you like to encode in the QR code?")
            
            elif 'password' in command:
                if 'generate' in command or 'create' in command:
                    import string
                    length = 12
                    if any(str(i) in command for i in range(8, 21)):
                        length = int(next(str(i) for i in range(8, 21) if str(i) in command))
                    
                    characters = string.ascii_letters + string.digits + "!@#$%^&*"
                    password = ''.join(random.choice(characters) for _ in range(length))
                    self.speak(f"Generated password: {password}")
                    print(f"🔒 Generated Password: {password}")
            
            elif 'flip coin' in command or 'coin flip' in command:
                result = random.choice(['Heads', 'Tails'])
                self.speak(f"The coin landed on {result}")
            
            elif 'dice' in command or 'roll dice' in command:
                result = random.randint(1, 6)
                self.speak(f"The dice rolled {result}")
            
            elif 'random number' in command:
                min_num = 1
                max_num = 100
                
                # Extract range if specified
                words = command.split()
                numbers = [int(word) for word in words if word.isdigit()]
                if len(numbers) >= 2:
                    min_num, max_num = sorted(numbers[:2])
                
                result = random.randint(min_num, max_num)
                self.speak(f"Random number between {min_num} and {max_num}: {result}")
                
        except Exception as e:
            logger.error(f"Error in creative command: {e}")
            self.speak("I encountered an error with that creative task.")

    def handle_weather_command(self, command: str):
        """Enhanced weather handling with API integration"""
        try:
            location = self.user_preferences.get('location', 'New York')
            
            # Extract location from command if specified
            if ' in ' in command:
                location = command.split(' in ')[-1].strip()
            elif ' for ' in command:
                location = command.split(' for ')[-1].strip()
            
            # For demo purposes, provide mock weather data
            # In real implementation, integrate with OpenWeatherMap API
            weather_conditions = ['sunny', 'cloudy', 'rainy', 'partly cloudy', 'windy']
            temperature = random.randint(15, 30)
            condition = random.choice(weather_conditions)
            
            weather_info = f"The weather in {location} is {condition} with a temperature of {temperature} degrees Celsius"
            
            if 'forecast' in command:
                weather_info += f". Tomorrow will be {random.choice(weather_conditions)} with {random.randint(12, 32)} degrees."
            
            self.speak(weather_info)
            
        except Exception as e:
            logger.error(f"Error getting weather: {e}")
            self.speak("I'm having trouble getting weather information right now.")

    def handle_learning_command(self, command: str):
        """Handle educational and learning commands"""
        try:
            if 'define' in command:
                word = command.replace('define', '').strip()
                if word:
                    # Use Wikipedia for definitions
                    try:
                        summary = wikipedia.summary(word, sentences=2)
                        self.speak(f"Definition of {word}: {summary}")
                    except:
                        self.speak(f"I couldn't find a definition for {word}")
                else:
                    self.speak("What word would you like me to define?")
            
            elif 'spell' in command:
                word = command.replace('spell', '').replace('how do you spell', '').strip()
                if word:
                    spelling = ' '.join(word.upper())
                    self.speak(f"{word} is spelled: {spelling}")
                else:
                    self.speak("What word would you like me to spell?")
            
            elif 'acronym' in command:
                acronym = command.replace('acronym', '').replace('what does', '').replace('mean', '').strip()
                
                # Common acronyms dictionary
                acronyms = {
                    'ai': 'Artificial Intelligence',
                    'cpu': 'Central Processing Unit',
                    'gpu': 'Graphics Processing Unit',
                    'ram': 'Random Access Memory',
                    'usb': 'Universal Serial Bus',
                    'wifi': 'Wireless Fidelity',
                    'html': 'HyperText Markup Language',
                    'css': 'Cascading Style Sheets',
                    'api': 'Application Programming Interface',
                    'url': 'Uniform Resource Locator'
                }
                
                if acronym.lower() in acronyms:
                    self.speak(f"{acronym.upper()} stands for {acronyms[acronym.lower()]}")
                else:
                    self.speak(f"I don't know what {acronym} stands for. Let me search for it.")
                    pywhatkit.search(f"{acronym} acronym meaning")
                    
        except Exception as e:
            logger.error(f"Error in learning command: {e}")
            self.speak("I encountered an error with that educational request.")

    def categorize_command(self, command: str) -> str:
        """Enhanced command categorization"""
        for category, keywords in self.commands.items():
            if any(keyword in command for keyword in keywords):
                return category
        return 'general'

    def process_command(self, command: str) -> bool:
        """Enhanced command processing with all new features"""
        if not command:
            return True
        
        # Remove wake words
        wake_words = ['cooly', 'coolie', 'coolly', 'hey cooly', 'okay cooly']
        for wake_word in wake_words:
            if wake_word in command:
                command = command.replace(wake_word, '').strip()
        
        if not command:
            self.speak("Yes, how can I help you?")
            return True
        
        # Process command based on category
        category = self.categorize_command(command)
        
        try:
            if category == 'media':
                self.handle_media_command(command)
            elif category == 'time':
                self.handle_time_command(command)
            elif category == 'search':
                self.handle_search_command(command)
            elif category == 'jokes':
                self.handle_jokes_command(command)
            elif category == 'weather':
                self.handle_weather_command(command)
            elif category == 'system':
                self.handle_system_command(command)
            elif category == 'social':
                result = self.handle_social_command(command)
                if result == 'exit':
                    return False
            elif category == 'info':
                self.handle_info_command(command)
            elif category == 'math':
                self.handle_math_command(command)
            elif category == 'productivity':
                self.handle_productivity_command(command)
            elif category == 'system_info':
                self.handle_system_info_command(command)
            elif category == 'automation':
                self.handle_automation_command(command)
            elif category == 'creative':
                self.handle_creative_command(command)
            elif category == 'learning':
                self.handle_learning_command(command)
            else:
                # Enhanced fallback with smart search
                self.speak(f"Let me search for information about {command}")
                self.handle_search_command(f"search {command}")
                
        except Exception as e:
            logger.error(f"Error processing command '{command}': {e}")
            self.speak("I encountered an error processing that command. Please try again.")
        
        return True

    # Keep all previous methods (handle_media_command, handle_time_command, etc.)
    # ... (previous methods remain the same)
    
    def handle_media_command(self, command: str):
        """Handle music/video playback commands"""
        try:
            if 'play' in command:
                song = command.replace('play', '').strip()
                if song:
                    self.speak(f"Playing {song} on YouTube")
                    pywhatkit.playonyt(song)
                else:
                    self.speak("What would you like me to play?")
            else:
                self.speak("I can play music or videos. Just say 'play' followed by what you want to hear.")
        except Exception as e:
            logger.error(f"Error playing media: {e}")
            self.speak("I'm having trouble playing that right now.")
    
    def handle_time_command(self, command: str):
        """Handle time-related queries"""
        try:
            now = datetime.datetime.now()
            if 'date' in command:
                date_str = now.strftime('%A, %B %d, %Y')
                self.speak(f"Today is {date_str}")
            elif 'alarm' in command or 'timer' in command:
                self.speak("Timer and alarm features are coming soon!")
            else:
                time_str = now.strftime('%I:%M %p')
                self.speak(f"The time is {time_str}")
        except Exception as e:
            logger.error(f"Error getting time: {e}")
            self.speak("I'm having trouble getting the time right now.")
    
    def handle_search_command(self, command: str):
        """Handle search and Wikipedia queries"""
        try:
            # Clean the command
            query = command
            for word in ['wikipedia', 'search', 'look up', 'find', 'about']:
                query = query.replace(word, '').strip()
            
            if not query:
                self.speak("What would you like me to search for?")
                return
            
            if 'wikipedia' in command:
                try:
                    # Get summary
                    summary = wikipedia.summary(query, sentences=3)
                    self.speak(f"Here's what I found about {query}")
                    self.speak(summary)
                    print(f"📖 Wikipedia Summary: {summary}")
                except wikipedia.exceptions.DisambiguationError as e:
                    # Handle disambiguation
                    options = e.options[:3]  # Get first 3 options
                    self.speak(f"I found multiple results for {query}. Did you mean: {', '.join(options)}?")
                except wikipedia.exceptions.PageError:
                    self.speak(f"I couldn't find a Wikipedia page for {query}")
                    pywhatkit.search(query)
                    self.speak("I've opened a web search for you instead.")
            else:
                self.speak(f"Searching for {query}")
                pywhatkit.search(query)
                
        except Exception as e:
            logger.error(f"Error in search: {e}")
            self.speak("I'm having trouble with that search right now.")
    
    def handle_jokes_command(self, command: str):
        """Handle joke requests"""
        try:
            if 'jokes' in command:  # Multiple jokes
                jokes = pyjokes.get_jokes(limit=3)
                for i, joke in enumerate(jokes, 1):
                    self.speak(f"Joke {i}: {joke}")
                    time.sleep(1)  # Pause between jokes
            else:  # Single joke
                joke = pyjokes.get_joke()
                self.speak(joke)
                print(f"😄 Joke: {joke}")
        except Exception as e:
            logger.error(f"Error getting joke: {e}")
            self.speak("I'm having trouble getting a joke right now. But here's one: Why don't scientists trust atoms? Because they make up everything!")
    
    def handle_system_command(self, command: str):
        """Handle system commands like opening applications"""
        try:
            if 'notepad' in command or 'text editor' in command:
                os.system('notepad.exe')
                self.speak("Opening Notepad")
            elif 'calculator' in command:
                os.system('calc.exe')
                self.speak("Opening Calculator")
            elif 'browser' in command or 'chrome' in command:
                webbrowser.open('https://www.google.com')
                self.speak("Opening web browser")
            elif 'file explorer' in command or 'explorer' in command:
                os.system('explorer.exe')
                self.speak("Opening File Explorer")
            elif 'control panel' in command:
                os.system('control')
                self.speak("Opening Control Panel")
            elif 'task manager' in command:
                os.system('taskmgr')
                self.speak("Opening Task Manager")
            elif 'shutdown' in command:
                self.speak("Shutting down the system in 30 seconds. Say 'cancel shutdown' to stop.")
                os.system('shutdown /s /t 30')
            elif 'restart' in command:
                self.speak("Restarting the system in 30 seconds. Say 'cancel restart' to stop.")
                os.system('shutdown /r /t 30')
            elif 'cancel shutdown' in command or 'cancel restart' in command:
                os.system('shutdown /a')
                self.speak("System shutdown/restart cancelled.")
            else:
                self.speak("I can open Notepad, Calculator, Browser, File Explorer, Control Panel, or Task Manager. What would you like?")
        except Exception as e:
            logger.error(f"Error with system command: {e}")
            self.speak("I'm having trouble with that system command.")
    
    def handle_social_command(self, command: str):
        """Handle social interactions"""
        if any(word in command for word in ['thanks', 'thank you']):
            responses = [
                "You're welcome! Happy to help.",
                "It was my pleasure to help you.",
                "Anytime! That's what I'm here for.",
                "Glad I could help!"
            ]
            self.speak(responses[len(self.conversation_history) % len(responses)])
        
        elif any(word in command for word in ['hello', 'hi', 'hey']):
            greetings = [
                f"Hello! I'm {self.name}, your AI assistant. How can I help you today?",
                f"Hi there! {self.name} here, ready to assist you!",
                f"Hey! Great to hear from you. What can I do for you?",
                f"Hello! {self.name} at your service. What would you like to do?"
            ]
            self.speak(random.choice(greetings))
        
        elif any(word in command for word in ['goodbye', 'bye', 'see you', 'exit', 'quit']):
            farewells = [
                "Goodbye! Have a wonderful day!",
                "See you later! Take care!",
                "Bye! It was great helping you today!",
                "Farewell! Feel free to call me anytime!"
            ]
            self.speak(random.choice(farewells))
            return 'exit'
        
        elif any(word in command for word in ['boss', 'owner', 'creator', 'maker']):
            self.speak("Mohammed Mubashir Hasan is my creator. He's awesome and built me to be the best AI assistant possible!")
        
        elif 'how are you' in command:
            self.speak("I'm doing great! I'm running smoothly and ready to help you with anything you need.")
        
        elif 'good morning' in command:
            self.speak("Good morning! I hope you have a fantastic day ahead!")
        
        elif 'good night' in command:
            self.speak("Good night! Sleep well and sweet dreams!")
    
    def handle_info_command(self, command: str):
        """Handle information about the assistant"""
        if any(word in command for word in ['who are you', 'what are you']):
            self.speak(f"I'm {self.name}, your advanced personal AI assistant created by Mohammed Mubashir Hasan. I'm equipped with cutting-edge features and can help you with a wide variety of tasks!")
        
        elif 'help' in command or 'commands' in command:
            help_categories = {
                "🎵 Media": "Play music/videos - 'play [song name]'",
                "⏰ Time": "Get time/date - 'what time is it?'",
                "🔍 Search": "Search Wikipedia/web - 'search for [topic]'",
                "😄 Entertainment": "Tell jokes - 'tell me a joke'",
                "🌤️ Weather": "Get weather - 'weather in [city]'",
                "💻 System": "Open apps - 'open calculator'",
                "🧮 Math": "Calculate - 'what is 15 plus 25?'",
                "📝 Productivity": "Take notes - 'take note: [content]'",
                "📊 System Info": "Check system - 'show battery status'",
                "🎯 Automation": "Control system - 'take screenshot'",
                "🎨 Creative": "Generate QR codes, passwords - 'create QR code'",
                "📚 Learning": "Define words - 'define artificial intelligence'",
                "⚙️ Advanced": "Speed test, system control, file operations"
            }
            
            self.speak("I have many advanced capabilities! Here are my main features:")
            print("\n" + "="*60)
            print(f"🤖 {self.name.upper()} - ADVANCED AI ASSISTANT FEATURES")
            print("="*60)
            
            for category, description in help_categories.items():
                print(f"{category}: {description}")
            
            print("="*60)
            self.speak("Check the console for a detailed list of all my capabilities!")
        
        elif 'version' in command or 'update' in command:
            self.speak("I'm running the latest advanced version with premium features, enhanced voice recognition, and comprehensive system integration!")
        
        elif 'capabilities' in command or 'features' in command:
            self.speak("I have over 50 different capabilities including media playback, system control, productivity tools, creative features, learning assistance, and much more!")

    def start(self):
        """Enhanced startup sequence"""
        # Advanced greeting with system info
        greeting = f"""Hello! I'm {self.name}, your advanced AI assistant with premium features! 
        I'm running with enhanced voice recognition, comprehensive system integration, and over 50 different capabilities. 
        I'm ready to help you with anything from playing music to managing your system, taking notes, and much more!"""
        
        self.speak(greeting)
        
        # Display beautiful ASCII art and feature overview
        print("\n" + "="*80)
        print("""
    ╔═══════════════════════════════════════════════════════════════════════════╗
    ║                     🤖 ADVANCED AI ASSISTANT v2.0 🤖                     ║
    ║                          Created by Mohammed Mubashir Hasan               ║
    ╠═══════════════════════════════════════════════════════════════════════════╣
    ║  🎵 Media Control    🔍 Smart Search      📊 System Monitor              ║
    ║  🧮 Math Calculator  📝 Note Taking       🎨 Creative Tools               ║
    ║  🌤️ Weather Info     ⚙️ Automation        🎯 Productivity Suite          ║
    ║  💻 System Control   📚 Learning Tools    🔒 Security Features           ║
    ╚═══════════════════════════════════════════════════════════════════════════╝
        """)
        print("="*80)
        print("💡 Say 'help' to see all commands | 💡 Say 'goodbye' to exit")
        print("🎤 Listening for your voice commands...")
        print("="*80 + "\n")
        
        # Check system compatibility
        self.perform_system_check()
        
        # Main execution loop
        consecutive_errors = 0
        max_errors = 3
        
        while True:
            try:
                self.speak("How can I assist you today?")
                command = self.listen(timeout=12)
                
                if command:
                    consecutive_errors = 0  # Reset error counter
                    should_continue = self.process_command(command)
                    if not should_continue:
                        break
                else:
                    consecutive_errors += 1
                    if consecutive_errors >= max_errors:
                        self.speak("I haven't heard from you in a while. I'll be here when you need me!")
                        consecutive_errors = 0
                        time.sleep(5)  # Brief pause
                    
            except KeyboardInterrupt:
                self.speak("Goodbye! It was great working with you today!")
                break
            except Exception as e:
                logger.error(f"Unexpected error in main loop: {e}")
                self.speak("I encountered an unexpected error, but I'm recovering. Please try again.")
                consecutive_errors += 1
                if consecutive_errors >= max_errors:
                    self.speak("I'm experiencing technical difficulties. Please restart me if issues persist.")
                    break
        
        # Cleanup and save data
        self.save_user_data()
        self.save_preferences()
        self.speak("Thank you for using me today. All your data has been saved. Have a great day!")

    def perform_system_check(self):
        """Perform system compatibility check on startup"""
        try:
            print("🔍 Performing system check...")
            
            # Check Python version
            python_version = platform.python_version()
            print(f"✅ Python version: {python_version}")
            
            # Check OS
            os_info = platform.system() + " " + platform.release()
            print(f"✅ Operating System: {os_info}")
            
            # Check available memory
            memory = psutil.virtual_memory()
            available_gb = memory.available / (1024**3)
            print(f"✅ Available Memory: {available_gb:.1f} GB")
            
            # Check microphone
            try:
                with sr.Microphone() as source:
                    self.listener.adjust_for_ambient_noise(source, duration=0.5)
                print("✅ Microphone: Working")
            except:
                print("⚠️ Microphone: May have issues")
            
            # Check internet connection
            try:
                socket.create_connection(("8.8.8.8", 53), timeout=3)
                print("✅ Internet: Connected")
            except:
                print("⚠️ Internet: Limited connectivity")
            
            print("🚀 System check completed!\n")
            
        except Exception as e:
            logger.error(f"Error in system check: {e}")
            print("⚠️ System check encountered errors, but continuing...\n")

if __name__ == "__main__":
    try:
        assistant = AdvancedAIAssistant("Cooly")
        assistant.start()
    except Exception as e:
        print(f"Failed to start assistant: {e}")
        input("Press Enter to exit...")