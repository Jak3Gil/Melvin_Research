#!/usr/bin/env python3
"""
Melvin Voice Assistant - Local STT + LLM + TTS on Jetson
Combines:
- Whisper (STT) - Speech to Text
- Ollama (LLM) - Language Model for responses
- Piper (TTS) - Text to Speech

All running locally on the Jetson for privacy and low latency.
"""

import subprocess
import sys
import os
import tempfile
import time
import wave
import pyaudio
import numpy as np
import struct
from pathlib import Path

class VoiceAssistant:
    def __init__(self):
        # Piper TTS configuration
        self.piper_bin = "/home/melvin/piper/piper/piper"
        self.piper_model = "/home/melvin/piper/models/en_US-lessac-medium.onnx"
        
        # Whisper STT configuration (will be installed)
        self.whisper_model = "base"  # Options: tiny, base, small, medium, large
        
        # Ollama LLM configuration
        self.ollama_model = "llama3.2:1b"  # Lightweight model for Jetson
        
        # Audio configuration
        self.sample_rate = 16000
        self.channels = 1
        self.chunk_size = 1024
        self.record_seconds = 5
        
        # USB audio device
        self.usb_device = "plughw:0,0"
        
    def check_dependencies(self):
        """Check if all required components are installed."""
        print("Checking dependencies...")
        print("=" * 50)
        
        # Check Piper
        if os.path.exists(self.piper_bin) and os.path.exists(self.piper_model):
            print("✓ Piper TTS: Installed")
        else:
            print("✗ Piper TTS: Not found")
            print(f"  Binary: {self.piper_bin}")
            print(f"  Model: {self.piper_model}")
            return False
        
        # Check Whisper
        try:
            import whisper
            print("✓ Whisper STT: Installed")
        except ImportError:
            print("✗ Whisper STT: Not installed")
            print("  Run: pip3 install openai-whisper")
            return False
        
        # Check Ollama
        try:
            result = subprocess.run(
                ["ollama", "list"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                print("✓ Ollama LLM: Installed")
                if self.ollama_model in result.stdout:
                    print(f"  ✓ Model '{self.ollama_model}' available")
                else:
                    print(f"  ⚠ Model '{self.ollama_model}' not found")
                    print(f"  Run: ollama pull {self.ollama_model}")
            else:
                print("✗ Ollama LLM: Not running")
                return False
        except (subprocess.TimeoutExpired, FileNotFoundError):
            print("✗ Ollama LLM: Not installed")
            print("  Install from: https://ollama.ai")
            return False
        
        # Check PyAudio
        try:
            import pyaudio
            print("✓ PyAudio: Installed")
        except ImportError:
            print("✗ PyAudio: Not installed")
            print("  Run: pip3 install pyaudio")
            return False
        
        print("=" * 50)
        return True
    
    def record_audio(self, duration=None):
        """Record audio from microphone."""
        if duration is None:
            duration = self.record_seconds
        
        print(f"\n🎤 Recording for {duration} seconds...")
        print("   Speak now!")
        
        audio = pyaudio.PyAudio()
        
        # Find USB audio input device
        input_device_index = None
        device_info = None
        for i in range(audio.get_device_count()):
            info = audio.get_device_info_by_index(i)
            if "USB" in info['name'] and info['maxInputChannels'] > 0:
                input_device_index = i
                device_info = info
                print(f"   Using input device: {info['name']}")
                break
        
        # Try different sample rates until one works
        # Whisper works best with 16000 Hz, but we'll record at device rate and resample if needed
        preferred_rates = [44100, 48000, 16000, 22050, 32000]
        sample_rate = None
        stream = None
        
        for rate in preferred_rates:
            try:
                stream = audio.open(
                    format=pyaudio.paInt16,
                    channels=self.channels,
                    rate=rate,
                    input=True,
                    input_device_index=input_device_index,
                    frames_per_buffer=self.chunk_size
                )
                sample_rate = rate
                print(f"   Using sample rate: {rate} Hz")
                break
            except Exception as e:
                continue
        
        if stream is None:
            print("   Error: Could not open audio stream with any sample rate")
            audio.terminate()
            return None
        
        frames = []
        max_level = 0
        total_chunks = int(sample_rate / self.chunk_size * duration)
        
        for i in range(0, total_chunks):
            data = stream.read(self.chunk_size)
            frames.append(data)
            
            # Check audio level
            samples = struct.unpack(f'<{len(data)//2}h', data)
            chunk_max = max(abs(s) for s in samples)
            max_level = max(max_level, chunk_max)
            
            # Show progress every 10 chunks
            if i % 10 == 0:
                level_bars = int(chunk_max / 32767 * 20)
                level_display = '█' * level_bars + '░' * (20 - level_bars)
                print(f"\r   [{level_display}] {i*100//total_chunks}%", end='', flush=True)
        
        print(f"\n   Recording complete! Max audio level: {max_level}/32767")
        
        if max_level < 100:
            print("   ⚠ WARNING: Audio level is very low - microphone may not be working!")
        elif max_level < 1000:
            print("   ⚠ Audio level is low - speak louder or check microphone")
        
        stream.stop_stream()
        stream.close()
        audio.terminate()
        
        # Save to temporary WAV file
        temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
        wf = wave.open(temp_file.name, 'wb')
        wf.setnchannels(self.channels)
        wf.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
        wf.setframerate(sample_rate)
        wf.writeframes(b''.join(frames))
        wf.close()
        
        # If we recorded at a different rate than Whisper expects, resample
        if sample_rate != 16000:
            print(f"   Resampling from {sample_rate} Hz to 16000 Hz for Whisper...")
            resampled_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
            resampled_file.close()  # Close so ffmpeg can write to it
            
            # Use ffmpeg to resample
            result = subprocess.run(
                ['ffmpeg', '-i', temp_file.name, '-ar', '16000', '-y', resampled_file.name],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            
            if result.returncode == 0 and os.path.exists(resampled_file.name):
                os.unlink(temp_file.name)  # Delete original
                temp_file.name = resampled_file.name
                print(f"   Resampled successfully to 16000 Hz")
            else:
                print(f"   Warning: Could not resample, Whisper may work with {sample_rate} Hz")
        
        return temp_file.name
    
    def speech_to_text(self, audio_file):
        """Convert speech to text using Whisper."""
        print("\n🔄 Converting speech to text...")
        
        # Check if audio file exists and has content
        if not os.path.exists(audio_file):
            print(f"   Error: Audio file not found: {audio_file}")
            return None
        
        file_size = os.path.getsize(audio_file)
        if file_size < 1000:  # Less than 1KB is probably empty
            print(f"   Warning: Audio file is very small ({file_size} bytes), may be silent")
            # Save for debugging
            debug_file = f"/tmp/debug_audio_{int(time.time())}.wav"
            os.system(f"cp {audio_file} {debug_file}")
            print(f"   Saved debug copy to: {debug_file}")
        
        try:
            import whisper
            
            # Load Whisper model (cache it to avoid reloading every time)
            if not hasattr(self, '_whisper_model'):
                print("   Loading Whisper model (first time, may take a moment)...")
                self._whisper_model = whisper.load_model(self.whisper_model)
            
            # Transcribe
            print("   Transcribing audio...")
            result = self._whisper_model.transcribe(
                audio_file,
                language="en",  # Specify English for better accuracy
                fp16=False  # Use FP32 on CPU
            )
            text = result["text"].strip()
            
            # Check if we got any text
            if not text:
                print("   Warning: Whisper returned empty transcription")
                print(f"   Audio file: {audio_file} ({file_size} bytes)")
                # Check audio levels
                try:
                    with wave.open(audio_file, 'rb') as wf:
                        frames = wf.readframes(wf.getnframes())
                        samples = struct.unpack(f'<{len(frames)//2}h', frames)
                        max_amplitude = max(abs(s) for s in samples)
                        print(f"   Max audio amplitude: {max_amplitude} (32767 is max)")
                        if max_amplitude < 100:
                            print("   ⚠ Audio level is very low - microphone may not be picking up sound")
                except:
                    pass
            
            print(f"   Transcribed: '{text}'")
            return text if text else None
        
        except Exception as e:
            print(f"   Error: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def get_llm_response(self, text):
        """Get response from LLM using Ollama."""
        print("\n🤖 Getting LLM response...")
        
        try:
            result = subprocess.run(
                ["ollama", "run", self.ollama_model, text],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                response = result.stdout.strip()
                print(f"   Response: '{response[:100]}...'")
                return response
            else:
                print(f"   Error: {result.stderr}")
                return None
        
        except subprocess.TimeoutExpired:
            print("   Timeout waiting for LLM response")
            return None
        except Exception as e:
            print(f"   Error: {e}")
            return None
    
    def text_to_speech(self, text):
        """Convert text to speech using Piper and play it."""
        print("\n🔊 Converting text to speech...")
        
        try:
            # Generate audio file
            temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
            
            # Run Piper
            process = subprocess.Popen(
                [self.piper_bin, '--model', self.piper_model, '--output_file', temp_file.name],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            stdout, stderr = process.communicate(input=text.encode())
            
            if process.returncode == 0:
                print("   Audio generated, playing...")
                
                # Play audio
                subprocess.run(
                    ['aplay', '-D', self.usb_device, temp_file.name],
                    capture_output=True
                )
                
                print("   Playback complete!")
                
                # Clean up
                os.unlink(temp_file.name)
                return True
            else:
                print(f"   Error generating audio: {stderr.decode()}")
                return False
        
        except Exception as e:
            print(f"   Error: {e}")
            return False
    
    def run_conversation(self):
        """Run a single conversation cycle."""
        print("\n" + "=" * 50)
        print("VOICE ASSISTANT - Conversation Cycle")
        print("=" * 50)
        
        # Step 1: Record audio
        audio_file = self.record_audio()
        
        if not audio_file:
            print("\n❌ Could not record audio")
            return False
        
        # Step 2: Speech to Text
        text = self.speech_to_text(audio_file)
        if audio_file and os.path.exists(audio_file):
            os.unlink(audio_file)  # Clean up
        
        if not text:
            print("\n❌ Could not understand speech")
            return False
        
        # Step 3: Get LLM response
        response = self.get_llm_response(text)
        
        if not response:
            print("\n❌ Could not get LLM response")
            return False
        
        # Step 4: Text to Speech
        success = self.text_to_speech(response)
        
        if not success:
            print("\n❌ Could not generate speech")
            return False
        
        print("\n✓ Conversation cycle complete!")
        return True
    
    def run_interactive(self):
        """Run interactive voice assistant loop."""
        print("\n" + "=" * 50)
        print("MELVIN VOICE ASSISTANT")
        print("=" * 50)
        print("\nPress ENTER to start recording, or 'q' to quit")
        
        while True:
            user_input = input("\n> ")
            
            if user_input.lower() in ['q', 'quit', 'exit']:
                print("\nGoodbye!")
                break
            
            self.run_conversation()

def main():
    """Main entry point."""
    assistant = VoiceAssistant()
    
    # Check dependencies
    if not assistant.check_dependencies():
        print("\n❌ Missing dependencies. Please install them first.")
        sys.exit(1)
    
    print("\n✓ All dependencies installed!")
    
    # Run interactive mode
    try:
        assistant.run_interactive()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user. Goodbye!")
        sys.exit(0)

if __name__ == "__main__":
    main()

