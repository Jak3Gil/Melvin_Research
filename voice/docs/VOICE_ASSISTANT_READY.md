# Voice Assistant - Ready to Use! ✓

## Summary

Your Jetson now has a **complete local voice assistant** with:

✅ **Whisper** (Speech-to-Text) - Converts your voice to text  
✅ **Ollama** (Large Language Model) - Generates intelligent responses  
✅ **Piper** (Text-to-Speech) - Speaks responses back to you  

**Everything runs locally on the Jetson** - no cloud, no internet required!

## What's Installed

| Component | Status | Model | Size |
|-----------|--------|-------|------|
| **Piper TTS** | ✓ Installed | en_US-lessac-medium | ~62 MB |
| **Whisper STT** | ✓ Installed | base | ~140 MB |
| **Ollama LLM** | ✓ Installed | llama3.2:1b | ~1.3 GB |
| **PyAudio** | ✓ Installed | - | - |

## Quick Start

### Option 1: Demo (No Microphone Needed)

Test the LLM + TTS pipeline:

```bash
ssh melvin@192.168.1.119
bash demo_voice_assistant.sh
```

This will:
1. Ask the LLM "What is 2 plus 2?"
2. Convert the response to speech
3. Play it through your speakers

### Option 2: Full Voice Assistant (Requires Microphone)

Interactive voice assistant with STT:

```bash
ssh melvin@192.168.1.119
python3 voice_assistant_jetson.py
```

Usage:
1. Press **ENTER** to start recording
2. Speak your question (5 seconds)
3. Wait for the assistant to respond
4. Press **ENTER** to ask another question
5. Type **q** to quit

### Option 3: Test Individual Components

**Test Whisper (Speech-to-Text):**
```bash
python3 test_whisper_jetson.py
```

**Test Ollama (LLM):**
```bash
bash test_ollama_jetson.sh
# Or interactive:
ollama run llama3.2:1b
```

**Test Piper (Text-to-Speech):**
```bash
bash test_hello_jetson.sh
```

## How It Works

```
┌─────────────────────────────────────────────────┐
│           VOICE ASSISTANT PIPELINE              │
└─────────────────────────────────────────────────┘

1. 🎤 LISTEN
   └─> Record audio from USB microphone (5 seconds)

2. 📝 TRANSCRIBE (Whisper)
   └─> Convert speech to text
   └─> Time: ~2-3 seconds

3. 🤖 THINK (Ollama)
   └─> Generate intelligent response
   └─> Model: llama3.2:1b (1.3GB)
   └─> Time: ~3-5 seconds

4. 🔊 SPEAK (Piper)
   └─> Convert text to speech
   └─> Voice: Male (Lessac)
   └─> Time: ~1 second

5. 🔈 PLAY
   └─> Output through USB speakers

Total Time: ~6-9 seconds per interaction
```

## Files on Jetson

All scripts are in `/home/melvin/`:

```
/home/melvin/
├── voice_assistant_jetson.py          # Main voice assistant
├── test_whisper_jetson.py             # Test STT
├── test_ollama_jetson.sh              # Test LLM
├── test_hello_jetson.sh               # Test TTS
├── demo_voice_assistant.sh            # Demo without mic
├── check_voice_assistant.sh           # Check dependencies
├── download_whisper_model.py          # Download Whisper model
└── VOICE_ASSISTANT_SETUP.md           # Full documentation
```

## Example Interactions

### Example 1: Simple Question
```
You: "What is the capital of France?"
Melvin: "The capital of France is Paris."
```

### Example 2: Math
```
You: "What is 15 times 7?"
Melvin: "15 times 7 equals 105."
```

### Example 3: General Knowledge
```
You: "Tell me about robots"
Melvin: "Robots are machines designed to perform tasks automatically..."
```

## Configuration

### Change Recording Duration

Edit `voice_assistant_jetson.py`:
```python
self.record_seconds = 10  # Change from 5 to 10 seconds
```

### Use Better Whisper Model

For improved accuracy (slower):
```python
self.whisper_model = "small"  # Options: tiny, base, small, medium
```

### Use Larger LLM

For better responses (requires more RAM):
```bash
ollama pull llama3.2:3b
```

Then edit `voice_assistant_jetson.py`:
```python
self.ollama_model = "llama3.2:3b"
```

### Change Voice

Female voice:
```python
self.piper_model = "/home/melvin/piper/models/en_US-amy-medium.onnx"
```

## Performance

On Jetson AGX Orin:

| Component | Time | Memory |
|-----------|------|--------|
| Whisper (base) | ~2-3s | ~500MB |
| Ollama (1b) | ~3-5s | ~1.5GB |
| Piper (medium) | ~1s | ~200MB |
| **Total** | **~6-9s** | **~2.2GB** |

## Troubleshooting

### No audio output?
```bash
# Check audio devices
aplay -l

# Test audio
aplay /usr/share/sounds/alsa/Front_Center.wav
```

### Ollama not responding?
```bash
# Check if running
pgrep ollama

# Restart if needed
pkill ollama
ollama serve &
```

### Whisper too slow?
Use a smaller model:
```python
self.whisper_model = "tiny"  # Fastest option
```

## Next Steps

1. ✅ **Test the demo** - Run `demo_voice_assistant.sh`
2. ✅ **Try the full assistant** - Run `voice_assistant_jetson.py`
3. 🔄 **Customize** - Adjust models and settings
4. 🤖 **Integrate with Melvin** - Add motor control commands
5. 🎯 **Add wake word** - Use OpenWakeWord for hands-free activation

## Integration Ideas

### Control Motors with Voice

Add voice commands to control Melvin's motors:

```python
def process_command(text):
    text = text.lower()
    
    if "move forward" in text:
        # Send CAN command to move forward
        return "Moving forward"
    
    elif "turn left" in text:
        # Send CAN command to turn left
        return "Turning left"
    
    elif "stop" in text:
        # Send CAN command to stop
        return "Stopping"
    
    else:
        # Use LLM for general conversation
        return get_llm_response(text)
```

### Wake Word Detection

Add "Hey Melvin" wake word:

```bash
pip3 install openwakeword
```

### Continuous Listening

Modify to listen continuously instead of manual activation.

## Resources

- **Full Documentation**: `VOICE_ASSISTANT_SETUP.md`
- **Whisper**: https://github.com/openai/whisper
- **Ollama**: https://ollama.ai
- **Piper**: https://github.com/rhasspy/piper

## Summary

🎉 **Your voice assistant is ready!**

The system combines three powerful AI models running entirely on your Jetson:
- **Whisper** understands your speech
- **Ollama** generates intelligent responses
- **Piper** speaks back to you

All processing happens locally for:
- ✓ Privacy (no data sent to cloud)
- ✓ Low latency (fast responses)
- ✓ Offline operation (no internet needed)

**Try it now:**
```bash
ssh melvin@192.168.1.119
bash demo_voice_assistant.sh
```

---

**Setup Date**: January 2026  
**Tested On**: NVIDIA Jetson AGX Orin  
**Status**: ✅ All components installed and working

