# Hardware Connection Guide

## Yamaha Diagnostic Port

### Connector Location
The 6-pin Yamaha diagnostic connector is typically located:
- Under the engine cowling
- Near the engine harness junction
- Sometimes near the tilt pin

### Connector Pinout

```
View looking at the connector on the engine:

    +------+
    | 1  2 |
    | 3  4 |
    | 5  6 |
    +------+

Pin 1: K-Line (KWP2000 data)
Pin 2: Ground (Chassis)
Pin 3: +12V (Accessory power)
Pin 4: (Unknown/Reserved)
Pin 5: (Unknown/Reserved)
Pin 6: (Unknown/Reserved)
```

**Important:** The K-Line carries the KWP2000 protocol data.

## Hardware Options

### Option 1: STN1110 Adapter (Recommended)

STN1110 is an ELM327-compatible OBD-II chip that supports KWP2000 (ISO 14230).

**Parts:**
- STN1110-based adapter (e.g., OBDLink LX, or bare STN1110 board)
- Yamaha 6-pin to OBD-II cable (or custom cable)

**Connection:**
```
Yamaha 6-pin Connector    STN1110 Adapter    Computer
      Pin 1 (K-Line)  -->  Pin 7 (K-Line)  -->  USB/BT
      Pin 2 (GND)     -->  Pin 4 (GND)     -->  GND
      Pin 3 (+12V)    -->  Pin 16 (12V)    -->  (adapter has its own)
```

### Option 2: ESP32 DIY Interface

For full control, build your own interface:

**Parts List:**
- ESP32 DevKit v1 (or wROOM-32)
- TJA1055 CAN transceiver module
- 6-pin Yamaha connector (dealer part or aftermarket)
- Prototyping board
- Case

**Pin Connections:**
```
ESP32 GPIO27  <-->  TJA1055 TX
ESP32 GPIO26  <-->  TJA1055 RX
ESP32 3.3V    <-->  TJA1055 VCC
ESP32 GND     <-->  TJA1055 GND

TJA1055 CANH  <-->  Yamaha K-Line (Pin 1)
TJA1055 CANL  <-->  GND (Pin 2) or leave floating for K-Line
```

**Note:** KWP2000 uses a single-wire K-Line, not CAN. The TJA1055 is a CAN transceiver but can work in a pinch. For proper K-Line, use L9637 or similar.

### Option 3: Raspberry Pi + USB-Serial

**Parts:**
- Raspberry Pi (any model with USB)
- USB to RS232 TTL adapter (FTDI or similar)
- L9637 K-Line interface circuit
- Yamaha 6-pin connector

**L9637 Connection:**
```
FTDI TX  -->  L9637 D1
FTDI RX  -->  L9637 D0
5V       -->  L9637 VCC
GND      -->  L9637 GND

L9637 K   -->  Yamaha K-Line (Pin 1)
+12V     -->  Yamaha Pin 3 (for pullup if needed)
```

## Cable Making

### Yamaha 6-Pin Connector

You can buy:
- Yamaha dealer part (part number varies by model)
- Aftermarket connectors on eBay/Amazon
- Make your own with Molex connectors

### Wiring Diagram for Custom Cable

```
                    Yamaha 6-pin          OBD-II / Serial
                    Connector             Adapter
    +---------------+       +---------------+
    |  1 K-Line ----+-------| K-Line        |
    |  2 GND -------+-------| GND           |
    |  3 +12V ------+       | (optional)   |
    |  4 -          |       |               |
    |  5 -          |       |               |
    |  6 -          |       |               |
    +---------------+       +---------------+
```

## Testing

### Verify Connection

1. Connect adapter to Yamaha diagnostic port
2. Turn key to ON (engine off)
3. Run reader:
   ```bash
   python3 src/reader.py /dev/ttyUSB0
   ```

4. If you see sensor data, connection is working!

### Troubleshooting

| Problem | Likely Cause | Fix |
|---------|-------------|-----|
| No response | Wrong baud rate | Try 4800, 9600, 19200 |
| Garbled data | Wrong port | Check serial port selection |
| Timeout | K-Line not connected | Verify wiring |
| Session fails | Adapter doesn't support KWP2000 | Use STN1110-based |

## Safety

- **Always** disconnect adapter before starting engine
- Don't plug/unplug while engine is running
- 12V from engine can damage your adapter - use protection
