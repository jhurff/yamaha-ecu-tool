# Hardware Setup Guide

## What You Need (Simplest Option)

### Option A: Buy a STN1110 Adapter (~30 min setup)

**Parts to buy:**

1. **STN1110-based OBD adapter** — $25-40
   - OBDLink LX (犇佰) - reliable, Bluetooth included
   - Or search "STN1110 OBD adapter" on Amazon/eBay

2. **Yamaha 6-pin to OBD-II cable** — $15-25
   - Search "Yamaha 6 pin diagnostic cable" on Amazon
   - Or buy from a Yamaha dealer

**Total cost: ~$40-65**

---

### Option B: DIY with ESP32 (~2 hours setup)

**Parts to buy:**

| Part | Where | Cost |
|------|-------|------|
| ESP32 DevKit v1 | Amazon | $10-15 |
| TJA1055 CAN module | Amazon/eBay | $5 |
| Yamaha 6-pin connector | Yamaha dealer or DIY | $5-10 |
| Jumper wires | Amazon | $3 |
| USB-C cable | You probably have one | $0 |

**Total cost: ~$20-30**

---

## How to Connect

### Find the Diagnostic Port

On your F150XD, the 6-pin diagnostic connector is usually:
- Under the engine cowling
- Near the engine harness junction box
- Check near the tilt pin area

The connector looks like this:

```
    +------+
    | 1  2 |
    | 3  4 |
    | 5  6 |
    +------+

Pin 1: K-Line (data) ← USE THIS
Pin 2: Ground (GND)  ← USE THIS
Pin 3: +12V (optional)
```

### Option A: STN1110 Connection

```
Yamaha 6-pin Cable          STN1110 Adapter          Your Computer
      Pin 1 (K-Line)  ────►   Pin 7 (K-Line)
      Pin 2 (GND)     ────►   Pin 4 (GND)
      
      [USB or Bluetooth]  ────►   USB port or Bluetooth
```

**Steps:**
1. Turn key to OFF
2. Plug Yamaha cable into your engine's diagnostic port
3. Connect cable to STN1110 adapter
4. Pair adapter via Bluetooth (or USB)
5. Run the software
6. Turn key to ON (engine stays off)

---

### Option B: ESP32 Connection

**Wiring:**

```
ESP32 GPIO27  ────►  TJA1055 TX
ESP32 GPIO26  ────►  TJA1055 RX  
ESP32 3.3V   ────►  TJA1055 VCC
ESP32 GND    ────►  TJA1055 GND

TJA1055 CANH  ────►  Yamaha Pin 1 (K-Line)
TJA1055 CANL  ────►  Yamaha Pin 2 (GND)
```

**ESP32 Pinout:**
```
    ┌─────────────┐
    │  3.3V   GND │
    │  GPIO27 TX  │
    │  GPIO26 RX  │
    │  USB 5V     │
    └─────────────┘
```

**Steps:**
1. Turn key to OFF
2. Connect ESP32 to your computer via USB
3. Wire ESP32 to TJA1055 as shown
4. Wire TJA1055 to Yamaha diagnostic port
5. Run the software
6. Turn key to ON

---

## How to Run

```bash
# 1. Install Python dependencies
pip install pyserial

# 2. Connect adapter to your computer

# 3. Find the serial port
# Linux/Mac:  ls /dev/ttyUSB*  or  ls /dev/tty.*
# Windows:    Check Device Manager for COM ports

# 4. Run the reader
python3 ~/yamaha-ecu-tool/src/reader.py /dev/ttyUSB0

# (replace /dev/ttyUSB0 with your actual port)
```

---

## If It Doesn't Work

| Problem | Try |
|---------|-----|
| "No response" | Check all wiring, try different baud rate |
| "Timeout" | K-Line not connected properly |
| "Session failed" | Your adapter might not support KWP2000 |
| Wrong data | Local ID values might need adjustment |

---

## Safety Rules

- ⚠️ Engine OFF when connecting/disconnecting
- ⚠️ Disconnect before starting engine  
- ⚠️ 12V from engine can fry your adapter - wire carefully
- ⚠️ Don't leave connected while boating

---

## Where to Buy

**STN1110 Adapters:**
- Amazon: Search "OBDLink LX"
- OBDSolutions.com: STN1110 boards

**Yamaha Cables:**
- Amazon: Search "Yamaha 6 pin outboard diagnostic cable"
- Yamaha dealer: Ask for "diagnostic harness connector"
- eBay: Search "Yamaha outboard 6 pin plug"

**ESP32:**
- Amazon: "ESP32 DevKit v1"
- Make sure it has USB-C and 38 pins
