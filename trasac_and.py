
from sense_hat import SenseHat
import time
import math

hat = SenseHat()
hat.low_light = True

Y = (255, 210, 0)   # Gul
O = (255, 100, 0)   # Orange
K = (5, 5, 5)       # Oeje
B = (0, 60, 180)    # Vand
D = (0, 0, 0)       # Baggrund

duck = [
    "........",
    "....YY..",
    "...YYYY.",
    "...YKYO.",
    "...YYYY.",
    "..YYYYY.",
    "YYYYYYY.",
    "........"
]

palette = {
    ".": D,
    "Y": Y,
    "O": O,
    "K": K
}

t = 0.0

try:
    while True:
        pixels = [D] * 64

        # Langsom vuggen
        bob = round(math.sin(t) * 0.5)

        for y in range(7):
            for x in range(8):
                sy = y - bob

                if 0 <= sy < 7:
                    c = duck[sy][x]
                    if c != ".":
                        pixels[y * 8 + x] = palette[c]

        # Animeret vand
        for x in range(8):
            wave = math.sin(x * 1.2 + t * 2)
            blue = int(100 + 50 * wave)
            pixels[7 * 8 + x] = (0, 30, blue)

        hat.set_pixels(pixels)
        t += 0.18
        time.sleep(0.12)

except KeyboardInterrupt:
    hat.clear()
