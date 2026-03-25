# Yamaha ECU Mobile App (Flutter)

## Overview

A Flutter mobile app that connects to the Yamaha ECU diagnostic hardware via Bluetooth and displays real-time engine data.

## Features (Planned)

- [ ] Bluetooth connection to STN1110/ESP32 adapter
- [ ] Real-time RPM, temp, voltage display
- [ ] Fault code reading and clearing
- [ ] Engine hours tracking
- [ ] Data logging to phone storage
- [ ] Historical data visualization

## Architecture

```
┌─────────────────┐      Bluetooth      ┌─────────────────┐
│   Yamaha F150   │◄──── KWP2000 ──────►│  Mobile Phone   │
│   Engine ECU    │                     │  Flutter App    │
└─────────────────┘                     └─────────────────┘
```

## Project Structure (Flutter)

```
yamaha_ecu_app/
├── lib/
│   ├── main.dart
│   ├── app.dart
│   ├── bluetooth/
│   │   ├── bluetooth_service.dart
│   │   └── device_list.dart
│   ├── ecu/
│   │   ├── kwp2000_service.dart
│   │   ├── yamaha_protocol.dart
│   │   └── models/
│   │       ├── sensor_data.dart
│   │       └── fault_code.dart
│   ├── ui/
│   │   ├── dashboard_screen.dart
│   │   ├── sensors_screen.dart
│   │   ├── dtc_screen.dart
│   │   └── settings_screen.dart
│   └── utils/
│       └── formatters.dart
├── pubspec.yaml
└── README.md
```

## Tech Stack

- Flutter 3.x
- flutter_blue_plus (Bluetooth LE)
- Provider or Riverpod (state management)
- fl_chart (data visualization)
- shared_preferences (settings)

## Getting Started

```bash
# Clone repo
git clone https://github.com/yourusername/yamaha-ecu-tool
cd yamaha-ecu-tool/app

# Get dependencies
flutter pub get

# Run on device
flutter run
```

## Building

### Android
```bash
flutter build apk --release
```

### iOS
```bash
flutter build ios --release
```

## Permissions

### Android (AndroidManifest.xml)
```xml
<uses-permission android:name="android.permission.BLUETOOTH"/>
<uses-permission android:name="android.permission.BLUETOOTH_ADMIN"/>
<uses-permission android:name="android.permission.ACCESS_FINE_LOCATION"/>
```

### iOS (Info.plist)
```xml
<key>NSBluetoothAlwaysUsageDescription</key>
<string>Bluetooth is used to connect to your engine diagnostic adapter</string>
<key>NSBluetoothPeripheralUsageDescription</key>
<string>Bluetooth is used to connect to your engine diagnostic adapter</string>
```

## TODO

1. [ ] Set up Flutter project structure
2. [ ] Implement Bluetooth scanning/connection
3. [ ] Build KWP2000 protocol parser in Dart
4. [ ] Create dashboard UI
5. [ ] Add sensor display screen
6. [ ] Add fault code screen
7. [ ] Implement data logging
8. [ ] Add settings screen

## Contributing

Open to contributions! See main project README for details.
