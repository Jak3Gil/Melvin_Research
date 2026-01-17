# Video Streaming Setup for USB Cameras

## Why Video Instead of JPEGs?

**Advantages of Video Streaming:**
- ✅ **Lower latency** - Continuous stream vs individual frame transfers
- ✅ **Better performance** - Encoded video uses less bandwidth than raw JPEGs
- ✅ **Smoother playback** - Proper frame timing and synchronization
- ✅ **Less overhead** - One connection instead of many SCP transfers
- ✅ **Standard protocols** - Works with common video players (VLC, etc.)

## Current Setup

Video streams are now running using **UDP** protocol for low-latency streaming:

- **Camera 1**: `udp://@:5004`
- **Camera 2**: `udp://@:5005`

### Stream Specifications

- **Format**: MPEG-TS over UDP
- **Codec**: H.264 (libx264)
- **Resolution**: 1280x720 (720p)
- **Frame Rate**: 30 FPS
- **Encoding**: Ultrafast preset with zerolatency tuning (minimal delay)

## Viewing Methods

### Method 1: VLC Media Player (Recommended)

**Install VLC** (if not already installed):
- Download: https://www.videolan.org/vlc/
- Install the application

**Open Streams in VLC:**

1. Open VLC Media Player
2. Go to: **Media > Open Network Stream**
3. Enter the stream URL:
   - Camera 1: `udp://@:5004`
   - Camera 2: `udp://@:5005`
4. Click **Play**

**Or use command line:**
```powershell
# If VLC is in PATH
vlc udp://@:5004
vlc udp://@:5005

# Or with full path
& "C:\Program Files\VideoLAN\VLC\vlc.exe" udp://@:5004
```

### Method 2: PowerShell Script

Run the automated viewer script:
```powershell
.\view_cameras_video.ps1 -Method UDP
```

This will:
- Check if VLC is installed
- Automatically open both camera streams in VLC
- Display stream URLs if VLC is not found

### Method 3: HTTP Video Stream (Alternative)

If UDP doesn't work, we can use HTTP streaming:

```powershell
# Start HTTP video server on Jetson
ssh melvin@192.168.1.119 "python3 ~/camera_video_streamer.py 8080 &"

# View in browser or VLC
# Camera 1: http://192.168.1.119:8080/camera1
# Camera 2: http://192.168.1.119:8080/camera2
```

## Starting/Stopping Streams

### Start Video Streams

```powershell
ssh melvin@192.168.1.119 "~/start_video_streams.sh"
```

### Stop Video Streams

```powershell
ssh melvin@192.168.1.119 "pkill -f 'ffmpeg.*video'"
```

### Check if Streams are Running

```powershell
ssh melvin@192.168.1.119 "pgrep -f 'ffmpeg.*video'"
```

## Stream URLs Reference

### UDP Streams (Low Latency)
- Camera 1: `udp://@:5004`
- Camera 2: `udp://@:5005`

### HTTP Streams (If enabled)
- Camera 1: `http://192.168.1.119:8080/camera1`
- Camera 2: `http://192.168.1.119:8080/camera2`

### RTSP Streams (If enabled)
- Camera 1: `rtsp://192.168.1.119:8554/stream`
- Camera 2: `rtsp://192.168.1.119:8555/stream`

## Troubleshooting

### VLC Can't Connect to Stream

1. **Check if streams are running on Jetson:**
   ```bash
   ssh melvin@192.168.1.119 "pgrep -f 'ffmpeg.*video'"
   ```

2. **Check firewall settings:**
   ```bash
   ssh melvin@192.168.1.119 "sudo ufw status"
   ```
   UDP ports should be open (5004, 5005)

3. **Test network connectivity:**
   ```powershell
   Test-NetConnection -ComputerName 192.168.1.119 -Port 5004 -InformationLevel Detailed
   ```

4. **View stream logs:**
   ```bash
   ssh melvin@192.168.1.119 "cat /tmp/video_stream.log"
   ```

### Low Frame Rate or Lag

1. **Reduce resolution:**
   Edit `start_video_streams.sh` and change `-video_size 1280x720` to `-video_size 640x480`

2. **Reduce frame rate:**
   Change `-framerate 30` to `-framerate 15` or `-framerate 10`

3. **Check network bandwidth:**
   UDP streams require good network connection

### Stream Cuts Out

1. **Restart streams:**
   ```powershell
   ssh melvin@192.168.1.119 "pkill -f 'ffmpeg.*video'; sleep 1; ~/start_video_streams.sh &"
   ```

2. **Check camera devices:**
   ```bash
   ssh melvin@192.168.1.119 "ls -la /dev/video*"
   ```

## Comparison: Video vs JPEG Streaming

| Feature | Video Streaming | JPEG Streaming |
|---------|----------------|----------------|
| **Latency** | Low (~100-200ms) | Higher (~500-1000ms) |
| **Bandwidth** | Efficient (compressed) | Higher (full JPEGs) |
| **Smoothness** | Very smooth | Can be choppy |
| **Compatibility** | Works with VLC, players | Manual refresh needed |
| **Setup Complexity** | Moderate | Simple |
| **CPU Usage** | Higher (encoding) | Lower (no encoding) |

## Next Steps

1. **Install VLC** if not already installed
2. **Open streams** using `.\view_cameras_video.ps1`
3. **Adjust settings** in `start_video_streams.sh` if needed
4. **Integrate with Melvin** system for automated video processing

---

**Video streaming provides a much better experience than JPEG frame-by-frame transfer!**

