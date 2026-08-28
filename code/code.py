import time
import board
import busio
import digitalio
import adafruit_ssd1306

# Setup I2C display (SDA = D4/GP8, SCL = D5/GP9)
i2c = busio.I2C(board.SCL, board.SDA)
display = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c)

# Clear display
display.fill(0)
display.text("Calc Ready", 0, 12, 1)
display.show()

# Pin mapping based on schematic:
# Rows 1-4: D0 (GP2), D1 (GP4), D2 (GP10), D3 (GP11) -> Remember GP1 is D0
row_pins = [board.D0, board.D1, board.D2, board.D3]
# Cols 1-4: D7 (GP9), D8 (GP8), D9 (GP7), D10 (GP6) -> wait, let's map matching schematic labels:
# S1-S4 connect to pins 7, 8, 9, 10 on the right side:
# Looking at U1: Pin 7=PB08_A6_D6_TX, Pin 8=PB09_A7_D7_RX, Pin 9=PA7_A8_D8_SCK, Pin 10=PA5_A9_D9_MISO, Pin 11=PA6_A10_D10_MOSI
# Let's use standard digitalio setup for the 4 rows (outputs/inputs) and 4 columns.
# Rows: Pins 1, 2, 3, 4 (D0, D1, D2, D3)
# Cols: Pins 7, 8, 9, 10 (D6, D7, D8, D9 or similar mapping)

rows = [digitalio.DigitalInOut(p) for p in [board.D0, board.D1, board.D2, board.D3]]
cols = [digitalio.DigitalInOut(p) for p in [board.D6, board.D7, board.D8, board.D9]]

for r in rows:
    r.direction = digitalio.Direction.OUTPUT
    r.value = False

for c in cols:
    c.direction = digitalio.Direction.INPUT
    c.pull = digitalio.Pull.DOWN

# Keypad layout mapping (4x4)
keys = [
    ['1', '2', '3', '+'],
    ['4', '5', '6', '-'],
    ['7', '8', '9', '*'],
    ['C', '0', '=', '/']
]

current_input = ""
expression = ""

def update_display(text):
    display.fill(0)
    display.text("Calc:", 0, 0, 1)
    display.text(text[:16], 0, 16, 1) # Limit to 16 chars for 128x32 screen
    display.show()

def get_key():
    for r_idx, row in enumerate(rows):
        row.value = True
        for c_idx, col in enumerate(cols):
            if col.value:
                row.value = False
                time.sleep(0.2) # debounce
                return keys[r_idx][c_idx]
        row.value = False
    return None

update_display("0")

while True:
    key = get_key()
    if key:
        if key == 'C':
            current_input = ""
            expression = ""
            update_display("0")
        elif key == '=':
            try:
                # Evaluate expression safely
                result = str(eval(expression + current_input))
                update_display(result)
                expression = ""
                current_input = result
            except Exception:
                update_display("Error")
                current_input = ""
                expression = ""
        elif key in ['+', '-', '*', '/']:
            if current_input:
                expression += current_input + key
                current_input = ""
                update_display(expression)
        else:
            current_input += key
            update_display(expression + current_input)