#!/bin/bash
# Start camera server with better error handling

cd ~
pkill -f simple_video_server 2>/dev/null
sleep 1

echo "Starting camera server..."
python3 simple_video_server.py 8080 > /tmp/simple_server.log 2>&1 &
SERVER_PID=$!

sleep 2

if ps -p $SERVER_PID > /dev/null; then
    echo "Server started successfully (PID: $SERVER_PID)"
    echo "Server log:"
    tail -5 /tmp/simple_server.log
    echo ""
    echo "Test connection:"
    curl -s -m 2 http://localhost:8080/ > /dev/null && echo "✓ Server responding locally" || echo "✗ Server not responding locally"
else
    echo "Server failed to start!"
    cat /tmp/simple_server.log
    exit 1
fi

