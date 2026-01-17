# Melvin Voice Assistant - Local STT + LLM + TTS Setup

This guide explains how to set up a fully local voice assistant on the NVIDIA Jetson that combines:
- **Whisper** (Speech-to-Text)
- **Ollama** (Large Language Model)
- **Piper** (Text-to-Speech)

All processing happens locally on the Jetson for privacy and low latency.

## Overview

The voice assistant workflow:
1. **Listen** → Record audio from USB microphone
2. **Transcribe** → Convert speech to text using Whisper
3. **Think** → Generate response using Ollama LLM
4. **Speak** → Convert response to speech using Piper
5. **Play** → Output audio through USB speakers

## System Requirements

### Hardware
- **NVIDIA Jetson** (AGX Orin, Orin Nano, Xavier, etc.)
- **RAM**: Minimum 8GB (16GB recommended for larger models)
- **Storage**: ~10GB free space for models
- **USB Microphone** (for audio input)
- **USB Speakers/Headphones** (for audio output)

### Software
- **Ubuntu 20.04** or later
- **Python 3.8+**
- **CUDA** (pre-installed on Jetson)

## Installation

### Quick Install (Recommended)

Upload and run the installation script on the Jetson:

```bash
# From your PC
scp install_voice_assistant_jetson.sh melvin@192.168.1.119:~/

# On the Jetson
ssh melvin@192.168.1.119
chmod +x install_voice_assistant_jetson.sh
bash install_voice_assistant_jetson.sh
```

This will install:
- Whisper (STT)
- Ollama (LLM)
- PyAudio (audio recording)
- Required dependencies
- Download necessary models

### Manual Installation

If you prefer to install components manually:

#### 1. Install Audio Dependencies

```bash
sudo apt-get update
sudo apt-get install -y portaudio19-dev python3-pyaudio ffmpeg alsa-utils
```

#### 2. Install Python Packages

```bash
pip3 install --upgrade pip
pip3 install pyaudio openai-whisper numpy scipy
```

#### 3. Install Ollama

```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

#### 4. Download LLM Model

```bash
# Lightweight model (1B parameters, ~1GB)
ollama pull llama3.2:1b

# Or larger model for better quality (3B parameters, ~2GB)
ollama pull llama3.2:3b
```

#### 5. Download Whisper Model

```bash
python3 << 'EOF'
import whisper
model = whisper.load_model("base")  # Downloads ~140MB model
print("Whisper model downloaded!")
EOF
```

#### 6. Verify Piper TTS

Piper should already be installed. Verify:

```bash
ls -lh ~/piper/piper/piper
ls -lh ~/piper/models/en_US-lessac-medium.onnx
```

If not installed, see `PIPER_TTS_MALE_VOICE_JETSON.md`.

## Testing Components

### Test Whisper (STT)

```bash
python3 test_whisper_jetson.py
```

This will:
- Record 5 seconds of audio
- Transcribe it using Whisper
- Display the transcribed text

### Test Ollama (LLM)

```bash
bash test_ollama_jetson.sh
```

Or test interactively:

```bash
ollama run llama3.2:1b "What is the capital of France?"
```

### Test Piper (TTS)

```bash
bash test_hello_jetson.sh
```

Or manually:

```bash
echo "Hello from Melvin" | \
    /home/melvin/piper/piper/piper \
    --model ~/piper/models/en_US-lessac-medium.onnx \
    --output_file /tmp/test.wav && \
    aplay -D plughw:0,0 /tmp/test.wav
```

## Running the Voice Assistant

### Upload the Voice Assistant Script

```bash
# From your PC
scp voice_assistant_jetson.py melvin@192.168.1.119:~/
```

### Run the Assistant

```bash
# On the Jetson
ssh melvin@192.168.1.119
python3 voice_assistant_jetson.py
```

### Usage

1. The assistant will check all dependencies
2. Press **ENTER** to start recording
3. Speak your question (5 seconds)
4. Wait for the assistant to:
   - Transcribe your speech
   - Generate a response
   - Speak the response
5. Press **ENTER** to ask another question
6. Type **q** and press ENTER to quit

### Example Interaction

```
> [Press ENTER]

🎤 Recording for 5 seconds...
   Speak now!
   Recording complete!

🔄 Converting speech to text...
   Transcribed: 'What is the weather like today?'

🤖 Getting LLM response...
   Response: 'I don't have access to real-time weather data...'

🔊 Converting text to speech...
   Audio generated, playing...
   Playback complete!

✓ Conversation cycle complete!
```

## Configuration

### Adjust Recording Duration

Edit `voice_assistant_jetson.py`:

```python
self.record_seconds = 10  # Change from 5 to 10 seconds
```

### Change Whisper Model

For better accuracy (but slower):

```python
self.whisper_model = "small"  # Options: tiny, base, small, medium, large
```

Model comparison:
- **tiny**: Fastest, least accurate (~39MB)
- **base**: Good balance (~140MB) ← Default
- **small**: Better accuracy (~460MB)
- **medium**: High accuracy (~1.5GB)
- **large**: Best accuracy (~3GB)

### Change LLM Model

For better responses (but requires more RAM):

```python
self.ollama_model = "llama3.2:3b"  # Larger model
```

Then download it:

```bash
ollama pull llama3.2:3b
```

Available models:
- **llama3.2:1b**: Lightweight, fast (~1GB RAM) ← Default
- **llama3.2:3b**: Better quality (~3GB RAM)
- **mistral:7b**: High quality (~7GB RAM)
- **llama3:8b**: Very high quality (~8GB RAM)

### Change Voice

To use a different Piper voice:

```python
self.piper_model = "/home/melvin/piper/models/en_US-amy-medium.onnx"  # Female voice
```

Download additional voices:

```bash
cd ~/piper/models

# Female voice (Amy)
wget https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/amy/medium/en_US-amy-medium.onnx
wget https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/amy/medium/en_US-amy-medium.onnx.json

# Alternative male voice (Ryan)
wget https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/ryan/medium/en_US-ryan-medium.onnx
wget https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/ryan/medium/en_US-ryan-medium.onnx.json
```

## Performance Optimization

### For Jetson Orin Nano (8GB)

Use lightweight models:
- Whisper: `tiny` or `base`
- Ollama: `llama3.2:1b`
- Piper: `medium` quality voices

### For Jetson AGX Orin (32GB+)

Use higher quality models:
- Whisper: `small` or `medium`
- Ollama: `llama3.2:3b` or `mistral:7b`
- Piper: `high` quality voices (if available)

### Reduce Latency

1. **Pre-load models**: Keep models in memory
2. **Reduce recording time**: Use 3-4 seconds instead of 5
3. **Use smaller models**: Trade quality for speed
4. **Optimize Ollama**: Set `OLLAMA_NUM_THREADS` environment variable

```bash
export OLLAMA_NUM_THREADS=4  # Adjust based on CPU cores
```

## Troubleshooting

### Issue: "No module named 'whisper'"

**Solution:**
```bash
pip3 install openai-whisper
```

### Issue: "Ollama command not found"

**Solution:**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

### Issue: "No USB audio device found"

**Solution:**
1. Check connected devices: `aplay -l` and `arecord -l`
2. Verify USB microphone is connected
3. Test recording: `arecord -d 5 test.wav && aplay test.wav`

### Issue: "Whisper is too slow"

**Solution:**
- Use a smaller model: `whisper_model = "tiny"`
- Reduce recording duration
- Close other applications

### Issue: "Out of memory"

**Solution:**
- Use smaller models (llama3.2:1b, whisper tiny)
- Close other applications
- Increase swap space:

```bash
sudo fallocate -l 8G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### Issue: "Ollama response timeout"

**Solution:**
- Increase timeout in code: `timeout=60`
- Use a smaller model
- Check Ollama service: `ollama list`

## Advanced Features

### Wake Word Detection

Add wake word detection using OpenWakeWord:

```bash
pip3 install openwakeword
```

### Continuous Listening

Modify the script to continuously listen instead of manual activation.

### Multi-turn Conversations

Add conversation history to maintain context across multiple interactions.

### Custom System Prompts

Customize the LLM's personality:

```bash
ollama run llama3.2:1b "You are Melvin, a helpful robot assistant..."
```

## Integration with Melvin System

The voice assistant can be integrated with Melvin's event-driven system:

```python
# Example: Trigger motor movement from voice command
def process_command(text):
    if "move forward" in text.lower():
        # Send CAN command to motors
        pass
    elif "turn left" in text.lower():
        # Send CAN command to motors
        pass
```

## File Locations

```
/home/melvin/
├── voice_assistant_jetson.py          # Main voice assistant script
├── test_whisper_jetson.py             # Whisper test script
├── test_ollama_jetson.sh              # Ollama test script
├── test_hello_jetson.sh               # Piper test script
├── install_voice_assistant_jetson.sh  # Installation script
└── piper/
    ├── piper/piper                    # Piper binary
    └── models/
        └── en_US-lessac-medium.onnx   # Voice model
```

## Resources

- **Whisper**: https://github.com/openai/whisper
- **Ollama**: https://ollama.ai
- **Piper**: https://github.com/rhasspy/piper
- **Jetson AI Lab**: https://www.jetson-ai-lab.com
- **NVIDIA Riva**: https://docs.nvidia.com/deeplearning/riva/

## Performance Metrics

Typical performance on Jetson AGX Orin:

| Component | Model | Time | Memory |
|-----------|-------|------|--------|
| Whisper (STT) | base | ~2-3s | ~500MB |
| Ollama (LLM) | llama3.2:1b | ~3-5s | ~1.5GB |
| Piper (TTS) | medium | ~1s | ~200MB |
| **Total** | | **~6-9s** | **~2.2GB** |

## Next Steps

1. ✓ Install all components
2. ✓ Test each component individually
3. ✓ Run the integrated voice assistant
4. Add wake word detection
5. Integrate with Melvin's motor control
6. Add multi-turn conversation support
7. Create custom voice commands for robot control

---

**Last Updated**: January 2026  
**Tested On**: NVIDIA Jetson AGX Orin  
**Ubuntu Version**: 20.04.6 LTS

