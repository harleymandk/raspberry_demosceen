#!/usr/bin/env python3
"""SENSE64 v3.0 — five-scene demoscene show for the Sense HAT 8x8 LEDs."""
import math
import time
from sense_hat import SenseHat

hat = SenseHat()
hat.low_light = True

FONT = {
 'A':['010','101','111','101','101'], 'B':['110','101','110','101','110'],
 'C':['011','100','100','100','011'], 'D':['110','101','101','101','110'],
 'E':['111','100','110','100','111'], 'F':['111','100','110','100','100'],
 'G':['011','100','101','101','011'], 'H':['101','101','111','101','101'],
 'I':['111','010','010','010','111'], 'J':['001','001','001','101','010'],
 'K':['101','101','110','101','101'], 'L':['100','100','100','100','111'],
 'M':['101','111','111','101','101'], 'N':['101','111','111','111','101'],
 'O':['010','101','101','101','010'], 'P':['110','101','110','100','100'],
 'Q':['010','101','101','111','011'], 'R':['110','101','110','101','101'],
 'S':['011','100','010','001','110'], 'T':['111','010','010','010','010'],
 'U':['101','101','101','101','111'], 'V':['101','101','101','101','010'],
 'W':['101','101','111','111','101'], 'X':['101','101','010','101','101'],
 'Y':['101','101','010','010','010'], 'Z':['111','001','010','100','111'],
 '0':['111','101','101','101','111'], '1':['010','110','010','010','111'],
 '2':['110','001','010','100','111'], '3':['110','001','010','001','110'],
 '4':['101','101','111','001','001'], '5':['111','100','110','001','110'],
 '6':['011','100','110','101','010'], '7':['111','001','010','010','010'],
 '8':['111','101','111','101','111'], '9':['111','101','111','001','110'],
 '!':['1','1','1','0','1'], '.':['0','0','0','0','1'],
 '-':['000','000','111','000','000'], ' ':['000','000','000','000','000'],
}

def columns_for(message):
    result = []
    for char in message.upper():
        glyph = FONT.get(char, FONT[' '])
        result.extend([[row[x] == '1' for row in glyph] for x in range(len(glyph[0]))])
        result.append([False] * 5)
    return result

TEXT = columns_for('   GREETINGS TO ALL OLD SCHOOL CODERS - 64 PIXELS OF GLORY! SENSE64 RULEZ!   ')
INTRO = columns_for('   SENSE64   ')
SCENES = [('INTRO', 6), ('DOUBLE SINE', 22), ('RASTER MADNESS', 22), ('PLASMA', 18), ('3D TUNNEL', 14)]
scene = 0
auto_mode = True
wave_strength = 1.0
scroll_speed = 8.0
scene_started = time.monotonic()
start = scene_started


def rgb(v, intensity=1.0):
    return tuple(max(0, min(255, int((127 + 127 * math.sin(v + shift)) * intensity)))
                 for shift in (0, 2.094, 4.189))


def set_scene(number):
    global scene, scene_started
    scene = number % len(SCENES)
    scene_started = time.monotonic()
    print('Scene:', SCENES[scene][0])


def joystick(event):
    global auto_mode, wave_strength
    if event.action != 'pressed':
        return
    if event.direction == 'left':
        set_scene(scene - 1)
    elif event.direction == 'right':
        set_scene(scene + 1)
    elif event.direction == 'up':
        wave_strength = min(1.0, wave_strength + 0.1)
    elif event.direction == 'down':
        wave_strength = max(0.0, wave_strength - 0.1)
    elif event.direction == 'middle':
        auto_mode = not auto_mode
        print('Auto:', auto_mode)


def scroller(pixels, t, text=TEXT, double=True):
    # Fractional movement in time, displayed at integer pixel coordinates.
    pos = int(t * scroll_speed)
    morph = (math.sin(t * 0.35) + 1) * 0.5
    f1 = 0.35 + 0.45 * morph
    f2 = 1.1 + 0.65 * (1 - morph)
    for x in range(8):
        col = text[(pos + x) % len(text)]
        w1 = math.sin(x * f1 + t * 1.8)
        w2 = math.sin(x * f2 - t * 3.06) if double else 0
        displacement = (0.65 * w1 + (0.35 * w2 if double else 0))
        offset = round(1.5 + 1.5 * wave_strength * displacement)
        for fy, on in enumerate(col):
            y = fy + offset
            if on and 0 <= y < 8:
                pixels[y * 8 + x] = rgb(x * 0.45 + t * 2.4 + fy * 0.15)


def raster(pixels, t):
    for y in range(8):
        b = 0.06 + 0.22 * (1 + math.sin(y * 1.35 + t * 3)) / 2
        c = rgb(y * 0.7 + t * 1.4, b)
        for x in range(8):
            pixels[y * 8 + x] = c


def plasma(pixels, t):
    for y in range(8):
        for x in range(8):
            v = math.sin(x * 0.8 + t * 1.2) + math.sin(y * 0.7 - t) + math.sin((x + y) * 0.5 + t)
            pixels[y * 8 + x] = rgb(v * 2, 0.30)


def tunnel(pixels, t):
    for y in range(8):
        for x in range(8):
            dx = x - 3.5 + 0.5 * math.sin(t * 0.6)
            dy = y - 3.5 + 0.5 * math.cos(t * 0.7)
            radius = math.hypot(dx, dy)
            ring = (1 + math.cos(radius * 3.2 - t * 5)) * 0.5
            brightness = 0.06 + 0.75 * ring
            pixels[y * 8 + x] = rgb(radius * 1.5 - t * 1.8, brightness)


def render(t):
    pixels = [(0, 0, 0)] * 64
    if scene == 0:
        # Pulsing introductory scroller
        scroller(pixels, t, INTRO)
        pulse = 0.4 + 0.6 * (1 + math.sin(t * 5)) / 2
        pixels = [tuple(int(c * pulse) for c in p) for p in pixels]
    elif scene == 1:
        scroller(pixels, t)
    elif scene == 2:
        raster(pixels, t)
        scroller(pixels, t)
    elif scene == 3:
        plasma(pixels, t)
        scroller(pixels, t)
    elif scene == 4:
        tunnel(pixels, t)
    return pixels


def main():
    global scene_started
    hat.stick.direction_any = joystick
    set_scene(0)
    try:
        while True:
            now = time.monotonic()
            if auto_mode and now - scene_started >= SCENES[scene][1]:
                set_scene(scene + 1)
            t = now - start
            hat.set_pixels(render(t))
            time.sleep(1 / 30)
    except KeyboardInterrupt:
        pass
    finally:
        hat.clear()

if __name__ == '__main__':
    main()
