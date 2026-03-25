#!/usr/bin/env python3
"""
Yamaha ECU Diagnostic Reader - CLI Tool

Usage:
    python3 reader.py /dev/ttyUSB0
    python3 reader.py COM3
"""

import argparse
import logging
import sys
import time
from typing import Optional

# Try to import serial, provide helpful error if not installed
try:
    import serial
except ImportError:
    print("ERROR: pyserial not installed.")
    print("Install with: pip install pyserial")
    sys.exit(1)

from kwp2000.protocol import KWP2000Protocol, KWP2000_SID
from yamaha.commands import YamahaYDS, format_dtc

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def parse_args():
    parser = argparse.ArgumentParser(
        description='Yamaha ECU Diagnostic Reader'
    )
    parser.add_argument(
        'port',
        help='Serial port (e.g., /dev/ttyUSB0, COM3)'
    )
    parser.add_argument(
        '--baud',
        type=int,
        default=19200,
        help='Baud rate (default: 19200 for KWP2000)'
    )
    parser.add_argument(
        '--timeout',
        type=float,
        default=3.0,
        help='Serial timeout in seconds (default: 3.0)'
    )
    parser.add_argument(
        '--session',
        type=int,
        default=0x81,
        help='Diagnostic session type (default: 0x81)'
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug logging'
    )
    return parser.parse_args()


class DiagnosticReader:
    """Main diagnostic reader application"""
    
    def __init__(self, port: str, baud: int = 19200, timeout: float = 3.0):
        self.port = port
        self.baud = baud
        self.timeout = timeout
        self.serial = None
        self.kwp = None
        self.yamaha = None
        
    def connect(self) -> bool:
        """Establish connection to ECU"""
        try:
            logger.info(f"Connecting to {self.port} at {self.baud} baud...")
            
            self.serial = serial.Serial(
                port=self.port,
                baudrate=self.baud,
                timeout=self.timeout,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
            )
            
            # KWP2000 uses 5-baud slow init or fast init
            # Most adapters handle this automatically
            time.sleep(1.0)  # Wait for ECU to initialize after connection
            
            self.kwp = KWP2000Protocol(self.serial)
            self.yamaha = YamahaYDS(self.kwp)
            
            logger.info("Starting diagnostic session...")
            if not self.kwp.start_session():
                logger.error("Failed to start diagnostic session")
                return False
            
            logger.info("Connected successfully!")
            return True
            
        except serial.SerialException as e:
            logger.error(f"Serial error: {e}")
            return False
    
    def read_sensors(self):
        """Read and display all sensor data"""
        print("\n" + "=" * 50)
        print("SENSOR DATA")
        print("=" * 50)
        
        sensors = self.yamaha.get_all_sensors()
        
        def fmt(val, unit="", none_str="N/A"):
            if val is None:
                return none_str
            return f"{val:.1f} {unit}" if isinstance(val, float) else f"{val} {unit}"
        
        print(f"RPM:              {fmt(sensors.get('rpm'), 'rpm', 'N/A')}")
        print(f"Coolant Temp:     {fmt(sensors.get('coolant_temp_c'), '°C', 'N/A')}")
        print(f"Oil Temp:         {fmt(sensors.get('oil_temp_c'), '°C', 'N/A')}")
        print(f"Throttle:         {fmt(sensors.get('throttle_pct'), '%', 'N/A')}")
        print(f"Battery Voltage:  {fmt(sensors.get('voltage'), 'V', 'N/A')}")
        print(f"Trim Position:    {fmt(sensors.get('trim'), '', 'N/A')}")
        
        hours = sensors.get('engine_hours')
        if hours:
            print(f"Engine Hours:     {hours // 60}h {hours % 60}m")
        else:
            print(f"Engine Hours:     N/A")
        
        status = sensors.get('status', {})
        if status:
            print("\nSTATUS FLAGS:")
            flags = []
            if status.get('check_engine'):
                flags.append("⚠️  CHECK ENGINE")
            if status.get('low_oil'):
                flags.append("⚠️  LOW OIL")
            if status.get('overheat'):
                flags.append("🚨  OVERHEAT")
            if status.get('water_in_fuel'):
                flags.append("💧  WATER IN FUEL")
            
            if flags:
                for f in flags:
                    print(f"  {f}")
            else:
                print("  ✅ No active warnings")
        
        print()
    
    def read_dtcs(self):
        """Read diagnostic trouble codes"""
        print("\n" + "=" * 50)
        print("DIAGNOSTIC TROUBLE CODES")
        print("=" * 50)
        
        dtcs = self.kwp.read_dtc()
        
        if not dtcs:
            print("No DTCs stored - engine is happy! ✅")
        else:
            for dtc, status in dtcs:
                print(f"  {format_dtc(dtc, status)}")
        print()
    
    def clear_dtcs(self):
        """Clear DTCs"""
        print("\nClearing DTCs...")
        if self.kwp.clear_dtc():
            print("DTCs cleared successfully! ✅")
        else:
            print("Failed to clear DTCs ❌")
        print()
    
    def keep_alive(self):
        """Send tester present to keep session alive"""
        self.kwp.tester_present()
    
    def disconnect(self):
        """Disconnect from ECU"""
        if self.kwp:
            self.kwp.end_session()
        if self.serial and self.serial.is_open:
            self.serial.close()
        logger.info("Disconnected")


def interactive_mode(reader: DiagnosticReader):
    """Interactive command mode"""
    print("\nYamaha ECU Diagnostic Reader")
    print("Commands: sensors, dtcs, clear, quit")
    print("-" * 30)
    
    while True:
        try:
            cmd = input("> ").strip().lower()
            
            if cmd == 'sensors' or cmd == 's':
                reader.read_sensors()
            elif cmd == 'dtcs' or cmd == 'd':
                reader.read_dtcs()
            elif cmd == 'clear' or cmd == 'c':
                reader.clear_dtcs()
            elif cmd == 'quit' or cmd == 'q' or cmd == 'exit':
                break
            elif cmd == 'help' or cmd == 'h':
                print("Commands: sensors (s), dtcs (d), clear (c), quit (q)")
            else:
                print(f"Unknown command: {cmd}")
                print("Commands: sensors (s), dtcs (d), clear (c), quit (q)")
            
            # Keep session alive
            reader.keep_alive()
            
        except KeyboardInterrupt:
            print("\nInterrupted")
            break
    
    reader.disconnect()


def main():
    args = parse_args()
    
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    reader = DiagnosticReader(args.port, args.baud, args.timeout)
    
    if not reader.connect():
        sys.exit(1)
    
    try:
        # Default: read sensors and DTCs
        reader.read_sensors()
        reader.read_dtcs()
        
        # Then go interactive
        interactive_mode(reader)
        
    except Exception as e:
        logger.error(f"Error: {e}")
        if args.debug:
            raise
        sys.exit(1)


if __name__ == '__main__':
    main()
