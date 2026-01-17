#!/usr/bin/env python3
"""
Test Whisper STT on Jetson
Records audio and transcribes it using OpenAI Whisper
"""

import subprocess
import sys
import os
import tempfile
import wave
import time

def test_whisper_simple():
    """Test Whisper with a simple audio recording."""
    print("=" * 50)
    print("Testing Whisper STT on Jetson")
    print("=" * 50)
    print()
    
    # Check if Whisper is installed
    try:
        import whisper
        print("✓ Whisper is installed")
    except ImportError:
        print("✗ Whisper is not installed")
        print("  Run: pip3 install openai-whisper")
        sys.exit(1)
    
    # Check PyAudio
    try:
        import pyaudio
        print("✓ PyAudio is installed")
    except ImportError:
        print("✗ PyAudio is not installed")
        print("  Run: pip3 install pyaudio")
        sys.exit(1)
    
    print()
    print("Recording 5 seconds of audio...")
    print("Speak now: 'Hello, this is a test'")
    print()
    
    # Record audio
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000
    RECORD_SECONDS = 5
    
    p = pyaudio.PyAudio()
    
    # Find USB audio input device
    input_device_index = None
    print("Available audio input devices:")
    for i in range(p.get_device_count()):
        info = p.get_device_info_by_index(i)
        if info['maxInputChannels'] > 0:
            print(f"  [{i}] {info['name']} (channels: {info['maxInputChannels']})")
            if "USB" in info['name']:
                input_device_index = i
                print(f"      ^ Using this device")
    
    if input_device_index is None:
        print("\n⚠ No USB audio device found, using default")
    
    print()
    print("🎤 Recording...")
    
    stream = p.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        input=True,
        input_device_index=input_device_index,
        frames_per_buffer=CHUNK
    )
    
    frames = []
    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)
        if i % 10 == 0:
            print(".", end="", flush=True)
    
    print("\n✓ Recording complete!")
    
    stream.stop_stream()
    stream.close()
    p.terminate()
    
    # Save to temporary file
    temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
    wf = wave.open(temp_file.name, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()
    
    print(f"\nAudio saved to: {temp_file.name}")
    print()
    
    # Transcribe with Whisper
    print("🔄 Transcribing with Whisper...")
    print("   Loading model (this may take a moment)...")
    
    start_time = time.time()
    model = whisper.load_model("base")
    load_time = time.time() - start_time
    print(f"   Model loaded in {load_time:.2f} seconds")
    
    print("   Transcribing...")
    start_time = time.time()
    result = model.transcribe(temp_file.name)
    transcribe_time = time.time() - start_time
    
    print()
    print("=" * 50)
    print("RESULTS")
    print("=" * 50)
    print(f"Transcribed text: {result['text']}")
    print(f"Language detected: {result['language']}")
    print(f"Transcription time: {transcribe_time:.2f} seconds")
    print("=" * 50)
    
    # Clean up
    os.unlink(temp_file.name)
    
    print()
    print("✓ Whisper test complete!")

if __name__ == "__main__":
    try:
        test_whisper_simple()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

