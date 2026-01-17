#!/usr/bin/env python3
"""
Test USB microphone on Jetson
Checks audio levels and helps diagnose microphone issues
"""

import pyaudio
import struct
import wave
import sys

def test_microphone():
    print("=" * 50)
    print("USB Microphone Test")
    print("=" * 50)
    print()
    
    audio = pyaudio.PyAudio()
    
    # Find USB audio input device
    print("Available audio input devices:")
    input_device_index = None
    device_info = None
    
    for i in range(audio.get_device_count()):
        info = audio.get_device_info_by_index(i)
        if info['maxInputChannels'] > 0:
            marker = " ← USB" if "USB" in info['name'] else ""
            print(f"  [{i}] {info['name']} (channels: {info['maxInputChannels']}, rate: {int(info.get('defaultSampleRate', 44100))}){marker}")
            if "USB" in info['name'] and input_device_index is None:
                input_device_index = i
                device_info = info
    
    print()
    
    if input_device_index is None:
        print("❌ No USB audio input device found!")
        audio.terminate()
        return False
    
    print(f"✓ Using device: {device_info['name']}")
    print()
    
    # Try different sample rates
    sample_rates = [44100, 48000, 16000, 22050, 32000]
    working_rate = None
    stream = None
    
    print("Testing sample rates...")
    for rate in sample_rates:
        try:
            test_stream = audio.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=rate,
                input=True,
                input_device_index=input_device_index,
                frames_per_buffer=1024
            )
            test_stream.stop_stream()
            test_stream.close()
            working_rate = rate
            print(f"  ✓ {rate} Hz - OK")
        except Exception as e:
            print(f"  ✗ {rate} Hz - Failed")
    
    if working_rate is None:
        print("❌ Could not find a working sample rate!")
        audio.terminate()
        return False
    
    print(f"\n✓ Using sample rate: {working_rate} Hz")
    print()
    
    # Record and test audio levels
    print("Recording 3 seconds of audio...")
    print("SPEAK LOUDLY into the microphone!")
    print()
    
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = working_rate
    RECORD_SECONDS = 3
    
    stream = audio.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        input=True,
        input_device_index=input_device_index,
        frames_per_buffer=CHUNK
    )
    
    frames = []
    max_level = 0
    min_level = 32767
    total_chunks = int(RATE / CHUNK * RECORD_SECONDS)
    
    print("Recording...")
    for i in range(0, total_chunks):
        data = stream.read(CHUNK)
        frames.append(data)
        
        # Check audio level
        samples = struct.unpack(f'<{len(data)//2}h', data)
        chunk_max = max(abs(s) for s in samples)
        chunk_min = min(abs(s) for s in samples)
        max_level = max(max_level, chunk_max)
        min_level = min(min_level, chunk_min)
        
        # Show progress
        if i % 5 == 0:
            level_bars = int(chunk_max / 32767 * 30)
            level_display = '█' * level_bars + '░' * (30 - level_bars)
            print(f"\r  [{level_display}] {chunk_max:5d}/32767", end='', flush=True)
    
    print("\n")
    
    stream.stop_stream()
    stream.close()
    audio.terminate()
    
    # Analyze results
    print("=" * 50)
    print("RESULTS")
    print("=" * 50)
    print(f"Max audio level: {max_level}/32767 ({max_level*100//32767}%)")
    print(f"Min audio level: {min_level}/32767")
    print()
    
    # Save test file
    test_file = "/tmp/mic_test.wav"
    wf = wave.open(test_file, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(audio.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()
    print(f"Test recording saved to: {test_file}")
    print()
    
    # Recommendations
    if max_level < 100:
        print("❌ PROBLEM: Audio level is extremely low!")
        print()
        print("Possible causes:")
        print("  1. Microphone is muted or volume is too low")
        print("  2. Microphone is not connected properly")
        print("  3. Wrong microphone selected")
        print("  4. USB audio device needs volume adjustment")
        print()
        print("Solutions:")
        print("  1. Check microphone volume:")
        print("     alsamixer")
        print("     (Press F4 to see capture devices, adjust 'Capture' volume)")
        print()
        print("  2. Test with arecord:")
        print("     arecord -D plughw:0,0 -d 3 -f cd test.wav")
        print("     aplay test.wav")
        print()
        print("  3. Check USB device:")
        print("     lsusb | grep -i audio")
        print()
        return False
    
    elif max_level < 1000:
        print("⚠ WARNING: Audio level is low")
        print()
        print("Recommendations:")
        print("  1. Increase microphone volume:")
        print("     alsamixer")
        print("     (Press F4, increase 'Capture' volume)")
        print()
        print("  2. Speak louder or move closer to microphone")
        print()
        return True
    
    elif max_level < 5000:
        print("✓ Audio level is acceptable but could be better")
        print()
        print("For best results, try increasing microphone volume:")
        print("  alsamixer")
        print()
        return True
    
    else:
        print("✓ Audio level is good!")
        print()
        return True

if __name__ == "__main__":
    try:
        success = test_microphone()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest cancelled")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

