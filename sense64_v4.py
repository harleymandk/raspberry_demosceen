#!/usr/bin/env python3
"""SENSE64 v4.6 — dedicated oldschool greetings scroller."""
import math
import random
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

TEXT = columns_for('   GREETINGS TO ALL OLD SCHOOL CODERS - 64 PIXELS OF GLORY! RASPBERRY PI RULEZ!   ')
INTRO = columns_for('   MIRROR   ')
GREETINGS_MESSAGE = (
    '   YO DEMOSCENERS! MIRROR SENDS MEGA GREETINGS TO... '
    '1001 CREW - THE JUDGES - CREST - BLACK MAIL - FAIRLIGHT - '
    'TRIAD - HORIZON - OXYRON - BONZAI - CENSOR DESIGN! '
    'SPECIAL RESPECT TO ALL DANISH AMIGA/C64 CODERS! '
    'KEEP THE SCENE ALIVE! KEEP THE PIXELS MOVING! '
    'SIGNED: HARLEYMAN AND BYTEBENDER OF MIRROR! '
    '64 PIXELS! NO LIMITS! SENSE64 RULEZ! '
    'SEE YOU AT THE NEXT COPY PARTY!   '
)
GREETINGS = columns_for(GREETINGS_MESSAGE)
GREETINGS_SPEED = 8.0
GREETINGS_DURATION = (len(GREETINGS) + 8) / GREETINGS_SPEED + 3.0

SCENES = [
    ('INTRO', 24), ('DOUBLE SINE', 20), ('RASTER MADNESS', 18),
    ('PLASMA', 16), ('3D TUNNEL', 14), ('RUBBER DUCK', 22),
    ('FIRE64', 14), ('SPACE INVADERS', 17), ('BOUNCING BALL', 14),
    ('MATRIX RAIN', 14), ('DUCK PARTY', 24), ('ROTATING CUBE', 16),
    ('PAC DOT', 14), ('HYPNO SPIRAL', 14),
    ('GREETINGS', GREETINGS_DURATION),
]

scene = 0
auto_mode = True
wave_strength = 1.0
scroll_speed = 8.0
scene_started = time.monotonic()
start = scene_started
TRANSITION_SECONDS = 1.8
FADE_OUT_SECONDS = 0.8
BLACK_PAUSE_SECONDS = 0.25
FADE_IN_SECONDS = 0.9
EXPLOSION_SECONDS = 2.8
previous_scene = None
previous_frame = [(0, 0, 0)] * 64
explosion_particles = []
last_frame = [(0, 0, 0)] * 64


def rgb(v, intensity=1.0):
    return tuple(max(0, min(255, int((127 + 127 * math.sin(v + shift)) * intensity)))
                 for shift in (0, 2.094, 4.189))


def set_scene(number):
    global scene, scene_started, previous_frame, previous_scene, explosion_particles
    previous_scene = scene
    previous_frame = list(last_frame)
    # Capture the visible duck and water as the source for the explosion.
    explosion_particles = []
    if scene == 10 and number % len(SCENES) == 11:
        for i, color in enumerate(previous_frame):
            if max(color) > 35:
                x, y = i % 8, i // 8
                angle = math.atan2(y - 3.5, x - 3.5) + 0.32 * math.sin(i * 4.7)
                speed = 1.5 + (i * 7 % 9) * 0.26
                explosion_particles.append((x, y, color,
                                            math.cos(angle) * speed,
                                            math.sin(angle) * speed))
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
    morph = (math.sin(t * 0.05) + 1) * 0.5
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


def greetings_scroll(pixels, position, t):
    """One-pass rainbow sine scroller with blank entry and exit."""
    for x in range(8):
        index = position + x
        if not 0 <= index < len(GREETINGS):
            continue
        offset = round(1.5 + 1.1 * math.sin(x * 0.65 + t * 2.3))
        for fy, on in enumerate(GREETINGS[index]):
            y = fy + offset
            if on and 0 <= y < 8:
                pixels[y * 8 + x] = rgb(x * 0.5 + t * 2.0 + fy * 0.15)


def intro_bounce(pixels, local_t, global_t):
    """Scroll in, pause, sweep back and forth three times, then exit."""
    # Visible viewport is 8 columns; 3x5 text is wider than the display.
    # The sweep traverses all letters, rather than wrapping abruptly.
    left = -8
    right = len(INTRO) - 8
    enter_time = 2.0
    pause_time = 0.6
    sweep_time = 3.0
    cycles = 3
    elapsed = max(0.0, local_t)

    if elapsed < enter_time:
        pos = left + (right - left) * elapsed / enter_time
    else:
        elapsed -= enter_time
        if elapsed < pause_time:
            pos = right
        else:
            elapsed -= pause_time
            segment = int(elapsed / sweep_time)
            fraction = min(1.0, (elapsed % sweep_time) / sweep_time)
            fraction = fraction * fraction * (3 - 2 * fraction)
            if segment >= 2 * cycles:
                pos = right
            elif segment % 2 == 0:
                pos = right + (left - right) * fraction
            else:
                pos = left + (right - left) * fraction

    for x in range(8):
        index = round(pos) + x
        if not 0 <= index < len(INTRO):
            continue
        column = INTRO[index]
        # Keep the intro readable; a subtle vertical shimmer is enough.
        offset = 1 + round(0.5 + 0.5 * math.sin(global_t * 1.4 + x * 0.4))
        for fy, on in enumerate(column):
            if on:
                y = fy + offset
                pixels[y * 8 + x] = rgb(x * 0.45 + global_t * 1.7)


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



# 8x7 duck sprite. The final row of the display is animated water.
DUCK = (
    '........',
    '....YY..',
    '...YYYY.',
    '...YKYOO',
    '..YYYY..',
    'YYYYYYY.',
    'YYYYYYY.',
)
DUCK_COLORS = {
    'Y': (255, 205, 0),
    'O': (255, 95, 0),
    'K': (5, 5, 5),
}


def rubber_duck(pixels, t):
    # A full out-and-back trip in 40 seconds, including entering/exiting.
    # The sprite is eight pixels wide, so positions run from -8 to +8.
    travel = (t % 40.0) / 40.0
    if travel < 0.5:
        left = -8 + 16 * (travel * 2)
        facing_right = True
    else:
        left = 8 - 16 * ((travel - 0.5) * 2)
        facing_right = False

    # Moving water stays visible throughout the scene.
    for x in range(8):
        wave = math.sin(x * 1.2 + t * 2.0)
        pixels[7 * 8 + x] = (0, 35 + int(15 * (wave + 1)),
                              110 + int(45 * (wave + 1)))

    # Small periodic vertical movement (0 or -1 pixel).
    bob = -1 if math.sin(t * 2.2) > 0.65 else 0
    x0 = round(left)
    for sy, row in enumerate(DUCK):
        y = sy + bob
        if not 0 <= y < 7:
            continue
        for sx, symbol in enumerate(row):
            if symbol == '.':
                continue
            x = x0 + (sx if facing_right else 7 - sx)
            if 0 <= x < 8:
                pixels[y * 8 + x] = DUCK_COLORS[symbol]


# --- Additional v4.0 scenes ---
_rng = random.Random(64)
_fire = [[0.0] * 8 for _ in range(8)]
_rain = [_rng.uniform(-8, 0) for _ in range(8)]


def fire64(pixels, t):
    # Cellular fire: bottom row feeds heat into the rows above.
    _fire[7] = [_rng.uniform(0.6, 1.0) for _ in range(8)]
    for y in range(6, -1, -1):
        for x in range(8):
            heat = (_fire[y + 1][x] * 0.5 +
                    _fire[y + 1][(x - 1) % 8] * 0.25 +
                    _fire[y + 1][(x + 1) % 8] * 0.25)
            _fire[y][x] = max(0.0, heat - _rng.uniform(0.05, 0.20))
    for y in range(8):
        for x in range(8):
            h = _fire[y][x]
            pixels[y * 8 + x] = (int(255 * min(1, h * 2)),
                                  int(205 * max(0, (h - 0.25) * 1.5)),
                                  int(40 * max(0, h - 0.75)))


ALIEN = ('01010', '11111', '10101', '01010')

def invaders(pixels, t):
    # Marching alien and a tiny laser ship.
    shift = int(t * 2) % 12 - 5
    for sy, row in enumerate(ALIEN):
        for sx, c in enumerate(row):
            x = shift + sx
            if c == '1' and 0 <= x < 8:
                pixels[(sy + 1) * 8 + x] = (30, 240, 65)
    shipx = int(3.5 + 3 * math.sin(t * 0.8))
    for x in (shipx - 1, shipx, shipx + 1):
        if 0 <= x < 8:
            pixels[7 * 8 + x] = (70, 170, 255)
    if int(t * 2.5) % 3 == 0:
        for y in range(4, 7):
            pixels[y * 8 + shipx] = (255, 90, 30)


def bouncing_ball(pixels, t):
    cx = 3.5 + 2.5 * math.sin(t * 1.1)
    cy = 3.5 + 2.5 * math.sin(t * 1.7)
    for y in range(8):
        for x in range(8):
            dx, dy = x - cx, y - cy
            if dx * dx + dy * dy <= 4.0:
                tile = (int(dx * 1.6 + t * 2) + int(dy * 1.6)) % 2
                pixels[y * 8 + x] = (250, 60, 85) if tile else (245, 245, 245)


def matrix_rain(pixels, t):
    for x in range(8):
        _rain[x] += _rng.uniform(0.09, 0.25)
        if _rain[x] > 12:
            _rain[x] = _rng.uniform(-5, -1)
        head = int(_rain[x])
        for y in range(8):
            dist = head - y
            if 0 <= dist <= 4:
                b = int(255 * (1 - dist / 5))
                pixels[y * 8 + x] = (b // 7, b, b // 5)


def line(pixels, x0, y0, x1, y1, color):
    steps = max(1, int(math.ceil(max(abs(x1-x0), abs(y1-y0)) * 2)))
    for i in range(steps + 1):
        f = i / steps
        x = round(x0 + (x1 - x0) * f)
        y = round(y0 + (y1 - y0) * f)
        if 0 <= x < 8 and 0 <= y < 8:
            pixels[y * 8 + x] = color


def rotating_cube(pixels, t):
    vertices = []
    a, b = t * 0.9, t * 0.65
    for x in (-1, 1):
        for y in (-1, 1):
            for z in (-1, 1):
                xr = x * math.cos(a) - z * math.sin(a)
                zr = x * math.sin(a) + z * math.cos(a)
                yr = y * math.cos(b) - zr * math.sin(b)
                zz = y * math.sin(b) + zr * math.cos(b)
                scale = 6 / (4.5 + zz)
                vertices.append((3.5 + xr * scale, 3.5 + yr * scale))
    for i in range(8):
        for bit in (1, 2, 4):
            j = i ^ bit
            if j > i:
                line(pixels, *vertices[i], *vertices[j],
                     (70, 200, 255) if bit == 1 else (250, 110, 220))


def pac_dot(pixels, t):
    cx = int(t * 2) % 12 - 2
    cy = 3
    open_mouth = int(t * 5) % 2 == 0
    for y in range(8):
        for x in range(8):
            dx, dy = x - cx, y - cy
            if dx * dx + dy * dy <= 4 and not (open_mouth and dx > 0 and abs(dy) <= dx):
                pixels[y * 8 + x] = (255, 220, 0)
    for x in range(8):
        if x > cx + 2 and x % 2 == 0:
            pixels[3 * 8 + x] = (255, 230, 130)
    ghost_x = cx - 4
    for yy, row in enumerate(('010', '111', '101')):
        for xx, c in enumerate(row):
            gx, gy = ghost_x + xx, yy + 2
            if c == '1' and 0 <= gx < 8:
                pixels[gy * 8 + gx] = (240, 50, 160)


def hypno_spiral(pixels, t):
    for y in range(8):
        for x in range(8):
            dx, dy = x - 3.5, y - 3.5
            theta = math.atan2(dy, dx)
            radius = math.hypot(dx, dy)
            v = theta * 2.0 + radius * 2.7 - t * 3.5
            strength = 0.15 + 0.85 * (1 + math.sin(v)) / 2
            pixels[y * 8 + x] = rgb(v * 0.7 + t, strength)


# Smaller, purpose-built duck and duckling sprites for the 8x8 canvas.
MOTHER = ('..YY.', '.YYYY', '.YKYO', 'YYYYY', '.YYY.')
BABY = ('..Y', '.YY', 'YYO')

def duck_party(pixels, t):
    for x in range(8):
        wave = math.sin(x * 1.2 + t * 2)
        pixels[7 * 8 + x] = (0, 45, int(120 + 55 * (wave + 1) / 2))
    # 24-second round trip; duckling follows behind.
    u = (t % 24) / 12
    right = u < 1
    lead = -6 + 17 * u if right else 11 - 17 * (u - 1)
    bob = 1 if math.sin(t * 2) > 0.6 else 0
    for sprite, left, top in ((MOTHER, round(lead), 1 + bob),
                              (BABY, round(lead - 4 if right else lead + 6), 4)):
        width = len(sprite[0])
        for sy, row in enumerate(sprite):
            for sx, c in enumerate(row):
                x = left + (sx if right else width - 1 - sx)
                y = top + sy
                if c != '.' and 0 <= x < 8 and 0 <= y < 7:
                    pixels[y * 8 + x] = {
                        'Y': (255, 215, 0), 'K': (5, 5, 5),
                        'O': (255, 100, 0)
                    }[c]
    fish_x = int(3.5 + 3 * math.sin(t * 0.7))
    pixels[6 * 8 + fish_x] = (40, 230, 210)


def render(t, local_t):
    pixels = [(0, 0, 0)] * 64
    if scene == 0:
        intro_bounce(pixels, local_t, t)
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
    elif scene == 5:
        rubber_duck(pixels, local_t)
    elif scene == 6:
        fire64(pixels, t)
    elif scene == 7:
        invaders(pixels, local_t)
    elif scene == 8:
        bouncing_ball(pixels, local_t)
    elif scene == 9:
        matrix_rain(pixels, t)
    elif scene == 10:
        duck_party(pixels, local_t)
    elif scene == 11:
        rotating_cube(pixels, local_t)
    elif scene == 12:
        pac_dot(pixels, local_t)
    elif scene == 13:
        hypno_spiral(pixels, t)
    elif scene == 14:
        # Play the complete greetings text once, then loop back to intro.
        # Start after the normal fade-in so no greetings are skipped.
        elapsed = max(0.0, local_t - FADE_OUT_SECONDS - BLACK_PAUSE_SECONDS)
        position = int(elapsed * GREETINGS_SPEED) - 8
        greetings_scroll(pixels, position, t)

    # Duck Party -> Rotating Cube: the duck explodes into coloured pixels,
    # which gather into the new scene. No extra LED hardware is required.
    if previous_scene == 10 and scene == 11 and local_t < EXPLOSION_SECONDS:
        p = max(0.0, local_t / EXPLOSION_SECONDS)
        output = [(0, 0, 0)] * 64
        targets = [i for i, c in enumerate(pixels) if max(c) > 20]
        if not targets:
            targets = [27, 28, 35, 36]
        for n, (sx, sy, color, vx, vy) in enumerate(explosion_particles):
            txi = targets[n % len(targets)]
            tx, ty = txi % 8, txi // 8
            # First burst outwards, then regroup into the rotating cube.
            if p < 0.48:
                q = p / 0.48
                x, y = sx + vx * q, sy + vy * q
                brightness = 1.0 - 0.35 * q
            else:
                q = (p - 0.48) / 0.52
                q = q * q * (3 - 2 * q)
                bx, by = sx + vx, sy + vy
                x, y = bx * (1 - q) + tx * q, by * (1 - q) + ty * q
                brightness = 0.65 + 0.35 * q
            ix, iy = round(x), round(y)
            if 0 <= ix < 8 and 0 <= iy < 8:
                idx = iy * 8 + ix
                c = tuple(int(v * brightness) for v in color)
                output[idx] = tuple(max(a, b) for a, b in zip(output[idx], c))
        # The cube fades in during the regrouping phase.
        fade = max(0.0, min(1.0, (p - 0.55) / 0.45))
        fade = fade * fade * (3 - 2 * fade)
        return [tuple(int(a * (1 - fade) + b * fade)
                      for a, b in zip(old, new))
                for old, new in zip(output, pixels)]

    # Special transition: Matrix rain reveals Duck Party from top to bottom.
    # Each column has a slightly different reveal timing, like falling rain.
    if previous_scene == 9 and scene == 10 and local_t < TRANSITION_SECONDS:
        progress = max(0.0, local_t / TRANSITION_SECONDS)
        result = []
        for y in range(8):
            for x in range(8):
                # Deterministic column offsets: no random flicker.
                delay = (x * 3 % 7) * 0.055
                edge = (progress - delay) / (1.0 - delay)
                boundary = edge * 10 - 1.0
                if y < boundary:
                    result.append(pixels[y * 8 + x])
                elif y < boundary + 1.0:
                    # Bright green falling leading edge.
                    result.append((20, 210, 55))
                else:
                    result.append(previous_frame[y * 8 + x])
        return result

    # Standard transition: old frame fades to black, then new scene fades in.
    # Smoothstep makes the beginning and end of each fade less abrupt.
    def smoothstep(value):
        value = max(0.0, min(1.0, value))
        return value * value * (3.0 - 2.0 * value)

    if local_t < FADE_OUT_SECONDS:
        brightness = 1.0 - smoothstep(local_t / FADE_OUT_SECONDS)
        source = previous_frame
    elif local_t < FADE_OUT_SECONDS + BLACK_PAUSE_SECONDS:
        return [(0, 0, 0)] * 64
    elif local_t < FADE_OUT_SECONDS + BLACK_PAUSE_SECONDS + FADE_IN_SECONDS:
        elapsed = local_t - FADE_OUT_SECONDS - BLACK_PAUSE_SECONDS
        brightness = smoothstep(elapsed / FADE_IN_SECONDS)
        source = pixels
    else:
        return pixels

    return [tuple(int(channel * brightness) for channel in color)
            for color in source]


def main():
    global last_frame
    hat.stick.direction_any = joystick
    set_scene(0)
    # Start at the fade-in phase for the very first scene.
    global scene_started
    scene_started -= FADE_OUT_SECONDS + BLACK_PAUSE_SECONDS
    last = time.monotonic()
    try:
        while True:
            now = time.monotonic()
            if auto_mode and now - scene_started >= SCENES[scene][1]:
                set_scene(scene + 1)
            local_t = now - scene_started
            last_frame = render(now - start, local_t)
            hat.set_pixels(last_frame)
            delay = 1 / 25 - (time.monotonic() - now)
            if delay > 0:
                time.sleep(delay)
    except KeyboardInterrupt:
        pass
    finally:
        hat.clear()


if __name__ == '__main__':
    main()
