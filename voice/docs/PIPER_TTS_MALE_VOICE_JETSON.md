# Piper TTS Male Voice Setup on Jetson

This document explains how to install and use the **male Lessac voice** (`en_US-lessac-medium.onnx`) for Piper TTS on NVIDIA Jetson devices.

## Overview

- **Voice Model**: `en_US-lessac-medium.onnx` (Lessac - Male voice)
- **Platform**: NVIDIA Jetson (ARM64/ARMv8)
- **Quality**: Medium (good balance of quality and performance)
- **Language**: English (US)

## Prerequisites

Before installing the voice model, ensure you have:

1. ✅ **Piper TTS Binary installed** on your Jetson
   - Location: `/home/melvin/piper/piper/piper`
   - See `PIPER_TTS_SETUP.md` for installation instructions

2. ✅ **Audio output configured**
   - USB headphones/audio device detected
   - Audio device verified with `aplay -l`

## Installation Steps

### Step 1: Connect to Jetson

```bash
ssh melvin@192.168.1.119
# Password: 123456
```

### Step 2: Navigate to Models Directory

```bash
cd ~/piper/models
```

If the directory doesn't exist, create it:

```bash
mkdir -p ~/piper/models
cd ~/piper/models
```

### Step 3: Download the Male Voice Model

Download both the `.onnx` model file and the `.onnx.json` configuration file:

```bash
# Download the model file (~61.7 MB)
wget https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx

# Download the configuration file
wget https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx.json
```

**Download with progress indicator:**

```bash
wget --progress=bar:force https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx
wget --progress=bar:force https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx.json
```

### Step 4: Verify Download

Check that both files are present:

```bash
ls -lh ~/piper/models/en_US-lessac-medium.*
```

You should see:
```
en_US-lessac-medium.onnx       (~62 MB)
en_US-lessac-medium.onnx.json  (~600 bytes)
```

## Testing the Male Voice

### Test 1: Generate and Play Audio

```bash
echo "Hello, this is a test of the male Lessac voice on the Jetson." | \
    /home/melvin/piper/piper/piper \
    --model ~/piper/models/en_US-lessac-medium.onnx \
    --output_file ~/test_male_voice.wav && \
    aplay ~/test_male_voice.wav
```

### Test 2: Use USB Headphones Directly

First, identify your USB audio device:

```bash
aplay -l
```

Look for your USB audio device (usually card 0):

```
card 0: Audio [AB13X USB Audio], device 0: USB Audio [USB Audio]
```

Then play audio to USB headphones:

```bash
echo "Testing male voice on USB headphones" | \
    /home/melvin/piper/piper/piper \
    --model ~/piper/models/en_US-lessac-medium.onnx \
    --output_file ~/test_usb.wav && \
    aplay -D plughw:0,0 ~/test_usb.wav
```

## Usage Examples

### Basic Text-to-Speech

```bash
echo "Your text here" | \
    /home/melvin/piper/piper/piper \
    --model ~/piper/models/en_US-lessac-medium.onnx \
    --output_file output.wav && \
    aplay output.wav
```

### From a Text File

```bash
# Create a text file
echo "This is a longer text that will be converted to speech using the male voice." > text.txt

# Generate speech
/home/melvin/piper/piper/piper \
    --model ~/piper/models/en_US-lessac-medium.onnx \
    --input_file text.txt \
    --output_file speech.wav

# Play the audio
aplay speech.wav
```

### Python Script Example

Create a Python script to use the male voice:

```python
#!/usr/bin/env python3
import subprocess
import sys

def speak_with_male_voice(text, output_file="output.wav"):
    """Generate speech using the male Lessac voice."""
    model_path = "/home/melvin/piper/models/en_US-lessac-medium.onnx"
    piper_bin = "/home/melvin/piper/piper/piper"
    
    process = subprocess.Popen(
        [piper_bin, '--model', model_path, '--output_file', output_file],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    stdout, stderr = process.communicate(input=text.encode())
    
    if process.returncode == 0:
        print(f"Audio generated: {output_file}")
        # Play the audio
        subprocess.run(['aplay', output_file])
    else:
        print(f"Error: {stderr.decode()}", file=sys.stderr)

if __name__ == "__main__":
    text = "Hello from the male Lessac voice on Jetson!"
    speak_with_male_voice(text)
```

Save as `speak_male.py` and run:

```bash
chmod +x speak_male.py
./speak_male.py
```

## Integration with Melvin System

Based on the [Melvin_november repository](https://github.com/Jak3Gil/Melvin_november), you can integrate the male voice into Melvin's event-driven system:

### C Integration Example

```c
#include <stdlib.h>
#include <stdio.h>

// Function to speak text using male voice
void speak_male_voice(const char *text) {
    char command[512];
    snprintf(command, sizeof(command),
        "echo '%s' | /home/melvin/piper/piper/piper "
        "--model /home/melvin/piper/models/en_US-lessac-medium.onnx "
        "--output_file /tmp/melvin_speech.wav && "
        "aplay /tmp/melvin_speech.wav",
        text);
    system(command);
}

// Example EXECUTABLE node that speaks
void melvin_speak_node(MelvinFile *g, uint64_t node_id) {
    const char *message = "Melvin is speaking with a male voice";
    speak_male_voice(message);
}
```

## Voice Model Details

### Model Information

- **Voice Name**: Lessac
- **Gender**: Male
- **Language**: English (US)
- **Quality**: Medium
- **File Size**: ~61.7 MB
- **Format**: ONNX (Open Neural Network Exchange)
- **Sample Rate**: 22,050 Hz
- **Channels**: Mono

### Performance Metrics

From testing on Jetson:
- **Real-time Factor**: ~0.53 (faster than real-time)
- **Load Time**: ~0.6 seconds
- **Inference Speed**: ~5.2 seconds for ~10 seconds of audio
- **Audio Generation**: ~9.8 seconds of audio from ~5.2 seconds of processing

## Troubleshooting

### Issue: Voice model not found

**Error**: `Could not load model: ~/piper/models/en_US-lessac-medium.onnx`

**Solution**: 
1. Verify the file exists: `ls -lh ~/piper/models/en_US-lessac-medium.onnx`
2. Check file permissions: `chmod 644 ~/piper/models/en_US-lessac-medium.onnx`
3. Ensure both `.onnx` and `.onnx.json` files are present

### Issue: Audio not playing

**Error**: Audio file generated but no sound

**Solutions**:
1. Check audio devices: `aplay -l`
2. Test default audio: `aplay ~/test_male_voice.wav`
3. Try USB device specifically: `aplay -D plughw:0,0 ~/test_male_voice.wav`
4. Check volume: `alsamixer`

### Issue: ONNX Runtime warnings

**Warning**: `pthread_setaffinity_np failed`

**Solution**: These warnings are harmless on ARM processors. They're related to CPU affinity settings and don't affect functionality. You can safely ignore them.

### Issue: Slow generation

If voice generation is too slow:

1. Check CPU usage: `top` or `htop`
2. Close unnecessary processes
3. Consider using a "low" quality model instead of "medium" if available
4. Ensure Jetson is not in power-saving mode

## Available Male Voices

If you want to try other male voices, here are some alternatives:

### English (US) Male Voices

- **lessac**: `en_US-lessac-medium.onnx` (Currently installed)
- **ryan**: `en_US-ryan-medium.onnx` (Different male voice)
- **nicole**: `en_US-nicole-medium.onnx` (Can be male in some models)

### Download Other Male Voices

```bash
cd ~/piper/models

# Download Ryan (alternative male voice)
wget https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/ryan/medium/en_US-ryan-medium.onnx
wget https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/ryan/medium/en_US-ryan-medium.onnx.json
```

## File Locations Summary

```
/home/melvin/
├── piper/
│   ├── piper/
│   │   └── piper          # Piper TTS binary
│   └── models/
│       ├── en_US-lessac-medium.onnx      # Male voice model
│       ├── en_US-lessac-medium.onnx.json # Voice configuration
│       ├── en_US-amy-medium.onnx         # Female voice (if installed)
│       └── en_US-amy-medium.onnx.json    # Female voice config
└── test_male_tts.wav      # Test output file
```

## Quick Reference

### Generate Speech Command

```bash
echo "Text to speak" | \
    /home/melvin/piper/piper/piper \
    --model ~/piper/models/en_US-lessac-medium.onnx \
    --output_file output.wav && \
    aplay output.wav
```

### Play Audio to USB Headphones

```bash
aplay -D plughw:0,0 output.wav
```

### List Available Voices

```bash
ls ~/piper/models/*.onnx
```

### Check Voice Model Info

```bash
cat ~/piper/models/en_US-lessac-medium.onnx.json
```

## Resources

- **Piper TTS Repository**: https://github.com/rhasspy/piper
- **Voice Models**: https://huggingface.co/rhasspy/piper-voices
- **Lessac Voice**: https://huggingface.co/rhasspy/piper-voices/tree/main/en/en_US/lessac/medium
- **Melvin Repository**: https://github.com/Jak3Gil/Melvin_november
- **Jetson Documentation**: NVIDIA Jetson Developer Documentation

## Notes

- The male Lessac voice was tested and verified working on **NVIDIA Jetson AGX Orin** running **Ubuntu 20.04.6 LTS**
- Real-time factor of ~0.53 means it's faster than real-time (good for interactive applications)
- The voice works well for general-purpose text-to-speech applications
- Consider the "medium" quality a good balance between quality and file size

## Next Steps

1. ✅ Voice model installed and tested
2. Integrate with Melvin system via EXECUTABLE nodes
3. Create wrapper functions for easier usage
4. Set up automatic voice selection based on context
5. Consider downloading additional voices for variety

---

**Last Updated**: January 2026  
**Tested On**: NVIDIA Jetson AGX Orin (ARM64)  
**Ubuntu Version**: 20.04.6 LTS  
**Piper Version**: 1.2.0

