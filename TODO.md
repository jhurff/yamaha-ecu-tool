# Yamaha ECU Tool - TODO

## High Priority
- [ ] Test with actual Yamaha F150XD ECU
- [ ] Confirm correct KWP2000 session type (0x81 vs others)
- [ ] Verify Local ID values for sensor data

## Medium Priority
- [ ] Create Python package for pip installation
- [ ] Add more Yamaha DTC definitions
- [ ] Build simple data logger (CSV export)
- [ ] Test with other Yamaha outboard models

## Low Priority
- [ ] Create Flutter mobile app
- [ ] Add GUI using tkinter/PyQt
- [ ] Build ESP32 firmware
- [ ] Document Yamaha Command Link protocol

## Research Needed
- [ ] Confirm ECU address (currently using 0x10)
- [ ] Verify slow init vs fast init requirements
- [ ] Find undocumented YDS command codes

## Testing Checklist
- [ ] F150XD 2022+
- [ ] F250 (earlier models)
- [ ] Other Yamaha outboards using KWP2000

## Known Issues
- Some STN1110 clones don't properly support KWP2000 slow init
- Response timing varies between ECU models
