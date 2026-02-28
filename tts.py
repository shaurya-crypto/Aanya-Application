import edge_tts
import asyncio
import pygame
import os
import re
import nest_asyncio  # 👈 ADD THIS
nest_asyncio.apply() #
import sys

try:
    pygame.mixer.init(frequency=24000, buffer=4096)
except:
    pass

# Voice Config
VOICE = "en-IN-NeerjaNeural"

def fix_pronunciation(text):
    """
    Fixes common pronunciation errors in Hinglish.
    The TTS reads English, so we must spell Hindi words phonetically.
    """
    if not text: return ""

    # Dictionary of fixes: "Original Word": "Phonetic Spelling"
    corrections = {
        # Basics
        r"\bAanya\b": "Aah-nya",       # Forces correct name pronunciation
        r"\bAI\b": "A.I.",             # Reads as letters, not "Ay"
        r"\bBoss\b": "Boss",           
        
        # Hindi pronouns & verbs (Crucial for Neerja)
        r"\bmain\b": "mein",           # 'Main' -> 'Mein' (Me)
        r"\bhum\b": "hum",
        r"\btum\b": "tum",
        r"\bkaun\b": " कौन ",          # Sometimes Hindi script works better
        r"\bkya\b": "kya",
        r"\bnahi\b": "nahin",          # Adds nasal sound
        r"\bha\b": "haan",
        r"\bhu\b": "hoon",             # 'Hu' -> 'Hoon'
        r"\bho\b": "ho",
        r"\bgaya\b": "gayaa",          # Long vowel
        r"\bkaro\b": "karo",
        r"\bkarungi\b": "karoongi",    # Long 'oo' sound
        r"\bchal\b": "chal",
        r"\brahi\b": "rahee",
        
        # Tech terms that might sound weird
        r"\bvideo\b": "vid-eo",
        r"\bdata\b": "day-ta",
    }

    # Apply corrections (Case insensitive replacement)
    for pattern, replacement in corrections.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    
    return text

def clean_text(text):
    """Removes asterisk actions like *laughs*."""
    if not text: return ""
    cleaned = re.sub(r'\*.*?\*', '', text)
    return cleaned.strip()

async def _gen(text):
    """Generates audio with Optimized Rate and Pitch."""
    file = "speech_output.mp3"
    
    # Force delete existing file
    if os.path.exists(file):
        try: os.remove(file)
        except: pass

    # 🔧 TUNING SETTINGS:
    # Rate: +5% (Clearer than +14%)
    # Pitch: +2Hz (Slightly brighter/happier tone)
    communicate = edge_tts.Communicate(text, VOICE, rate="+5%", pitch="+2Hz")
    await communicate.save(file)
    return file

def speak(text):
    """Main speak function."""
    
    # 1. Clean & Fix Pronunciation
    clean = clean_text(text)
    if not clean: return
    
    # We print the ORIGINAL text for the user to see
    print(f"Aanya: {clean}")
    
    # We send the PHONETIC text to the engine (Hidden)
    spoken_text = fix_pronunciation(clean)
    
    output_file = "speech_output.mp3"
    file_generated = False

    # 2. Generate Audio
    try:
        # Create a fresh event loop to avoid asyncio conflicts
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(_gen(spoken_text))
        loop.close()

        if os.path.exists(output_file):
            file_generated = True
    except Exception as e:
        print(f"❌ EdgeTTS Error: {e}")

    if not file_generated:
        return

    # 3. Playback
    try:
        try: pygame.mixer.music.unload()
        except: pass
            
        pygame.mixer.music.load(output_file)
        pygame.mixer.music.play()
        
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)

        pygame.mixer.music.unload()
        try: os.remove(output_file)
        except: pass
            
    except Exception as e:
        print(f"Audio Playback Error: {e}")

# Test it
if __name__ == "__main__":
    speak("Hello Boss. Main aagayi hu. Kya karungi aaj?")
