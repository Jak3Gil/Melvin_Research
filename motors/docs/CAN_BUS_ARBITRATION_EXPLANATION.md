# CAN Bus Arbitration - Why Motors 7, 9, 11 Don't Respond

## How CAN Bus Arbitration Works

### The Problem
CAN bus uses **non-destructive bitwise arbitration**. When multiple devices try to transmit simultaneously:

1. **Lower CAN ID = Higher Priority**
   - CAN ID 1 (binary: 00000000001) has **HIGHEST priority**
   - CAN ID 14 (binary: 00000001110) has **LOWER priority**
   - CAN ID 127 has **LOWEST priority**

2. **What Happens When Multiple Motors Respond:**
   ```
   Time:  0ms    1ms    2ms    3ms    4ms    5ms
   Motor 1: |=====[WINS]======|  (Response sent)
   Motor 3: |==[BLOCKED]      |  (Backs off, waits)
   Motor 7: |==[BLOCKED]      |  (Backs off, waits)
   Motor 9: |==[BLOCKED]      |  (Backs off, waits)
   Motor 11:|==[BLOCKED]      |  (Backs off, waits)
   Motor 14:|==[BLOCKED]      |  (Backs off, waits)
   ```

3. **After Motor 1 Wins:**
   - Motor 1 transmits its response (takes ~1-2ms)
   - Motors 3, 7, 9, 11, 14 see bus is busy and wait
   - After Motor 1 finishes, remaining motors retry
   - Motor 3 (ID 3) wins next arbitration
   - Process repeats...

## Why This Causes Issues

### When All 6 Motors Are Connected:

**Scenario 1: Broadcast Query Triggers All Motors**
```
You send: Query command
Motors 1, 3, 7, 9, 11, 14 all try to respond simultaneously
Result:
  ✅ Motor 1 (ID 1, highest priority) - WINS, responds
  ✅ Motor 3 (ID 3, high priority) - Wins next, responds
  ❌ Motor 7 (ID 7, medium priority) - May lose to others
  ❌ Motor 9 (ID 9, medium priority) - May lose to others
  ❌ Motor 11 (ID 11, lower priority) - Often loses
  ✅ Motor 14 (ID 14, lower priority) - Sometimes wins if others back off
```

**Scenario 2: Individual Queries But Bus Contention**
```
Query Motor 7 → Motor 7 tries to respond
BUT Motor 1, 3, 14 are still processing/responding from previous queries
Result: Motor 7's response collides and is blocked
```

## Solutions

### Solution 1: Query in Reverse Priority Order (Highest ID First)

Query motors with **HIGHEST IDs FIRST** so they respond before lower-ID motors can interfere:

```python
# Query order: 14, 11, 9, 7, 3, 1
# Lower priority motors get to respond first
```

**Why this works:**
- Motor 14 responds first (no competition)
- Then Motor 11 (Motor 14 already done)
- Then Motor 9 (14, 11 done)
- ...and so on

### Solution 2: Longer Delays Between Queries

Wait long enough for:
- Previous response to complete
- Bus to become idle
- All motors to process previous queries

```python
Query Motor 1 → Wait 3 seconds → Query Motor 3 → Wait 3 seconds → ...
```

### Solution 3: Query High-ID Motors in Isolation

Query motors 7, 9, 11 FIRST (before 1, 3, 14):

```python
# Query order: 11, 9, 7 (high IDs first)
# Then: 14, 3, 1 (lower IDs)
```

This ensures high-ID motors respond before lower-ID motors can interfere.

### Solution 4: Passive Listening with Extended Timeout

After sending all queries, listen passively for delayed responses:

```python
# Send all queries
for motor in [7, 9, 11, 14, 3, 1]:
    send_query(motor)
    time.sleep(0.5)

# Then listen passively for 10 seconds
# Motors that lost arbitration will retry later
listen_passive(10.0)
```

### Solution 5: Use CanOPEN Node Guarding/Heartbeat

CanOPEN heartbeat messages (COB-ID = 0x700 + node_id) might have different priorities or timing.

## Implementation Strategy

The best approach combines:
1. **Query high-ID motors FIRST** (14, 11, 9, 7)
2. **Long delays between queries** (2-3 seconds)
3. **Extended response timeouts** (5 seconds per motor)
4. **Passive listening after all queries** (10 seconds)

