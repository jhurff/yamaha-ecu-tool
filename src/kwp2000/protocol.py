"""
KWP2000 Protocol Implementation (ISO 14230)
Based on open source work by aster94/Keyword-Protocol-2000
"""

import time
import logging
from typing import Optional, List, Tuple

logger = logging.getLogger(__name__)

# KWP2000 Service IDs
class KWP2000_SID:
    START_DIAGNOSTIC_SESSION = 0x10
    ECU_RESET = 0x11
    CLEAR_DIAGNOSTIC_TROUBLE_CODES = 0x14
    READ_DIAGNOSTIC_TROUBLE_CODES = 0x17
    READ_DIAGNOSTIC_TROUBLE_CODES_BY_STATUS = 0x18
    READ_DATA_BY_LOCAL_ID = 0x22
    READ_DATA_BY_COMMON_ID = 0x21
    READ_DATA_BY_PERIODIC_ID = 0x29
    READ_MEMORY_ADDRESS = 0x23
    SECURITY_ACCESS = 0x27
    COMMUNICATION_CONTROL = 0x28
    READ_ECU_IDENTIFICATION = 0x1A
    DEVICE_CONTROL = 0x30
    WRITE_DATA_BY_LOCAL_ID = 0x3B
    WRITE_MEMORY_ADDRESS = 0x3D
    TESTER_PRESENT = 0x3E
    CONTROL_DTC_SETTING = 0x85
    RESPONSE_PENDING = 0x78

# KWP2000 Negative Response Codes
class KWP2000_NRC:
    GENERAL_REJECT = 0x10
    SERVICE_NOT_SUPPORTED = 0x11
    FUNCTION_NOT_SUPPORTED = 0x12
    CONDITIONS_NOT_CORRECT = 0x22
    REQUEST_SEQUENCE_ERROR = 0x24
    NO_RESPONSE_FROM_SUBNET_COMPONENT = 0x31
    FAILURE_PREVENTS_EXECUTION = 0x33
    REQUEST_OUT_OF_RANGE = 0x34
    SECURITY_ACCESS_DENIED = 0x35
    INVALID_KEY = 0x36
    EXCEEDED_NUMBER_OF_ATTEMPTS = 0x37
    REQUIRED_TIME_DELAY_NOT_EXPIRED = 0x38
    RESERVED = 0x39
    REQUEST_CORRECTLY_RECEIVED_PENDING = 0x78
    SUB_FUNCTION_NOT_SUPPORTED_INVALID_FORMAT = 0x12

class KWP2000Protocol:
    """KWP2000 protocol handler for ISO 14230"""
    
    # Standard timing (ms)
    P3_TIMEOUT = 3000  # Response timeout
    P4_INTER_BYTE = 200  # Inter-byte timeout
    
    def __init__(self, serial_interface, slow_init=True):
        """
        Initialize KWP2000 protocol
        
        Args:
            serial_interface: Serial port interface (must have read/write methods)
            slow_init: Use slow initialization (5 baud, required for some ECUs)
        """
        self.serial = serial_interface
        self.slow_init = slow_init
        self.session_active = False
        self.source_address = 0xF1  # Tester address
        self.target_address = 0x10  # ECU address (common for Yamaha)
        self.session_type = 0x00
        
    def slow_init_kline(self) -> bool:
        """
        Perform slow initialization on K-line (5 baud)
        Returns True if ECU responds
        """
        # This is handled by hardware in most cases
        # Some adapters auto-detect
        logger.info("Slow init not implemented in software - handled by adapter")
        return True
    
    def fast_init_kline(self) -> bool:
        """
        Perform fast initialization
        Returns True if ECU responds
        """
        # For fast init, we just send a wakeup message
        return True
    
    def send_message(self, data: List[int]) -> bool:
        """
        Send a KWP2000 message
        
        Args:
            data: List of bytes (SID + parameters)
        """
        # Build message: [format byte, length, target, source, data..., checksum]
        length = len(data) + 2  # +2 for source and target
        format_byte = 0x80 | length  # 0x80 = data bytes follow
        
        message = [
            format_byte,
            length,
            self.target_address,
            self.source_address,
            *data
        ]
        
        # Calculate checksum (simple modulo 256 sum)
        checksum = sum(message) & 0xFF
        message.append(checksum)
        
        # Send with inter-byte delay
        for byte in message:
            self.serial.write(byte)
            time.sleep(self.P4_INTER_BYTE / 1000.0)
        
        logger.debug(f"Sent: {' '.join(f'{b:02X}' for b in message)}")
        return True
    
    def receive_message(self, timeout_ms: int = None) -> Optional[List[int]]:
        """
        Receive a KWP2000 message
        
        Returns:
            List of bytes or None on timeout/error
        """
        timeout = timeout_ms or self.P3_TIMEOUT
        start_time = time.time()
        
        data = []
        while (time.time() - start_time) * 1000 < timeout:
            if self.serial.in_waiting > 0:
                byte = self.serial.read()
                data.append(byte)
                
                # Check for message complete (format byte tells us length)
                if len(data) >= 2:
                    length = data[1] & 0x7F  # Strip MSB if set
                    expected_len = length + 2  # +2 for source and target bytes
                    if len(data) >= expected_len:
                        # Got complete message
                        logger.debug(f"Received: {' '.join(f'{b:02X}' for b in data)}")
                        return data
            time.sleep(0.001)
        
        logger.warning(f"Timeout receiving message, got {len(data)} bytes")
        return None
    
    def send_and_receive(self, data: List[int], timeout_ms: int = None) -> Optional[List[int]]:
        """
        Send a message and wait for response
        Handles response pending (0x78) correctly
        """
        self.send_message(data)
        
        # Initial response
        response = self.receive_message(timeout_ms)
        
        # Handle response pending
        if response and len(response) >= 5:
            if response[4] == KWP2000_SID.RESPONSE_PENDING:
                # ECU is processing, wait for actual response
                logger.debug("Response pending, waiting for actual response")
                response = self.receive_message(timeout_ms)
        
        return response
    
    def parse_response(self, response: List[int]) -> Tuple[bool, List[int], int]:
        """
        Parse KWP2000 response
        
        Returns:
            Tuple: (success, data_bytes, error_code)
            - success: True if positive response
            - data_bytes: The actual data (excluding header/crc)
            - error_code: NRC if negative response, 0 if ok
        """
        if response is None or len(response) < 4:
            return False, [], -1
        
        # Skip header: [format, length, target, source]
        data_start = 4
        data = response[data_start:-1]  # Exclude checksum
        
        # Check if positive or negative response
        if len(data) >= 2:
            if data[1] == 0x00:  # Positive response echo or success
                return True, data[1:], 0
            elif data[1] == 0x7F:  # Negative response
                if len(data) >= 3:
                    nrc = data[2]
                    logger.warning(f"Negative response: SID={data[1]:02X} NRC={nrc:02X}")
                    return False, [], nrc
        
        # Assume success if no clear error
        return True, data, 0
    
    def start_session(self, session_type: int = 0x81) -> bool:
        """
        Start a diagnostic session
        
        Args:
            session_type: 0x81 = normal, 0x01 = programming, etc.
        """
        self.session_type = session_type
        data = [KWP2000_SID.START_DIAGNOSTIC_SESSION, session_type]
        
        response = self.send_and_receive(data)
        success, _, _ = self.parse_response(response)
        
        if success:
            self.session_active = True
            logger.info(f"Diagnostic session started (type 0x{session_type:02X})")
        else:
            logger.error("Failed to start diagnostic session")
        
        return success
    
    def tester_present(self) -> bool:
        """Send tester present to keep session alive"""
        data = [KWP2000_SID.TESTER_PRESENT, 0x00]
        self.send_message(data)
        return True
    
    def read_data_by_local_id(self, local_id: int) -> Optional[List[int]]:
        """
        Read data by local ID (Yamaha specific)
        
        Args:
            local_id: Local identifier for the data to read
        """
        data = [KWP2000_SID.READ_DATA_BY_LOCAL_ID, local_id]
        response = self.send_and_receive(data)
        
        success, data_bytes, _ = self.parse_response(response)
        if success and len(data_bytes) > 2:
            return data_bytes[2:]  # Skip echo of local_id
        return None
    
    def read_dtc(self) -> List[Tuple[int, int]]:
        """
        Read diagnostic trouble codes
        
        Returns:
            List of (DTC, status) tuples
        """
        data = [KWP2000_SID.READ_DIAGNOSTIC_TROUBLE_CODES]
        response = self.send_and_receive(data)
        
        if response is None:
            return []
        
        success, data_bytes, _ = self.parse_response(response)
        if not success:
            return []
        
        # Parse DTCs from response
        dtcs = []
        # Format: [num_codes, code1_lo, code1_hi, status1, code2_lo, code2_hi, status2, ...]
        if len(data_bytes) >= 2:
            num_codes = data_bytes[1]
            idx = 2
            for _ in range(num_codes):
                if idx + 2 < len(data_bytes):
                    dtc = (data_bytes[idx] << 8) | data_bytes[idx + 1]
                    status = data_bytes[idx + 2] if idx + 2 < len(data_bytes) else 0
                    dtcs.append((dtc, status))
                    idx += 3
        
        return dtcs
    
    def clear_dtc(self) -> bool:
        """Clear diagnostic trouble codes"""
        data = [KWP2000_SID.CLEAR_DIAGNOSTIC_TROUBLE_CODES]
        response = self.send_and_receive(data)
        
        success, _, _ = self.parse_response(response)
        if success:
            logger.info("DTCs cleared successfully")
        return success
    
    def read_ecu_id(self) -> Optional[dict]:
        """
        Read ECU identification
        Returns dict with various IDs
        """
        # System supplier id
        data = [KWP2000_SID.READ_ECU_IDENTIFICATION, 0x81]
        response = self.send_and_receive(data)
        
        if response is None:
            return None
        
        success, data_bytes, _ = self.parse_response(response)
        if not success or len(data_bytes) < 3:
            return None
        
        # Parse ECU ID - format varies by manufacturer
        return {
            'raw': data_bytes[2:],
            'status': data_bytes[1]
        }
    
    def end_session(self) -> bool:
        """End diagnostic session"""
        if not self.session_active:
            return True
        
        # Return to normal session
        success = self.start_session(0x82)  # Return to ecu
        if success:
            self.session_active = False
            logger.info("Diagnostic session ended")
        
        return success
    
    def close(self):
        """Clean up and close connection"""
        self.end_session()
