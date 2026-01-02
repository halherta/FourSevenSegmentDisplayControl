import gpiod
from gpiod.line import Direction, Value
import time
import threading


class FourSevenSeg:
    # Segment patterns for digits 0-9
    # Each tuple represents (a, b, c, d, e, f, g)
    DIGIT_PATTERNS = {
        0: (1, 1, 1, 1, 1, 1, 0),  # Display "0"
        1: (0, 1, 1, 0, 0, 0, 0),  # Display "1"
        2: (1, 1, 0, 1, 1, 0, 1),  # Display "2"
        3: (1, 1, 1, 1, 0, 0, 1),  # Display "3"
        4: (0, 1, 1, 0, 0, 1, 1),  # Display "4"
        5: (1, 0, 1, 1, 0, 1, 1),  # Display "5"
        6: (1, 0, 1, 1, 1, 1, 1),  # Display "6"
        7: (1, 1, 1, 0, 0, 0, 0),  # Display "7"
        8: (1, 1, 1, 1, 1, 1, 1),  # Display "8"
        9: (1, 1, 1, 1, 0, 1, 1),  # Display "9"
    }
    
    # Additional characters
    CHAR_PATTERNS = {
        'A': (1, 1, 1, 0, 1, 1, 1),
        'b': (0, 0, 1, 1, 1, 1, 1),
        'C': (1, 0, 0, 1, 1, 1, 0),
        'd': (0, 1, 1, 1, 1, 0, 1),
        'E': (1, 0, 0, 1, 1, 1, 1),
        'F': (1, 0, 0, 0, 1, 1, 1),
        'H': (0, 1, 1, 0, 1, 1, 1),
        'L': (0, 0, 0, 1, 1, 1, 0),
        'P': (1, 1, 0, 0, 1, 1, 1),
        'U': (0, 1, 1, 1, 1, 1, 0),
        '-': (0, 0, 0, 0, 0, 0, 1),  # Minus sign
        ' ': (0, 0, 0, 0, 0, 0, 0),  # Blank
    }
    
    def __init__(self, chip: str = "/dev/gpiochip0", 
                 seven_segment_pins: list = None, 
                 dp_pin: int = None, 
                 select_pins: list = None,
                 refresh_rate: float = 200):
        if seven_segment_pins is None or len(seven_segment_pins) != 7:
            raise Exception("You must specify 7 pins to control a seven segment display")
        if select_pins is None or len(select_pins) != 4:
            raise Exception("You must specify 4 pins to control the 4 seven segment displays")

        self.chip_path = chip
        self.refresh_rate = refresh_rate
        self._running = False
        self._thread = None
        self.display_data = [(0,0,0,0,0,0,0)] * 4  # Initialize with blank displays
        self.dp_states = [False] * 4
        
        # Thread safety: lock for protecting shared display data
        self._lock = threading.Lock()
        
        # Request lines for seven segment display (gpiod 2.x API)
        self.seven_segment_request = gpiod.request_lines(
            chip,
            consumer="seven_segment",
            config={
                tuple(seven_segment_pins): gpiod.LineSettings(
                    direction=Direction.OUTPUT,
                    output_value=Value.INACTIVE
                )
            }
        )
        self.seven_segment_pins = seven_segment_pins
        
        # Request lines for digit selection
        self.select_request = gpiod.request_lines(
            chip,
            consumer="digit_select",
            config={
                tuple(select_pins): gpiod.LineSettings(
                    direction=Direction.OUTPUT,
                    output_value=Value.INACTIVE
                )
            }
        )
        self.select_pins = select_pins
        
        # Request line for decimal point (optional)
        self.dp_request = None
        self.dp_pin = dp_pin
        if dp_pin is not None:
            self.dp_request = gpiod.request_lines(
                chip,
                consumer="decimal_point",
                config={
                    dp_pin: gpiod.LineSettings(
                        direction=Direction.OUTPUT,
                        output_value=Value.INACTIVE
                    )
                }
            )

    def write_seven_segment_display(self, value: tuple = None):
        if value is None or len(value) != 7:
            raise ValueError(f"Expected 7 values, got {len(value) if value else 0}")
        
        # Convert tuple to dictionary mapping pin to Value
        values = {
            self.seven_segment_pins[i]: Value.ACTIVE if value[i] else Value.INACTIVE
            for i in range(7)
        }
        self.seven_segment_request.set_values(values)

    def select_segment(self, digit: int = 0):
        if digit < 0 or digit > 4:
            raise ValueError(f"Expecting a value between 0 and 4 inclusive")

        # Create value dictionary for all select pins
        values = {pin: Value.INACTIVE for pin in self.select_pins}
        
        if 1 <= digit <= 4:
            values[self.select_pins[digit-1]] = Value.ACTIVE
            
        self.select_request.set_values(values)
  
    def write_dp(self, value: bool = False):
        """Set decimal point state"""
        if self.dp_request:
            self.dp_request.set_value(
                self.dp_pin, 
                Value.ACTIVE if value else Value.INACTIVE
            )
        
    def _multiplexing_loop(self):
        """
        Main multiplexing loop - runs in separate thread.
        Rapidly cycles through each digit to create persistence of vision effect.
        """
        digit_time = 1.0 / self.refresh_rate  # Time per digit
        
        while self._running:
            for digit_index in range(4):
                if not self._running:
                    break
                
                # Acquire lock to safely read display data
                with self._lock:
                    segment_pattern = self.display_data[digit_index]
                    dp_state = self.dp_states[digit_index]
                
                # Set segments for this digit
                self.write_seven_segment_display(segment_pattern)
                
                # Set decimal point for this digit
                self.write_dp(dp_state)
                
                # Enable this digit
                self.select_segment(digit_index + 1)
                
                # Wait for persistence of vision
                time.sleep(digit_time)
                
                # Disable all digits (reduces ghosting)
                self.select_segment(0)
    
    def start(self):
        """Start multiplexing (required to see anything on display)"""
        if not self._running:
            self._running = True
            self._thread = threading.Thread(target=self._multiplexing_loop, daemon=True)
            self._thread.start()
    
    def stop(self):
        """Stop multiplexing and clear display"""
        self._running = False
        if self._thread:
            self._thread.join()
        self.select_segment(0)

    def update_display_data(self, digits: list):
        """Set all four digit patterns at once"""
        if len(digits) != 4:
            raise ValueError("Must provide exactly 4 digit patterns")
        
        # Acquire lock to safely write display data
        with self._lock:
            self.display_data = digits      
    
    def update_dp_segment(self, dp_states: list):
        if dp_states is None or len(dp_states) != 4:
            raise ValueError(f"Expecting a list of four boolean values")
        
        # Acquire lock to safely write dp states
        with self._lock:
            self.dp_states = dp_states

    def close(self):
        """Clean up resources"""
        self.stop()
        self.seven_segment_request.release()
        self.select_request.release()
        if self.dp_request:
            self.dp_request.release()
