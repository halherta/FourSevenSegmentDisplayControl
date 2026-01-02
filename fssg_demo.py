import time
from four_seven_segment_display import FourSevenSeg

def main():
    # Configure your GPIO pins here
    SEGMENT_PINS = [7, 25, 23, 15, 14, 8, 24]  # a, b, c, d, e, f, g
    SELECT_PINS = [20, 21, 26, 16]  # digit 1, 2, 3, 4 select pins
    DP_PIN = 18  # decimal point pin (optional)
    
    # Initialize the display
    display = FourSevenSeg(
        chip="/dev/gpiochip0",
        seven_segment_pins=SEGMENT_PINS,
        dp_pin=DP_PIN,
        select_pins=SELECT_PINS,
        refresh_rate=200  # Hz
    )
    
    try:
        # Start the multiplexing thread
        display.start()
        print("Display started.")
        
        print("\nCounting 0-20")
        for i in range(21):
            digits = [
                FourSevenSeg.DIGIT_PATTERNS[i // 1000 % 10],
                FourSevenSeg.DIGIT_PATTERNS[i // 100 % 10],
                FourSevenSeg.DIGIT_PATTERNS[i // 10 % 10],
                FourSevenSeg.DIGIT_PATTERNS[i % 10]
            ]
            display.update_display_data(digits)
            time.sleep(0.5)
        
        time.sleep(1)
        
        # Display with decimal points
        print("\nDisplaying 12.34")
        digits = [
            FourSevenSeg.DIGIT_PATTERNS[1],
            FourSevenSeg.DIGIT_PATTERNS[2],
            FourSevenSeg.DIGIT_PATTERNS[3],
            FourSevenSeg.DIGIT_PATTERNS[4]
        ]
        display.update_display_data(digits)
        display.update_dp_segment([False, True, False, False])  # DP after digit 2
        time.sleep(3)
        
        # Display text
        print("\nDisplaying 'HELP'")
        digits = [
            FourSevenSeg.CHAR_PATTERNS['H'],
            FourSevenSeg.CHAR_PATTERNS['E'],
            FourSevenSeg.CHAR_PATTERNS['L'],
            FourSevenSeg.CHAR_PATTERNS['P']
        ]
        display.update_display_data(digits)
        display.update_dp_segment([False, False, False, False])
        time.sleep(3)
        
        
        # Blinking decimal points
        print("\nBlinking decimal points")
        digits = [
            FourSevenSeg.DIGIT_PATTERNS[8],
            FourSevenSeg.DIGIT_PATTERNS[8],
            FourSevenSeg.DIGIT_PATTERNS[8],
            FourSevenSeg.DIGIT_PATTERNS[8]
        ]
        display.update_display_data(digits)
        
        for _ in range(6):
            display.update_dp_segment([True, True, True, True])
            time.sleep(0.5)
            display.update_dp_segment([False, False, False, False])
            time.sleep(0.5)
        
        # Clear display
        print("\nClearing display")
        blank = [FourSevenSeg.CHAR_PATTERNS[' ']] * 4
        display.update_display_data(blank)
        time.sleep(2)
        
        print("\nDemo complete!")
        
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    
    finally:
        # Clean up
        display.close()
        print("Display closed")

if __name__ == "__main__":
    main()
