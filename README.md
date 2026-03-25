# Yamaha ECU Diagnostic Tool

Open source diagnostic reader for Yamaha outboard engines using KWP2000 (ISO 14230) protocol.

## What This Does

- Read engine fault codes (DTCs)
- Clear fault codes
- Display live sensor data (RPM, temp, pressure)
- Read engine hours and trim position
- Works with Yamaha outboards that use the YDS (Yamaha Diagnostic System) protocol

## Supported Engines

Tested with:
- Yamaha F150XD (2022+)
- Yamaha F250 (earlier models)

Other Yamaha outboards using KWP2000 should work but not confirmed.

## Hardware

### Option 1: STN1110 Adapter (Recommended)
- ELM327-compatible, supports KWP2000
- ~$25-40 from Amazon or OBDSol
- Connect to 6-pin Yamaha diagnostic port

### Option 2: ESP32 DIY Interface
- ESP32 + TJA1055 CAN transceiver
- Full control, programmable
- ~$20 in parts

### Option 3: Raspberry Pi + RS232
- Python-based
- Good for homebrew debugging station

## Quick Start

```bash
# Install dependencies
pip install python-serial cantools

# Connect adapter to diagnostic port
# Run reader
python3 src/reader.py
```

## Project Structure

```
yamaha-ecu-tool/
├── README.md
├── LICENSE
├── hardware/           # DIY hardware designs
├── src/
│   ├── kwp2000/      # KWP2000 protocol implementation
│   ├── yamaha/       # Yamaha-specific commands
│   ├── reader.py     # CLI diagnostic reader
│   └── logger.py     # Data logger
├── app/              # Mobile app (Flutter)
└── docs/             # Documentation
```

## Protocol

This tool uses the KWP2000 protocol (ISO 14230) which Yamaha uses for their dealer diagnostic system (YDS).

KWP2000 is the same protocol used by:
- Suzuki (SDS)
- Kawasaki (KDS)
- Honda (HDS)
- Yamaha (YDS)

## Contributing

Open to contributions. See TODO.md for planned features.

## Disclaimer

This tool reads diagnostic data only. Writing/tuning ECU parameters requires Yamaha's proprietary tools and is not supported by this project.
