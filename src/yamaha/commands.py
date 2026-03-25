"""
Yamaha YDS (Yamaha Diagnostic System) Command Definitions

These are Yamaha-specific interpretations of KWP2000 commands.
Based on community reverse engineering.
"""

from typing import Optional, Dict, List

# Yamaha-specific Local IDs for READ_DATA_BY_LOCAL_ID
class YDS_LID:
    """Yamaha Local IDs - these are guessed/inferred from community work"""
    
    # Engine Data
    ENGINE_RPM = 0x01
    ENGINE_COOLANT_TEMP = 0x02
    ENGINE_OIL_TEMP = 0x03
    INTAKE_AIR_TEMP = 0x04
    THROTTLE_POSITION = 0x05
    BATTERY_VOLTAGE = 0x06
    FUEL_LEVEL = 0x07
    SPEED = 0x08
    GEAR_POSITION = 0x09
    
    # Trim & Tilt
    TRIM_POSITION = 0x10
    TILT_POSITION = 0x11
    
    # Engine Hours
    ENGINE_HOURS = 0x20
    ENGINE_MINUTES = 0x21
    
    # Status Flags
    ENGINE_STATUS = 0x30
    CHECK_ENGINE = 0x31
    LOW_OIL_PRESSURE = 0x32
    OVERHEAT = 0x33
    
    # DTC related
    DTC_COUNT = 0x40
    DTC_FIRST = 0x41
    DTC_SECOND = 0x42


# Yamaha DTC (Diagnostic Trouble Code) definitions
# Format: P0XXX for powertrain
YAMAHA_DTC_CODES = {
    0x0100: "Generic DTC - Query ECU",
    0x0110: "Intake Air Temperature Sensor Circuit",
    0x0111: "Intake Air Temperature Sensor Range",
    0x0120: "Throttle Position Sensor Circuit",
    0x0121: "Throttle Position Sensor Range",
    0x0130: "O2 Sensor Circuit",
    0x0131: "O2 Sensor Range",
    0x0200: "Fuel System Circuit",
    0x0210: "Fuel Temperature Circuit",
    0x0220: "Fuel Pressure Circuit",
    0x0300: "Misfire Detected",
    0x0400: "Catalyst System",
    0x0500: "Evaporative System",
    0x0600: "OBD-II System",
    0x0700: "Transmission",
    0x0800: "Computer Output Circuit",
}


class YamahaYDS:
    """Yamaha YDS-specific command wrapper"""
    
    def __init__(self, kwp_protocol):
        self.kwp = kwp_protocol
    
    def read_rpm(self) -> Optional[int]:
        """Read engine RPM"""
        data = self.kwp.read_data_by_local_id(YDS_LID.ENGINE_RPM)
        if data and len(data) >= 2:
            # RPM is typically 16-bit, divide by 4 for actual value
            return ((data[0] << 8) | data[1]) // 4
        return None
    
    def read_coolant_temp(self) -> Optional[int]:
        """Read engine coolant temperature in Celsius"""
        data = self.kwp.read_data_by_local_id(YDS_LID.ENGINE_COOLANT_TEMP)
        if data and len(data) >= 1:
            # Convert to Celsius (offset may vary)
            return data[0] - 40 if data[0] > 40 else data[0]
        return None
    
    def read_oil_temp(self) -> Optional[int]:
        """Read oil temperature in Celsius"""
        data = self.kwp.read_data_by_local_id(YDS_LID.ENGINE_OIL_TEMP)
        if data and len(data) >= 1:
            return data[0] - 40 if data[0] > 40 else data[0]
        return None
    
    def read_throttle(self) -> Optional[float]:
        """Read throttle position as percentage (0-100)"""
        data = self.kwp.read_data_by_local_id(YDS_LID.THROTTLE_POSITION)
        if data and len(data) >= 1:
            return (data[0] / 255.0) * 100.0
        return None
    
    def read_voltage(self) -> Optional[float]:
        """Read battery voltage"""
        data = self.kwp.read_data_by_local_id(YDS_LID.BATTERY_VOLTAGE)
        if data and len(data) >= 2:
            # Voltage is typically 12-bit, units of 0.01V
            value = ((data[0] << 8) | data[1]) / 100.0
            return value
        return None
    
    def read_trim(self) -> Optional[int]:
        """Read trim position (0-100)"""
        data = self.kwp.read_data_by_local_id(YDS_LID.TRIM_POSITION)
        if data and len(data) >= 1:
            return data[0]
        return None
    
    def read_engine_hours(self) -> Optional[int]:
        """Read total engine hours"""
        hours = self.kwp.read_data_by_local_id(YDS_LID.ENGINE_HOURS)
        minutes = self.kwp.read_data_by_local_id(YDS_LID.ENGINE_MINUTES)
        
        if hours and len(hours) >= 2:
            h = (hours[0] << 8) | hours[1]
            m = minutes[0] if minutes else 0
            return h * 60 + m
        return None
    
    def read_engine_status(self) -> Dict[str, bool]:
        """Read engine status flags"""
        data = self.kwp.read_data_by_local_id(YDS_LID.ENGINE_STATUS)
        
        status = {}
        if data and len(data) >= 1:
            byte = data[0]
            status['check_engine'] = bool(byte & 0x01)
            status['low_oil'] = bool(byte & 0x02)
            status['overheat'] = bool(byte & 0x04)
            status['water_in_fuel'] = bool(byte & 0x08)
        return status
    
    def get_all_sensors(self) -> Dict[str, any]:
        """Read all available sensor data"""
        sensors = {}
        
        sensors['rpm'] = self.read_rpm()
        sensors['coolant_temp_c'] = self.read_coolant_temp()
        sensors['oil_temp_c'] = self.read_oil_temp()
        sensors['throttle_pct'] = self.read_throttle()
        sensors['voltage'] = self.read_voltage()
        sensors['trim'] = self.read_trim()
        sensors['engine_hours'] = self.read_engine_hours()
        sensors['status'] = self.read_engine_status()
        
        return sensors


def format_dtc(dtc: int, status: int) -> str:
    """Format a DTC for human reading"""
    # DTC format: first 2 chars identify the system
    # P = Powertrain, B = Body, C = Chassis, U = Network
    if dtc == 0:
        return "No DTC stored"
    
    category = (dtc >> 12) & 0x0F
    if category == 0:
        prefix = "P0"
    elif category == 1:
        prefix = "P1"
    elif category == 2:
        prefix = "P2"
    elif category == 3:
        prefix = "P3"
    elif category == 4:
        prefix = "B0"
    elif category == 5:
        prefix = "B1"
    elif category == 6:
        prefix = "C0"
    elif category == 7:
        prefix = "C1"
    elif category == 8:
        prefix = "U0"
    elif category == 9:
        prefix = "U1"
    elif category == 10:
        prefix = "U2"
    elif category == 11:
        prefix = "U3"
    else:
        prefix = "P?"
    
    code = dtc & 0xFFF
    formatted = f"{prefix}{code:03X}"
    
    # Look up known codes
    description = YAMAHA_DTC_CODES.get(dtc, "Unknown DTC")
    
    return f"{formatted}: {description} (status: 0x{status:02X})"
