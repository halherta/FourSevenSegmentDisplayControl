# FourSevenSegmentDisplayControl

![photo of seven segment led interfacing to raspberry pi](https://github.com/halherta/FourSevenSegmentDisplayControl/blob/main/images/seven_segment_display_photo.jpg)

A Python library for controlling 4-digit seven-segment displays on Raspberry Pi using the modern Linux GPIOD driver (libgpiod 2.x).

## Overview

This library provides a clean, efficient interface for controlling common cathode 4-digit seven-segment displays (like the 5461AS) using the Raspberry Pi's GPIO pins. It leverages the modern GPIOD library, which is the kernel-recommended approach for GPIO interaction on Linux systems, offering better performance and reliability compared to older interfaces like sysfs.

## Features

- **Modern GPIOD 2.x API**: Uses the latest Linux GPIO character device interface
- **Efficient Multiplexing**: Implements digit scanning to control 4 displays with only 12 GPIO pins instead of 32
- **Thread-Safe Display**: Background thread handles display refresh automatically
- **Configurable Refresh Rate**: Adjustable refresh rate (default 200Hz) for flicker-free display
- **Built-in Character Patterns**: Pre-defined patterns for digits 0-9 and common characters
- **Decimal Point Control**: Independent control of decimal points for each digit
- **Easy to Use**: Simple API for updating display content

## Hardware Requirements

- Raspberry Pi (tested on Zero 2W, should work on any model)
- 4-digit seven-segment display (common cathode, e.g., 5461AS)
- 8x 220Ω resistors (for LED current limiting)
- 4x NPN transistors (e.g., 2N2222, for digit control)
- 4x 1kΩ resistors (for transistor base)
- Breadboard and jumper wires

## Wiring

The library requires 12 GPIO pins total:
- 7 pins for segments (A-G)
- 1 pin for decimal point (DP)
- 4 pins for digit selection (DIG1-4)

![breadboard diagram](https://github.com/halherta/FourSevenSegmentDisplayControl/blob/main/images/seven_segment_display_breadboard.png)

### Connection Details

1. **Segment Control**: Each segment (A-G) connects to a GPIO pin through a 220Ω current-limiting resistor
2. **Decimal Point**: DP pin connects to a GPIO pin through a 220Ω resistor
3. **Digit Selection**: Each DIG pin connects to ground via an NPN transistor, with the transistor base controlled by a GPIO pin through a 1kΩ resistor

This configuration ensures that current from multiple LEDs doesn't flow through a single GPIO pin, protecting your Raspberry Pi.

![schematic diagram](https://github.com/halherta/FourSevenSegmentDisplayControl/blob/main/images/seven_segment_display_schematic.png)

### Example Pin Configuration

```python
SEGMENT_PINS = [7, 25, 23, 15, 14, 8, 24]  # GPIO pins for segments a, b, c, d, e, f, g
SELECT_PINS = [20, 21, 26, 16]              # GPIO pins for digit 1, 2, 3, 4 selection
DP_PIN = 18                                  # GPIO pin for decimal point
```

For detailed schematics and breadboard diagrams, see the [blog post](https://hussamtalkstech.com/rpi-4sevenseg01/).

## Installation

### Prerequisites

Install the Python GPIOD library:

```bash
sudo apt-get update
sudo apt-get install python3-libgpiod
```

### Get the Code

```bash
git clone https://github.com/halherta/FourSevenSegmentDisplayControl.git
cd FourSevenSegmentDisplayControl
```

## Usage

### Basic Example

```python
from four_seven_segment_display import FourSevenSeg
import time

# Configure your GPIO pins
SEGMENT_PINS = [7, 25, 23, 15, 14, 8, 24]  # a, b, c, d, e, f, g
SELECT_PINS = [20, 21, 26, 16]              # digit 1, 2, 3, 4
DP_PIN = 18

# Initialize the display
display = FourSevenSeg(
    chip="/dev/gpiochip0",
    seven_segment_pins=SEGMENT_PINS,
    dp_pin=DP_PIN,
    select_pins=SELECT_PINS,
    refresh_rate=200  # Hz
)

# Start the display
display.start()

# Display "12.34"
digits = [
    FourSevenSeg.DIGIT_PATTERNS[1],
    FourSevenSeg.DIGIT_PATTERNS[2],
    FourSevenSeg.DIGIT_PATTERNS[3],
    FourSevenSeg.DIGIT_PATTERNS[4]
]
display.update_display_data(digits)
display.update_dp_segment([False, True, False, False])  # DP after digit 2

time.sleep(3)

# Clear display
blank = [FourSevenSeg.CHAR_PATTERNS[' ']] * 4
display.update_display_data(blank)
display.update_dp_segment([False, False, False, False])

# Clean up
display.close()
```

### Available Patterns

The library includes built-in patterns accessible via:
- `FourSevenSeg.DIGIT_PATTERNS`: Dictionary for digits 0-9
- `FourSevenSeg.CHAR_PATTERNS`: Dictionary for additional characters (including space)

### API Reference

#### Initialization

```python
FourSevenSeg(chip, seven_segment_pins, dp_pin, select_pins, refresh_rate=200)
```

- `chip`: GPIO chip device (usually "/dev/gpiochip0")
- `seven_segment_pins`: List of 7 GPIO pins for segments A-G
- `dp_pin`: GPIO pin for decimal point
- `select_pins`: List of 4 GPIO pins for digit selection
- `refresh_rate`: Display refresh rate in Hz (default: 200)

#### Methods

- `start()`: Start the display refresh thread
- `update_display_data(digits)`: Update the digits to display (list of 4 segment patterns)
- `update_dp_segment(dp_states)`: Update decimal points (list of 4 boolean values)
- `close()`: Stop the display and release GPIO resources

## How It Works

The display uses a technique called **multiplexing** or **digit scanning**. Instead of controlling all 4 digits simultaneously (which would require 32 GPIO pins), the library rapidly switches between digits, activating only one at a time. When this switching happens faster than ~30 times per second, human persistence of vision makes it appear that all digits are lit continuously.

The default refresh rate of 200Hz means each digit is updated 50 times per second, providing a flicker-free display.

## Demo

The repository includes `fssg_demo.py` which demonstrates various display capabilities. Run it with:

```bash
python3 fssg_demo.py
```

## Technical Details

- Uses Python's threading module for background display refresh
- Implements thread-safe data updates with locks
- Compatible with GPIOD 2.x API
- Typical LED current: ~6mA per segment (with 220Ω resistors)

## Troubleshooting

- **No display**: Check your wiring and ensure GPIO pins match your configuration
- **Flickering**: Try increasing the refresh rate
- **Dim display**: Check resistor values and LED current ratings
- **Permission errors**: Ensure you have access to `/dev/gpiochip0` (may need to add user to `gpio` group)

## Resources

- [Detailed tutorial and wiring diagrams](https://hussamtalkstech.com/rpi-4sevenseg01/)
- [5461AS Datasheet](https://hussamtalkstech.com/wp-content/uploads/5461AS.pdf)

## License

This project is open source. Feel free to use and modify as needed.

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## Author

Created by Hussam Al-Hertani (halherta)

## Acknowledgments

This project was developed to advance understanding of the Linux GPIOD driver and demonstrate modern GPIO control techniques on Raspberry Pi.
