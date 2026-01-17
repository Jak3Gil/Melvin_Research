# Piper TTS Setup on Jetson

## Installation Status

✅ **Piper TTS is successfully installed on your Jetson!**

- **Location**: `/home/melvin/piper/piper/piper`
- **Version**: 1.2.0
- **Platform**: ARM64 (NVIDIA Jetson)

## Quick Start

### Add to PATH

Add this line to your `~/.bashrc` (already done):
```bash
export PATH="$PATH:/home/melvin/piper"
```

Then reload your shell:
```bash
source ~/.bashrc
```

Or use the full path: `/home/melvin/piper/piper/piper`

## Download Voice Models

Voice models are available from the [Piper Voices repository](https://huggingface.co/rhasspy/piper-voices).

### Example: Download English (US) - Amy (Medium quality)

```bash
cd ~/piper/models
wget https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/amy/medium/en_US-amy-medium.onnx
wget https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/amy/medium/en_US-amy-medium.onnx.json
```

### Browse Available Voices

Visit: https://huggingface.co/rhasspy/piper-voices/tree/main

Choose your language and voice, then download both the `.onnx` model file and `.onnx.json` configuration file.

## Usage

### Basic Text-to-Speech

```bash
echo "Hello, this is a test of Piper TTS" | piper --model ~/piper/models/en_US-amy-medium.onnx --output_file output.wav
```

### Play Audio

```bash
aplay output.wav
# or
paplay output.wav
```

### Using with File Input

```bash
piper --model ~/piper/models/en_US-amy-medium.onnx --input_file text.txt --output_file speech.wav
```

### List Available Voices (if you have multiple)

```bash
ls ~/piper/models/
```

## Python Integration

You can also use Piper from Python using subprocess:

```python
import subprocess

text = "Hello from Python and Piper TTS"
model_path = "/home/melvin/piper/models/en_US-amy-medium.onnx"
output_file = "output.wav"

process = subprocess.Popen(
    ['piper', '--model', model_path, '--output_file', output_file],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE
)

stdout, stderr = process.communicate(input=text.encode())
```

## Integration with Melvin_november

Based on the [Melvin_november repository](https://github.com/Jak3Gil/Melvin_november), you can integrate Piper TTS into your Melvin system by:

1. Creating an EXECUTABLE node that calls Piper
2. Using the event-driven system to trigger speech output
3. Connecting sensor inputs or graph patterns to TTS output

### Example Integration

```c
// In your Melvin EXECUTABLE node code
void speak_text(MelvinFile *g, uint64_t node_id) {
    const char *text = "Hello from Melvin";
    system("echo 'Hello from Melvin' | piper --model /home/melvin/piper/models/en_US-amy-medium.onnx --output_file /tmp/speech.wav && aplay /tmp/speech.wav");
}
```

## Troubleshooting

### Permission Denied

If you get permission errors:
```bash
chmod +x /home/melvin/piper/piper/piper
```

### Audio Output Issues

If audio doesn't work, check your audio system:
```bash
# Check audio devices
aplay -l

# Test audio
speaker-test -t sine -f 1000 -l 1
```

### Model Not Found

Make sure you've downloaded both the `.onnx` and `.onnx.json` files for your voice model.

## Resources

- **Piper GitHub**: https://github.com/rhasspy/piper
- **Piper Voices**: https://huggingface.co/rhasspy/piper-voices
- **Melvin_november**: https://github.com/Jak3Gil/Melvin_november

