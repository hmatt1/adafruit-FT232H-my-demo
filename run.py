import usb
import usb.util
print("usb:")
dev = usb.core.find(idVendor=0x0403, idProduct=0x6014)
print(dev)


from pyftdi.ftdi import Ftdi
print("ftdi:")
#Ftdi().open_from_url('ftdi:///?')

import os
blah = os.environ["BLINKA_FT232H"]
print("os:")
print(blah)


import board
import time
import digitalio


print("--- Full Board Inspection ---")
print(f"board_id: {board.board_id}")
print(f"board_key: {board.board_key}")
print(f"board_module: {board.board_module}")
print(f"pin: {board.pin}")
print(dir(board))


led = digitalio.DigitalInOut(board.C0)
led.direction = digitalio.Direction.OUTPUT


i = 0
while i < 10:
    led.value = False
    time.sleep(0.1)
    led.value = True
    time.sleep(0.1)
    i = i + 1

# Backpack I2C Address (defined in Adafruit docs, and etched on the board)
ADDR = 0x70

print("i2c setup...")
i2c = board.I2C()

while not i2c.try_lock():
    print("trying...")
    pass
addresses = i2c.scan()

for x in addresses:
    print(f"-> Device found at address: {hex(x)} (Decimal: {x})")
    if x == ADDR:
        print(f"   *** ADDR {hex(ADDR)} detected! ***")

try:
    print("blinking led on backpack...")
    
    # System Setup Register

    # The system setup register configures system operation or standby for the HT16K33A.

    # - The internal system oscillator is enabled when the 'S' bit of the system setup register is set to "1".
    # - The internal system clock is disabled and the device will enter the standby mode when the "S" bit of the system setup register is set to "0".
    # - Before the standby mode command is sent, it is strongly recommended to read the key data first.
    # - The system setup register command is shown as follows:

    # +------------+-----+-----+-----+-----+-----+-----+-----+-----+----------------+--------------------------------------------------+------+
    # | Name       | D15 | D14 | D13 | D12 | D11 | D10 | D9  | D8  | Option         | Description                                      | Def. |
    # +------------+-----+-----+-----+-----+-----+-----+-----+-----+----------------+--------------------------------------------------+------+
    # | System set |  0  |  0  |  1  |  0  |  X  |  X  |  X  |  S  | {S} Write only | Defines internal system oscillator on/off.       | 20H  |
    # |            |     |     |     |     |     |     |     |     |                |  {0}: Turn off System oscillator (standby mode)  |      |
    # |            |     |     |     |     |     |     |     |     |                |  {1}: Turn on System oscillator (normal mode)    |      |
    # +------------+-----+-----+-----+-----+-----+-----+-----+-----+----------------+--------------------------------------------------+------+

    # 0b00100001 = 0x21
    # The command to send is 0x21
    i2c.writeto(ADDR, bytes([0x21]))
    
    # 2. Set brightness
    
    # +-----+-----+-----+-----+-----+-----+-----+-----+-----------------------------+------+
    # | D15 | D14 | D13 | D12 | D11 | D10 | D9  | D8  | ROW Driver Output Pulse     | Def. |
    # |     |     |     |     |     |     |     |     | Width                       |      |
    # +-----+-----+-----+-----+-----+-----+-----+-----+-----------------------------+------+
    # |  1  |  1  |  1  |  0  |  P3 |  P2 |  P1 |  P0 | —                           |  —   |
    # +-----+-----+-----+-----+-----+-----+-----+-----+-----------------------------+------+
    # |  1  |  1  |  1  |  0  |  0  |  0  |  0  |  0  | 1/16  duty                  |  —   |
    # |  1  |  1  |  1  |  0  |  0  |  0  |  0  |  1  | 2/16  duty                  |  —   |
    # |  1  |  1  |  1  |  0  |  0  |  0  |  1  |  0  | 3/16  duty                  |  —   |
    # |  1  |  1  |  1  |  0  |  0  |  0  |  1  |  1  | 4/16  duty                  |  —   |
    # |  1  |  1  |  1  |  0  |  0  |  1  |  0  |  0  | 5/16  duty                  |  —   |
    # |  1  |  1  |  1  |  0  |  0  |  1  |  0  |  1  | 6/16  duty                  |  —   |
    # |  1  |  1  |  1  |  0  |  0  |  1  |  1  |  0  | 7/16  duty                  |  —   |
    # |  1  |  1  |  1  |  0  |  0  |  1  |  1  |  1  | 8/16  duty                  |  —   |
    # |  1  |  1  |  1  |  0  |  1  |  0  |  0  |  0  | 9/16  duty                  |  —   |
    # |  1  |  1  |  1  |  0  |  1  |  0  |  0  |  1  | 10/16 duty                  |  —   |
    # |  1  |  1  |  1  |  0  |  1  |  0  |  1  |  0  | 11/16 duty                  |  —   |
    # |  1  |  1  |  1  |  0  |  1  |  0  |  1  |  1  | 12/16 duty                  |  —   |
    # |  1  |  1  |  1  |  0  |  1  |  1  |  0  |  0  | 13/16 duty                  |  —   |
    # |  1  |  1  |  1  |  0  |  1  |  1  |  0  |  1  | 14/16 duty                  |  —   |
    # |  1  |  1  |  1  |  0  |  1  |  1  |  1  |  0  | 15/16 duty                  |  —   |
    # |  1  |  1  |  1  |  0  |  1  |  1  |  1  |  1  | 16/16 duty                  |  Y   |
    # +-----+-----+-----+-----+-----+-----+-----+-----+-----------------------------+------+

    # 0b11100111 = 0xE7
    # The command to send for half brightness is 0xE7
    i2c.writeto(ADDR, bytes([0xE7]))

    # Writing digits to the display

    # segments for lower byte
    SEG_A  = 0x01  # top horizontal
    SEG_B  = 0x02  # upper right vertical
    SEG_C  = 0x04  # lower right vertical
    SEG_D  = 0x08  # bottom horizontal
    SEG_E  = 0x10  # lower left vertical
    SEG_F  = 0x20  # upper left vertical
    SEG_G1 = 0x40  # middle left horizontal
    SEG_G2 = 0x80  # middle right horizontal

    # segments for upper byte
    SEG_H  = 0x01  # upper left diagonal  (\)
    SEG_I  = 0x02  # upper vertical
    SEG_J  = 0x04  # upper right diagonal (/)
    SEG_K  = 0x08  # lower left diagonal  (/)
    SEG_L  = 0x10  # lower vertical
    SEG_M  = 0x20  # lower right diagonal (\)
    SEG_DP = 0x40  # decimal point

    # --- Character Map ---
    # Format: 'Character': [Lower Byte, Upper Byte]
    CHAR_MAP = {
        # Numbers
        '0': [SEG_A | SEG_B | SEG_C | SEG_D | SEG_E | SEG_F, 0x00],
        '1': [SEG_B | SEG_C, 0x00],
        '2': [SEG_A | SEG_B | SEG_D | SEG_E | SEG_G1 | SEG_G2, 0x00],
        '3': [SEG_A | SEG_B | SEG_C | SEG_D | SEG_G2, 0x00],
        '4': [SEG_B | SEG_C | SEG_F | SEG_G1 | SEG_G2, 0x00],
        '5': [SEG_A | SEG_C | SEG_D | SEG_F | SEG_G1 | SEG_G2, 0x00],
        '6': [SEG_A | SEG_C | SEG_D | SEG_E | SEG_F | SEG_G1 | SEG_G2, 0x00],
        '7': [SEG_A | SEG_B | SEG_C, 0x00],
        '8': [SEG_A | SEG_B | SEG_C | SEG_D | SEG_E | SEG_F | SEG_G1 | SEG_G2, 0x00],
        '9': [SEG_A | SEG_B | SEG_C | SEG_D | SEG_F | SEG_G1 | SEG_G2, 0x00],

        # Letters
        'A': [SEG_A | SEG_B | SEG_C | SEG_E | SEG_F | SEG_G1 | SEG_G2, 0x00],
        'B': [SEG_A | SEG_B | SEG_C | SEG_D | SEG_G2, SEG_I | SEG_L], 
        'C': [SEG_A | SEG_D | SEG_E | SEG_F, 0x00],
        'D': [SEG_A | SEG_B | SEG_C | SEG_D, SEG_I | SEG_L],
        'E': [SEG_A | SEG_D | SEG_E | SEG_F | SEG_G1 | SEG_G2, 0x00],
        'F': [SEG_A | SEG_E | SEG_F | SEG_G1 | SEG_G2, 0x00],
        'G': [SEG_A | SEG_C | SEG_D | SEG_E | SEG_F | SEG_G2, 0x00],
        'H': [SEG_B | SEG_C | SEG_E | SEG_F | SEG_G1 | SEG_G2, 0x00],
        'I': [SEG_A | SEG_D, SEG_I | SEG_L], 
        'J': [SEG_B | SEG_C | SEG_D | SEG_E, 0x00],
        'K': [SEG_E | SEG_F | SEG_G1, SEG_J | SEG_M],
        'L': [SEG_D | SEG_E | SEG_F, 0x00],
        'M': [SEG_B | SEG_C | SEG_E | SEG_F, SEG_H | SEG_J],
        'N': [SEG_B | SEG_C | SEG_E | SEG_F, SEG_H | SEG_M],
        'O': [SEG_A | SEG_B | SEG_C | SEG_D | SEG_E | SEG_F, 0x00],
        'P': [SEG_A | SEG_B | SEG_E | SEG_F | SEG_G1 | SEG_G2, 0x00],
        'Q': [SEG_A | SEG_B | SEG_C | SEG_D | SEG_E | SEG_F, SEG_M],
        'R': [SEG_A | SEG_B | SEG_E | SEG_F | SEG_G1 | SEG_G2, SEG_M],
        'S': [SEG_A | SEG_C | SEG_D | SEG_F | SEG_G1 | SEG_G2, 0x00],
        'T': [SEG_A, SEG_I | SEG_L],
        'U': [SEG_B | SEG_C | SEG_D | SEG_E | SEG_F, 0x00],
        'V': [SEG_E | SEG_F, SEG_J | SEG_K],
        'W': [SEG_B | SEG_C | SEG_E | SEG_F, SEG_K | SEG_M],
        'X': [0x00, SEG_H | SEG_J | SEG_K | SEG_M],
        'Y': [0x00, SEG_H | SEG_J | SEG_L],
        'Z': [SEG_A | SEG_D, SEG_J | SEG_K],

        # Symbols
        ' ': [0x00, 0x00], # Space
        '-': [SEG_G1 | SEG_G2, 0x00],
        '.': [0x00, SEG_DP],
        '*': [SEG_G1 | SEG_G2, SEG_H | SEG_I | SEG_J | SEG_K | SEG_L | SEG_M],
        '+': [SEG_G1 | SEG_G2, SEG_I | SEG_L],
        '?': [SEG_A | SEG_B | SEG_G2, SEG_L]
    }

    def get_digit(char):
        """
        Returns the [lower_byte, upper_byte] for a given character.
        Defaults to a blank space if the character isn't in the map.
        """
        # Convert to string and uppercase to ensure matching
        char = str(char).upper() 
        return CHAR_MAP.get(char, [0x00, 0x00])

    # --- Usage Example ---

    # digit 0 → RAM address 0x00
    # digit 1 → RAM address 0x02
    # digit 2 → RAM address 0x04
    # digit 3 → RAM address 0x06

    # digit = [0x08, 0x10]
    # digit_address = 0x02

    i2c.writeto(ADDR, bytes([0x00] + get_digit("M") ))
    i2c.writeto(ADDR, bytes([0x02] + get_digit("A") ))
    i2c.writeto(ADDR, bytes([0x04] + get_digit("T") ))
    i2c.writeto(ADDR, bytes([0x06] + get_digit("H") ))

    # 4. Turn on the display and set the hardware blink rate

    # +-------------+-----+-----+-----+-----+-----+-----+-----+-----+----------------+--------------------------------------------+------+
    # | Name        | D15 | D14 | D13 | D12 | D11 | D10 | D9  | D8  | Option         | Description                                | Def. |
    # +-------------+-----+-----+-----+-----+-----+-----+-----+-----+----------------+--------------------------------------------+------+
    # | Display set |  1  |  0  |  0  |  0  |  X  |  B1 |  B0 |  D  | {D} Write only | Defines Display on/off status.             | 80H  |
    # |             |     |     |     |     |     |     |     |     |                |  {0}: Display off                          |      |
    # |             |     |     |     |     |     |     |     |     |                |  {1}: Display on                           |      |
    # |             |     |     |     |     |     |     |     |     +----------------+--------------------------------------------+      |
    # |             |     |     |     |     |     |     |     |     | {B1,B0}        | Defines the blinking frequency.            |      |
    # |             |     |     |     |     |     |     |     |     | Write only     |  {0,0} = Blinking OFF                      |      |
    # |             |     |     |     |     |     |     |     |     |                |  {0,1} = 2Hz                               |      |
    # |             |     |     |     |     |     |     |     |     |                |  {1,0} = 1Hz                               |      |
    # |             |     |     |     |     |     |     |     |     |                |  {1,1} = 0.5Hz                             |      |
    # +-------------+-----+-----+-----+-----+-----+-----+-----+-----+----------------+--------------------------------------------+------+

    # 0b10001000 = 0x81
    # The command to send is 0x21 (turn display on, with blinking off)
    i2c.writeto(ADDR, bytes([0x81]))

    time.sleep(3)

    i2c.writeto(ADDR, bytes([0x00] + get_digit("I") + get_digit("S") + get_digit(" ") + get_digit(" ") ))

    time.sleep(3)

    i2c.writeto(ADDR, bytes([0x00] + get_digit("C") + get_digit("O") + get_digit("O") + get_digit("L") ))

    time.sleep(3)

    # 5. Turn off the display
    # Base Blink Command (0x80) with the Display On bit cleared (0x00) = 0x80
    i2c.writeto(ADDR, bytes([0x80]))

finally:
    i2c.unlock()
    i2c.deinit()
    print("\nBus unlocked and cleaned up.")

print("shutting down...")

led.value = False
