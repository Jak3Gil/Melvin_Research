#!/bin/bash
# Check investigation progress

echo "=== Investigation Process Status ==="
ps aux | grep deep_investigation | grep -v grep
echo ""
echo "=== Log File Status ==="
ls -lh deep_investigation.log 2>/dev/null || echo "Log file not found"
wc -l deep_investigation.log 2>/dev/null || echo "0 lines"
echo ""
echo "=== Last 50 lines of log (if any) ==="
tail -50 deep_investigation.log 2>/dev/null || echo "Log file is empty or not accessible"
echo ""
echo "=== Checking for other log files ==="
ls -lh *.log 2>/dev/null | head -10

