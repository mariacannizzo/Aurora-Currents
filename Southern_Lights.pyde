# ============================================================
# SOUTHERN LIGHTS  (Aurora Australis)
# Processing Python Mode
#
# Mouse over sky: swirl and interact
# Click: send a glowing wave through the curtains
# Mouse over water: create ripples
# ============================================================

import math
from java.lang import System

# Profiler (set SHOW_PROFILE = False to hide it)
SHOW_PROFILE = True
prof = {}
_lap_t = [0]


def lap_reset():
    _lap_t[0] = System.nanoTime()


def lap(name):
    n = System.nanoTime()
    d = (n - _lap_t[0]) / 1000000.0
    prof[name] = prof.get(name, d) * 0.9 + d * 0.1
    _lap_t[0] = n

# ============================================================
# SETTINGS
# ============================================================

W = 640
H = 720

S = 8   # aurora is drawn at 1/8 size then scaled up (much cheaper + softer)
BW = W // S
BH = H // S

# Smaller step = more detail, more processing
CSTEP = 30
NCOL = W // CSTEP + 3

LEVELS = 16
NP = 5
GLOW = 0.75   # overall light intensity (was 1.08, which blew out to white)

# Smooth natural movement (slightly slower than before)
TSPEED = 0.028

# Water reflection refresh frequency
REFLECTION_INTERVAL = 3

# Extra detail settings
BREATH_STRENGTH = 0.13
RAY_SHIMMER = 1.0
SURGE_STRENGTH = 0.35

# ---- NEW: mouse-interaction smoothing controls ----
MOUSE_FOLLOW = 0.30      # how softly the "virtual mouse" chases the real one
HOVER_RISE = 0.07       # how slowly the hover effect fades in
HOVER_FALL = 0.02       # how slowly the hover effect fades out
GRID_SMOOTH = 0.35       # how softly the flow grid eases to new values
HOVER_SPEED_BOOST = 0.40 # curtain speed boost while hovering
HOVER_BRIGHT_BOOST = 0.20  # curtain brightness boost while hovering
HOVER_WAVE_AMP = 35.0    # swirl strength
HOVER_WAVE_SPEED = 1.5   # swirl travel speed
HOVER_GLOW = 0.10        # extra glow right under the mouse
HOVER_RADIUS = 150.0     # size of that glow area
HOVER_PULL = -0.45       # negative = curtains lean AWAY from the mouse
CURTAIN_W = 88.0 / S         # width of each light column (wider = more blended)
BLUR_PASSES = 0          # softness of the aurora buffer (0 = off)

# ---- NEW: pushing / dragging the waves with the mouse ----
PUSH_RADIUS = 140.0      # how big an area of aurora the cursor drags along
PUSH_GAIN = 0.25         # how strongly cursor movement shoves the waves
PUSH_DECAY = 0.92       # how slowly the waves drift back (closer to 1 = longer)
PUSH_MAX = 60.0          # max shove distance in pixels

# ---- NEW: dispersing the lights around the cursor ----
DISPERSE_RADIUS = 155.0  # size of the area that scatters
DISPERSE_AMP = 120.0     # how far the light is blown outward
DISPERSE_SWIRL = 0.45    # sideways curl so it scatters organically
DISPERSE_FADE = 0.45     # how much the light thins out under the cursor

HORIZON = int(H * 0.80)
WATER_BOTTOM = int(H * 0.90)

VPY = -H * 0.9

MOON_X = W * 0.17
MOON_Y = H * 0.17
MOON_R = 19
MOON_ENABLED = False     # no moon: a dark sky lets the aurora and stars shine

# Southern Cross position
CROSS_X = W * 0.74
CROSS_Y = H * 0.27

# Person standing on the hill
PERSON_X = W * 0.20

# Glow along the horizon (yellow-green low, pink above it)
HAZE_GREEN = 46
HAZE_PINK = 26

LY0 = int(H * 0.55)
LAYER_H = HORIZON + 4 - LY0
LAYER_W = W + 60
SNOW_Y0 = HORIZON

# Aurora flow displacement grid
GROWS = 4
GY0 = H * 0.10
GSP = H * 0.18

gdx = [0.0] * (NCOL * GROWS)
gdy = [0.0] * (NCOL * GROWS)

# NEW: persistent "shove" the mouse leaves in the aurora
pushx = [0.0] * (NCOL * GROWS)
pushy = [0.0] * (NCOL * GROWS)

# Original colour palettes
PALETTES = [
    ((200, 255, 50), (255, 70, 150), (120, 50, 230)),
    ((150, 255, 80), (255, 50, 120), (90, 40, 220)),
    ((230, 255, 70), (255, 100, 170), (150, 60, 240)),
    ((120, 255, 110), (230, 60, 200), (80, 60, 255)),
    ((255, 230, 70), (255, 60, 130), (130, 40, 200))
]

WISP_COLS = [
    (255, 90, 170),
    (200, 80, 255),
    (170, 255, 90),
    (255, 120, 200),
    (130, 90, 255),
    (230, 255, 110)
]

HX = [
    math.exp(-((x - 7.5) / 3.9) ** 2)
    for x in range(16)
]

# ============================================================
# OBJECT COLLECTIONS
# ============================================================

stars = []
pleiades = []
allstars = []

curtains = []
ripples = []
wripples = []
wisps = []
shooters = []
flakes = []
clouds = []

pal_sprites = []
wisp_sprites = []

# ============================================================
# ANIMATION VARIABLES
# ============================================================

t = 0.0
last_time_ms = None
step = 1.0

hover = 0.0
last_move = -10000
last_spawn = 0

# NEW: smoothed "virtual" mouse position
mx = W * 0.5
my = H * 0.4
mvx = 0.0   # smoothed cursor velocity (pixels per frame)
mvy = 0.0

burst = 0.0
bx = W * 0.5
brad = 0.0

par = 0.0
vpx = W * 0.5

POLE_X = W * 0.70
POLE_Y = H * 0.16

# New aurora effects
breath = 1.0
surge = 0.0

# ============================================================
# GRAPHICS BUFFERS
# ============================================================

sky = None
buf = None
refl = None

far_l = None
mid_l = None
near_l = None

water_img = None
snowg = None

fog1 = None
fog2 = None
mist_a = None
mist_b = None

moon_glow = None
cloud_img = None

REFL_H = len(
    range(HORIZON + 1, WATER_BOTTOM, 4)
) * 4


# ============================================================
# HELPERS
# ============================================================

def mix(c1, c2, k):
    return (
        lerp(c1[0], c2[0], k),
        lerp(c1[1], c2[1], k),
        lerp(c1[2], c2[2], k)
    )


def make_sprite(c0, a0, c1, a1, scale, h=48):
    img = createImage(16, h, ARGB)
    img.loadPixels()

    for y in range(h):
        k = y / float(h - 1)
        c = mix(c0, c1, k)
        a = lerp(a0, a1, k) * scale

        r = int(c[0])
        g = int(c[1])
        b = int(c[2])

        for x in range(16):
            alpha = int(
                constrain(a * HX[x], 0, 255)
            )

            img.pixels[y * 16 + x] = color(
                r, g, b, alpha
            )

    img.updatePixels()
    return img


def make_wisp_sprite(col, n=32):
    img = createImage(n, n, ARGB)
    img.loadPixels()

    for y in range(n):
        for x in range(n):
            d = dist(
                x, y,
                (n - 1) / 2.0,
                (n - 1) / 2.0
            ) / (n / 2.0)

            if d < 1:
                a = 150 * (1 - d) * (1 - d)
            else:
                a = 0

            img.pixels[y * n + x] = color(
                col[0], col[1], col[2], int(a)
            )

    img.updatePixels()
    return img


def make_radial(
    n, col, amax, power=2.0, squash=1.0
):
    img = createImage(n, n, ARGB)
    img.loadPixels()

    for y in range(n):
        for x in range(n):
            dx = (x - (n - 1) / 2.0) / (n / 2.0)

            dy = (
                (y - (n - 1) / 2.0) /
                (n / 2.0) / squash
            )

            d = math.sqrt(dx * dx + dy * dy)

            if d < 1:
                a = amax * ((1 - d) ** power)
            else:
                a = 0

            img.pixels[y * n + x] = color(
                col[0], col[1], col[2], int(a)
            )

    img.updatePixels()
    return img


def make_fog(w, h, col, amax, fx, seed):
    img = createImage(w, h, ARGB)
    img.loadPixels()

    colA = [
        noise(x * fx + seed, 3.3)
        for x in range(w)
    ]

    for y in range(h):
        gy = math.exp(
            -((y - h * 0.55) / (h * 0.25)) ** 2
        )

        for x in range(w):
            a = amax * gy * (
                0.25 + 0.9 * colA[x]
            )

            img.pixels[y * w + x] = color(
                col[0], col[1], col[2],
                int(constrain(a, 0, 255))
            )

    img.updatePixels()
    return img


def scale_img(img, w, h):
    g = createGraphics(w, h)
    g.beginDraw()
    g.image(img, 0, 0, w, h)
    g.endDraw()
    return g


# ============================================================
# STARS
# ============================================================

class Star(object):

    def __init__(self, x, y, size, bright, tint_c):
        self.size = size
        self.bright = bright
        self.tint = tint_c

        self.phase = random(TWO_PI)
        self.speed = random(0.6, 3.2)

        self.r = dist(x, y, POLE_X, POLE_Y)

        self.a0 = math.atan2(
            y - POLE_Y,
            x - POLE_X
        )

    def pos(self, rot):
        a = self.a0 + rot

        return (
            POLE_X + math.cos(a) * self.r,
            POLE_Y + math.sin(a) * self.r
        )


# ============================================================
# AURORA RIPPLES
# ============================================================

class Ripple(object):

    def __init__(self, x, y, amp):
        self.x = x
        self.y = y
        self.amp = amp

        self.radius = 0.0
        self.life = 1.0

    def update(self):
        # Slower expansion and slower fade
        # than before so the wave drifts
        # instead of snapping across the sky.
        self.radius += 4.2 * step
        self.life *= 0.989 ** step

        return (
            self.life > 0.04 and
            self.radius < 1100
        )


# ============================================================
# WATER RIPPLES
# ============================================================

class WRipple(object):

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.r = 2.0
        self.life = 1.0


# ============================================================
# GLOW WISPS
# ============================================================

class Wisp(object):

    def __init__(self, x, y, vx, vy):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy

        self.size = random(12, 26)
        self.life = 1.0
        self.decay = random(0.007, 0.013)

        self.spr = int(
            random(len(wisp_sprites))
        )

    def update(self):
        n = noise(
            self.x * 0.006,
            self.y * 0.006,
            t * 0.4
        ) * TWO_PI * 2

        # Gentler steering force
        self.vx += math.cos(n) * 0.10 * step
        self.vy += (
            math.sin(n) * 0.10 - 0.01
        ) * step

        drag = 0.982 ** step

        self.vx *= drag
        self.vy *= drag

        self.x += self.vx * step
        self.y += self.vy * step

        self.size += 0.25 * step
        self.life -= self.decay * step

        return (
            self.life > 0 and
            self.y < HORIZON
        )


# ============================================================
# SHOOTING STARS
# ============================================================

class Shooter(object):

    def __init__(self):
        self.x = random(W * 0.2, W)
        self.y = random(0, H * 0.35)

        ang = random(0.35, 0.8)
        spd = random(10, 17)

        self.vx = -math.cos(ang) * spd
        self.vy = math.sin(ang) * spd

        self.life = 1.0

    def update(self):
        self.x += self.vx * step
        self.y += self.vy * step
        self.life -= 0.025 * step

        return (
            self.life > 0 and
            self.y < HORIZON
        )


# ============================================================
# CLOUDS
# ============================================================

class Cloud(object):

    def __init__(self):
        self.x = random(-200, W)
        self.y = random(H * 0.04, H * 0.50)

        self.w = random(160, 310)
        self.sp = random(0.08, 0.25)
        self.a = random(25, 55)

        self.img = None
        self.ox = 0


# ============================================================
# AURORA CURTAINS
# ============================================================

class Curtain(object):

    def __init__(self, i):
        self.seed = random(1000)

        self.base = (
            H * (0.56 + 0.045 * i) +
            random(-16, 16)
        )

        self.height = random(330, 540)
        self.speed = random(0.14, 0.30)

        self.layer_alpha = [
            0.95, 1.05, 1.15, 1.05, 0.75
        ][i % 5]

        self.dscale = 0.9 + 0.1 * i

        # NEW: accumulated animation phase.
        # Previously the code used (t * speed) where speed
        # changed whenever the mouse moved. Because t keeps
        # growing, that made the noise lookup JUMP, which
        # caused the sudden fast/patchy movement.
        # Accumulating the phase makes speed changes smooth.
        self.phase = 0.0


# ============================================================
# SETUP
# ============================================================

def setup():
    global sky, buf, refl
    global far_l, mid_l, near_l
    global water_img, snowg
    global fog1, fog2, mist_a, mist_b
    global moon_glow, cloud_img

    # Smaller window
    size(640, 720)

    smooth()
    frameRate(60)

    noiseDetail(3, 0.5)
    noiseSeed(7)
    randomSeed(11)

    build_stars()

    for i in range(5):
        curtains.append(Curtain(i))

    # Pre-create the aurora light sprites
    for p in range(NP):
        bottom, mid, top = PALETTES[p]

        mid_top = mix(mid, top, 0.55)
        lst = []

        for L in range(LEVELS):
            sc = (
                (L + 1) / float(LEVELS) * GLOW
            )

            lst.append((
                make_sprite(
                    top, 0, mid_top, 150, sc
                ),
                make_sprite(
                    mid_top, 150, bottom, 250, sc
                ),
                make_sprite(
                    bottom, 250, bottom, 0, sc
                )
            ))

        pal_sprites.append(lst)

    for c in WISP_COLS:
        wisp_sprites.append(
            make_wisp_sprite(c)
        )

    moon_glow = make_radial(
        96, (190, 215, 255), 120, 2.2
    )

    cloud_img = make_radial(
        64, (6, 16, 30), 210, 1.6, 0.5
    )

    fog1 = make_fog(
        (W + 300) // 2, 35,
        (150, 70, 150), 60, 0.012, 5
    )

    fog2 = make_fog(
        (W + 300) // 2, 35,
        (170, 90, 140), 55, 0.015, 25
    )

    mist_a = make_fog(
        (W + 300) // 2, 35,
        (180, 200, 90), 36, 0.010, 45
    )

    mist_b = make_fog(
        (W + 300) // 2, 35,
        (200, 170, 110), 30, 0.014, 65
    )

    # Pre-scale atmospheric layers once
    fog1 = scale_img(fog1, W + 300, 70)
    fog2 = scale_img(fog2, W + 300, 70)

    mist_a = scale_img(mist_a, W + 300, 70)
    mist_b = scale_img(mist_b, W + 300, 60)

    for i in range(3):
        clouds.append(Cloud())

    for c in clouds:
        bake_cloud(c)

    # Lightweight snowfall
    for i in range(0):
        flakes.append([
            random(W),
            random(H),
            random(1.0, 2.6),
            random(TWO_PI)
        ])

    buf = createGraphics(BW, BH)
    refl = createGraphics(W, REFL_H)

    sky = build_sky()

    far_l = build_layer(
        far_y,
        (46, 26, 80),
        (20, 12, 42)
    )

    mid_l = build_layer(
        mid_y,
        (32, 20, 62),
        (14, 9, 30)
    )

    near_l = build_layer(
        near_y,
        (14, 10, 26),
        (6, 5, 14)
    )

    water_img = build_water()
    snowg = build_snow_layer()


# ============================================================
# PRE-RENDER CLOUDS
# ============================================================

def bake_cloud(c):
    w = c.w

    c.ox = int(w * 0.3) + 3

    pw = int(w * 1.6) + 6
    ph = int(w * 0.32) + 4

    g = createGraphics(pw, ph)
    g.beginDraw()
    g.clear()

    g.tint(255, c.a)

    g.image(
        cloud_img,
        c.ox, 0,
        w, w * 0.32
    )

    g.image(
        cloud_img,
        c.ox + w * 0.45,
        w * 0.05,
        w * 0.8,
        w * 0.26
    )

    g.image(
        cloud_img,
        c.ox - w * 0.30,
        w * 0.08,
        w * 0.7,
        w * 0.22
    )

    g.noTint()
    g.endDraw()

    c.img = g


# ============================================================
# BUILD STAR FIELD
# ============================================================

def build_stars():

    for i in range(260):
        x = random(-150, W + 150)
        y = random(-150, HORIZON)

        b = random(0.25, 1.0) ** 2
        pick = random(1)

        if pick < 0.6:
            c = (255, 255, 255)
        elif pick < 0.85:
            c = (190, 215, 255)
        else:
            c = (255, 230, 190)

        stars.append(Star(
            x, y,
            random(0.8, 1.9) +
            (2.2 if b > 0.8 else 0),
            b, c
        ))

    # Southern Cross and the two Pointer stars
    u = 26.0

    for dx_, dy_, sz_ in [
        (0.00, -1.00, 3.2),   # Gacrux
        (0.05, 1.00, 3.6),    # Acrux
        (0.75, -0.10, 3.2),   # Mimosa
        (-0.65, -0.25, 2.6),  # Delta Crucis
        (0.10, 0.15, 1.8),    # Epsilon Crucis
        (-2.90, 1.50, 3.8),   # Alpha Centauri
        (-2.55, 0.55, 3.4)    # Beta Centauri
    ]:
        pleiades.append(Star(
            CROSS_X + dx_ * u,
            CROSS_Y + dy_ * u,
            sz_,
            1.0,
            (200, 220, 255)
        ))

    allstars.extend(stars)
    allstars.extend(pleiades)


# ============================================================
# BUILD SKY AND MOON
# ============================================================

def build_sky():
    g = createGraphics(W, H)
    g.beginDraw()

    for y in range(H):
        f = constrain(
            y / float(HORIZON),
            0, 1
        )

        if f < 0.55:
            k = f / 0.55

            c = (
                lerp(3, 14, k),
                lerp(2, 6, k),
                lerp(14, 40, k)
            )

        else:
            k = (f - 0.55) / 0.45

            c = (
                lerp(14, 40, k),
                lerp(6, 14, k),
                lerp(40, 52, k)
            )

        g.stroke(c[0], c[1], c[2])
        g.line(0, y, W, y)

    g.noStroke()

    # Static Milky Way stars
    for i in range(550):
        along = random(-0.2, 1.2)

        x = W * along + randomGaussian() * 55
        y = (
            H * (0.05 + 0.45 * along) +
            randomGaussian() * 37
        )

        if 0 < y < HORIZON - 30:
            g.fill(
                210, 225, 255,
                random(40, 130)
            )

            g.rect(x, y, 1, 1)

    # Distant star cluster
    for i in range(6):
        g.fill(150, 110, 255, 6)

        g.ellipse(
            CROSS_X - 30,
            CROSS_Y + 10,
            90 - i * 11,
            75 - i * 9
        )

    if not MOON_ENABLED:
        g.endDraw()
        return g

    # Bake moon into the sky
    g.blendMode(ADD)
    g.tint(255, 210)

    g.image(
        moon_glow,
        MOON_X - 145,
        MOON_Y - 145,
        290, 290
    )

    g.noTint()
    g.blendMode(BLEND)

    g.fill(236, 240, 230)

    g.ellipse(
        MOON_X,
        MOON_Y,
        MOON_R * 2,
        MOON_R * 2
    )

    g.fill(205, 212, 204, 110)

    for cr in [
        (-6, -5, 8),
        (5, 3, 11),
        (-2, 8, 6),
        (8, -8, 5),
        (-9, 5, 4)
    ]:
        g.ellipse(
            MOON_X + cr[0],
            MOON_Y + cr[1],
            cr[2],
            cr[2]
        )

    g.endDraw()
    return g


# ============================================================
# MOUNTAINS
# ============================================================

def ridge_y(x, left):

    if left:
        edge = W * 0.46

        if x > edge:
            return None

        k = 1.0 - x / edge

        return (
            HORIZON -
            H * 0.115 * (k ** 1.5) *
            (
                0.65 +
                0.7 * noise(x * 0.018, 3)
            )
        )

    else:
        edge = W * 0.60

        if x < edge:
            return None

        k = (x - edge) / (W - edge)

        return (
            HORIZON -
            H * 0.13 * (k ** 1.3) *
            (
                0.65 +
                0.7 * noise(x * 0.016, 9)
            )
        )


def near_y(x):
    x2 = constrain(x, 0, W)
    r = ridge_y(x2, True)

    if r is None:
        r = ridge_y(x2, False)

    return r


def far_y(x):
    return (
        HORIZON -
        H * (
            0.045 +
            0.06 * noise(x * 0.006 + 70, 2)
        ) -
        10 * noise(x * 0.04, 8)
    )


def mid_y(x):
    return (
        HORIZON -
        H * (
            0.03 +
            0.10 * noise(x * 0.0045 + 30, 11)
        ) -
        8 * noise(x * 0.05, 5)
    )


def ground_y(x):
    return (
        H * 0.915 +
        (noise(x * 0.006, 40) - 0.5) * 55 -
        72 * math.exp(
            -((x - PERSON_X) / 150.0) ** 2
        )
    )


def vgrad(g, x, y0, y1, c0, c1, w=2):
    g.strokeWeight(w)

    n = max(
        1, int((y1 - y0) / 3)
    )

    for i in range(n):
        k = i / float(n)
        c = mix(c0, c1, k)

        g.stroke(c[0], c[1], c[2])

        ya = y0 + (y1 - y0) * k
        g.line(x, ya, x, ya + 4)


def build_layer(fn, c0, c1):
    g = createGraphics(LAYER_W, LAYER_H)
    g.beginDraw()

    g.translate(30, -LY0)

    for x in range(-30, W + 31, 2):
        y = fn(x)

        if y is None:
            continue

        vgrad(
            g, x, y,
            HORIZON + 3,
            c0, c1, 2
        )

    g.endDraw()
    return g


# ============================================================
# WATER BACKGROUND
# ============================================================

def build_water():
    h = WATER_BOTTOM - HORIZON + 1

    g = createGraphics(W, h)
    g.beginDraw()

    for y in range(h):
        k = y / float(h - 1)

        c = mix(
            (24, 14, 44),
            (7, 4, 18),
            k
        )

        g.stroke(c[0], c[1], c[2])
        g.line(0, y, W, y)

    g.endDraw()
    return g


# ============================================================
# DARK HILL FOREGROUND WITH PERSON AND RAILING
# ============================================================

def build_snow_layer():
    g = createGraphics(
        LAYER_W,
        H - SNOW_Y0
    )

    g.beginDraw()
    g.smooth()

    g.translate(30, -SNOW_Y0)

    # Dark hillside
    for x in range(-30, W + 31, 2):
        vgrad(
            g, x,
            ground_y(x), H,
            (14, 11, 22),
            (3, 3, 8), 2
        )

    # Grass tufts along the crest
    g.strokeWeight(1)

    for x in range(-30, W + 31, 3):
        gy = ground_y(x)

        g.stroke(10, 8, 16)

        g.line(
            x, gy + 1,
            x + random(-2, 2),
            gy - random(3, 9)
        )

    g.noStroke()

    px = PERSON_X
    py = ground_y(px) + 1

    # Wooden railing to the left of the person
    g.stroke(4, 4, 8)
    g.strokeWeight(2)

    prev = None

    for j in range(6):
        rx = px - 16 - j * 13
        ry = ground_y(rx)

        top = (rx, ry - 26)
        mid = (rx, ry - 14)

        g.line(rx, ry + 2, top[0], top[1])

        if prev is not None:
            g.line(prev[0][0], prev[0][1], top[0], top[1])
            g.line(prev[1][0], prev[1][1], mid[0], mid[1])

        prev = (top, mid)

    # Person with both arms raised
    g.stroke(4, 4, 8)
    g.strokeWeight(3.4)

    g.line(px - 4, py - 29, px - 11, py - 44)
    g.line(px + 4, py - 29, px + 11, py - 44)

    g.noStroke()
    g.fill(4, 4, 8)

    g.rect(px - 4.5, py - 17, 9, 17)
    g.rect(px - 5.5, py - 31, 11, 15)
    g.ellipse(px, py - 36, 9, 9)

    g.endDraw()
    return g


# ============================================================
# INTERACTIVE FLOW FIELD
# Uses the SMOOTHED mouse (mx, my) instead of the raw
# mouse, so quick mouse jumps no longer cause sudden
# jerks in the aurora.
# ============================================================

def wave_vec(x, y):

    dx = (
        noise(
            x * 0.003,
            y * 0.003,
            t * 0.35
        ) - 0.5
    ) * 115.0

    dy = (
        noise(
            x * 0.003 + 50,
            y * 0.003 + 50,
            t * 0.35
        ) - 0.5
    ) * 85.0

    if hover > 0.01:
        ex = x - mx
        ey = y - my

        dm = math.sqrt(
            ex * ex + ey * ey
        ) + 0.001

        ux = ex / dm
        uy = ey / dm

        wv = (
            hover * HOVER_WAVE_AMP *
            math.exp(-dm / 260.0) *
            math.sin(
                dm * 0.028 -
                t * HOVER_WAVE_SPEED
            )
        )

        dx += ux * wv - uy * wv * 0.7
        dy += uy * wv + ux * wv * 0.7

    for r in ripples:
        ex = x - r.x
        ey = y - r.y

        dm = math.sqrt(
            ex * ex + ey * ey
        ) + 0.001

        dd = dm - r.radius

        if abs(dd) < 200:
            wv = (
                r.amp * r.life *
                math.sin(dd * 0.04) *
                math.exp(
                    -(dd * dd) / 9000.0
                )
            )

            ux = ex / dm
            uy = ey / dm

            dx += ux * wv - uy * wv * 0.5
            dy += uy * wv * 1.2 + ux * wv * 0.5

    return dx, dy


# ============================================================
# SPAWN WISPS
# ============================================================

def spawn_wisps(x, y, n, vx, vy, burst_sp):

    for i in range(n):
        if len(wisps) >= 65:
            return

        a = random(TWO_PI)
        sp = random(0.4, burst_sp)

        wisps.append(Wisp(
            x + random(-12, 12),
            y + random(-12, 12),
            vx * 0.15 + math.cos(a) * sp,
            vy * 0.15 + math.sin(a) * sp
        ))


# ============================================================
# MOUSE CLICK
# ============================================================

def mousePressed():
    global burst, bx, brad

    burst = 1.0
    bx = mouseX
    brad = 0.0

    spawn_wisps(
        mouseX, mouseY,
        18, 0, 0, 4.0
    )

    ripples.append(
        Ripple(mouseX, mouseY, 85)
    )


# ============================================================
# UPDATE MOUSE INTERACTION
# ============================================================

def update_mouse():
    global hover, last_move, last_spawn
    global mx, my, mvx, mvy

    # Smoothly chase the real mouse. This removes
    # sudden jumps when the mouse moves fast or
    # enters the window from the edge.
    follow = 1.0 - (1.0 - MOUSE_FOLLOW) ** step

    old_mx = mx
    old_my = my

    mx += (mouseX - mx) * follow
    my += (mouseY - my) * follow

    # Velocity of the smoothed cursor, itself eased
    # so the push stays fluid
    mvx += ((mx - old_mx) / max(step, 0.3) - mvx) * 0.35
    mvy += ((my - old_my) / max(step, 0.3) - mvy) * 0.35

    moved = (
        mouseX != pmouseX or
        mouseY != pmouseY
    )

    if moved:
        last_move = millis()

        vx = mouseX - pmouseX
        vy = mouseY - pmouseY

        spd = math.sqrt(
            vx * vx + vy * vy
        )

        if (
            mouseY < HORIZON and
            spd > 1 and
            frameCount % 6 == 0
        ):
            spawn_wisps(
                mouseX, mouseY,
                1, vx, vy, 2.0
            )

        # Fewer, softer aurora ripples
        if (
            frameCount - last_spawn > 14 and
            spd > 2 and
            len(ripples) < 4
        ):
            ripples.append(Ripple(
                mouseX, mouseY,
                constrain(spd * 1.6, 25, 60)
            ))

            spawn_wisps(
                mouseX, mouseY,
                3, vx, vy, 2.5
            )

            last_spawn = frameCount

        if (
            HORIZON < mouseY < WATER_BOTTOM and
            frameCount % 6 == 0 and
            len(wripples) < 10
        ):
            wripples.append(
                WRipple(mouseX, mouseY)
            )

    target = (
        1.0 if millis() - last_move < 2400
        else 0.0
    )

    # Slower fade in / fade out
    rate = HOVER_RISE if target > hover else HOVER_FALL

    hover += (
        target - hover
    ) * (1.0 - (1.0 - rate) ** step)

    if (
        frameCount % 18 == 0 and
        len(wisps) < 40
    ):
        spawn_wisps(
            random(W),
            random(H * 0.2, H * 0.6),
            1, 0, 0, 1.2
        )

    for r in ripples[:]:
        if not r.update():
            ripples.remove(r)

    for w in wisps[:]:
        if not w.update():
            wisps.remove(w)


# ============================================================
# UPDATE DISPLACEMENT GRID
# Values now EASE toward their targets rather than
# snapping, which removes the patchy look.
# ============================================================

def update_flow_grid():

    ease = 1.0 - (1.0 - GRID_SMOOTH) ** step

    for i in range(NCOL):
        x = (i - 1) * CSTEP

        for j in range(GROWS):
            gy_pos = GY0 + j * GSP

            dx, dy = wave_vec(x, gy_pos)

            k = i * GROWS + j

            # --- Drag the waves along with the cursor ---
            # Cells near the cursor get shoved in the
            # direction the cursor is travelling, and slowly
            # drift back when it stops.
            ex = x - mx
            ey = gy_pos - my

            wgt = math.exp(
                -(ex * ex + ey * ey) /
                (2.0 * PUSH_RADIUS * PUSH_RADIUS)
            )

            pushx[k] += mvx * wgt * PUSH_GAIN * step
            pushy[k] += mvy * wgt * PUSH_GAIN * step

            pm = math.sqrt(
                pushx[k] * pushx[k] +
                pushy[k] * pushy[k]
            )

            if pm > PUSH_MAX:
                pushx[k] *= PUSH_MAX / pm
                pushy[k] *= PUSH_MAX / pm

            decay = PUSH_DECAY ** step

            pushx[k] *= decay
            pushy[k] *= decay

            dx += pushx[k]
            dy += pushy[k]

            # --- Disperse: blow the light outward from the cursor ---
            if hover > 0.01:
                dd_m = math.sqrt(ex * ex + ey * ey) + 0.001

                ux = ex / dd_m
                uy = ey / dd_m

                core = math.exp(
                    -(dd_m * dd_m) /
                    (2.0 * DISPERSE_RADIUS * DISPERSE_RADIUS)
                )

                # Stronger just outside the very centre,
                # with organic variation
                ring = min(1.0, dd_m / 60.0)

                vary = 0.7 + 0.6 * noise(
                    x * 0.01 + 20,
                    gy_pos * 0.01,
                    t * 0.8
                )

                amt = hover * DISPERSE_AMP * core * ring * vary

                dx += (ux - uy * DISPERSE_SWIRL) * amt
                dy += (uy + ux * DISPERSE_SWIRL) * amt

            gdx[k] += (dx - gdx[k]) * ease
            gdy[k] += (dy - gdy[k]) * ease


def samp(i, y):
    idx = constrain(
        (y - GY0) / GSP,
        0, GROWS - 1.001
    )

    j = int(idx)
    f = idx - j

    k = i * GROWS + j

    return (
        gdx[k] * (1 - f) +
        gdx[k + 1] * f,

        gdy[k] * (1 - f) +
        gdy[k + 1] * f
    )


# ============================================================
# AURORA BREATHING AND SURGES
# ============================================================

def update_aurora_energy():
    global breath, surge

    # Two overlapping slow rhythms
    # create irregular, organic expansion.
    slow_a = math.sin(t * 0.31)
    slow_b = math.sin(
        t * 0.17 + 1.4
    )

    breath = (
        1.0 +
        BREATH_STRENGTH *
        (slow_a * 0.65 + slow_b * 0.35)
    )

    # A soft surge occasionally passes
    # through the entire aurora.
    wave = max(
        0.0,
        math.sin(t * 0.19 - 0.8)
    )

    surge = SURGE_STRENGTH * wave ** 8


# ============================================================
# DRAW STARS
# ============================================================

def draw_stars(rot):
    noStroke()

    near = []

    for s in allstars:
        x, y = s.pos(rot)

        if (
            y > HORIZON - 25 or
            y < 0 or
            x < 0 or
            x > W
        ):
            continue

        tw = (
            0.55 +
            0.45 * math.sin(
                t * s.speed * 0.6 +
                s.phase
            )
        )

        a = s.bright * tw * 255
        sz = s.size

        if hover > 0.01:
            dx = x - mx
            dy = y - my

            d = math.sqrt(
                dx * dx + dy * dy
            )

            if d < 125:
                prox = 1.0 - d / 125.0

                a = min(
                    255,
                    a * (
                        1 + 1.3 * prox * hover
                    )
                )

                sz *= (
                    1 + 0.6 * prox * hover
                )

                x += (
                    dx / (d + 1) *
                    prox * hover * 5
                )

                y += (
                    dy / (d + 1) *
                    prox * hover * 5
                )

                near.append(
                    (d, x, y, prox)
                )

        if sz > 1.8:
            fill(
                s.tint[0],
                s.tint[1],
                s.tint[2],
                a * 0.15
            )

            rect(
                x - sz * 1.2,
                y - sz * 1.2,
                sz * 2.4,
                sz * 2.4
            )

        fill(
            s.tint[0],
            s.tint[1],
            s.tint[2],
            a
        )

        rect(
            x - sz * 0.5,
            y - sz * 0.5,
            sz, sz
        )

        if sz > 2.2:
            stroke(
                s.tint[0],
                s.tint[1],
                s.tint[2],
                a * 0.5
            )

            strokeWeight(1)

            L = sz * 3.0 * tw

            line(x - L, y, x + L, y)
            line(x, y - L, x, y + L)

            noStroke()

    if len(near) > 1:
        near.sort()

        n = min(
            len(near), 6
        )

        strokeWeight(1)

        for k in range(n - 1):
            a0 = near[k]
            a1 = near[k + 1]

            stroke(
                170, 210, 255,
                80 * hover *
                min(a0[3], a1[3])
            )

            line(
                a0[1], a0[2],
                a1[1], a1[2]
            )

        noStroke()


# ============================================================
# DRAW CLOUDS
# ============================================================

def draw_clouds():

    for c in clouds:
        c.x += c.sp * step

        if c.x > W + c.w:
            c.x = -c.w * 1.5

        image(
            c.img,
            c.x - c.ox,
            c.y
        )


# ============================================================
# FLOWING AURORA CURTAINS
# ============================================================

def draw_curtain(c):

    bright = (
        1.0 +
        HOVER_BRIGHT_BOOST * hover +
        surge * 0.75
    )

    # FIX: advance the curtain's own phase instead of
    # multiplying a growing time value by a changing speed.
    # Speed changes now only change the RATE of travel,
    # never cause a sudden jump in position.
    c.phase += (
        TSPEED * step * c.speed *
        (1.0 + HOVER_SPEED_BOOST * hover)
    )

    ph = c.phase   # replaces the old (t * spd)

    wp = CURTAIN_W

    swell = (
        0.90 +
        0.30 * noise(
            t * 0.2,
            c.seed
        )
    )

    # Breathing differs for each curtain.
    curtain_breath = (
        breath +
        0.045 * math.sin(
            t * 0.23 +
            c.seed
        )
    )

    for i in range(NCOL):
        x = (i - 1) * CSTEP
        nx = x * 0.0035

        # Wandering curtain motion
        sway = noise(
            nx + c.seed,
            ph
        ) - 0.5

        base = (
            c.base +
            sway * 230 +
            math.sin(
                x * 0.008 +
                t * 0.7 +
                c.seed
            ) * 30 +
            math.sin(
                x * 0.019 -
                t * 0.45 +
                c.seed * 2.1
            ) * 11
        )

        # Height changes organically.
        hgt = c.height * (
            0.55 +
            0.95 * noise(
                nx * 1.7 +
                c.seed + 77,
                ph * 1.3
            )
        )

        # Breathing changes the height
        # without translating the curtain.
        section_breath = (
            curtain_breath +
            0.035 * math.sin(
                x * 0.009 -
                t * 0.24 +
                c.seed
            )
        )

        hgt *= section_breath

        # Horizontal folding of the
        # original vertical curtain
        xw = (
            noise(
                nx * 2.0 +
                c.seed + 300,
                ph * 1.2
            ) - 0.5
        ) * 115

        xw += (
            math.sin(
                x * 0.013 +
                t * 0.5 +
                c.seed * 1.3
            ) * 11 +
            math.sin(
                x * 0.006 -
                t * 0.33 +
                c.seed * 0.7
            ) * 17
        )

        # Irregular ray brightness
        ray = noise(
            x * 0.010 +
            c.seed * 3,
            t * 0.35
        )

        # Softer contrast between neighbouring columns
        ray = constrain(
            0.55 +
            0.85 * ray * ray,
            0, 1.2
        )

        pulse = (
            0.78 +
            0.22 * math.sin(
                x * 0.011 -
                t * 1.6 +
                c.seed
            )
        )

        flick = (
            0.88 +
            0.12 * noise(
                x * 0.03,
                t * 1.6 +
                c.seed
            )
        )

        # Glowing energy travelling
        # gradually along the curtain
        surge_wave = (
            math.sin(
                x * 0.012 -
                t * 1.25 +
                c.seed
            ) * 0.5 + 0.5
        )

        local_surge = (
            surge *
            (0.55 + 0.45 * surge_wave)
        )

        hgt *= (
            1.0 + local_surge * 0.15
        )

        # Mouse-click wave
        bl = 0.0

        if burst > 0.02:
            dd = abs(x - bx) - brad

            bl = burst * (
                0.35 +
                0.9 * math.exp(
                    -(dd * dd) / 30000.0
                )
            )

            hgt *= (
                1.0 + 0.35 * bl
            )

        # Mouse proximity glow: brighten the part of the
        # aurora near the (smoothed) cursor
        mprox = 0.0

        if hover > 0.01:
            gdx_m = x - mx
            gdy_m = (base - hgt * 0.5) - my

            mprox = hover * math.exp(
                -(gdx_m * gdx_m + gdy_m * gdy_m) /
                (2.0 * HOVER_RADIUS * HOVER_RADIUS)
            )

        A = (
            c.layer_alpha *
            bright *
            ray *
            pulse *
            flick *
            swell *
            (1.0 + bl + local_surge + HOVER_GLOW * mprox) *
            (1.0 - DISPERSE_FADE * mprox)
        )

        lvl = int(
            constrain(
                A, 0, 0.999
            ) * LEVELS
        )

        if lvl <= 0:
            continue

        # Slowly drifting colours
        v = (
            (
                noise(
                    x * 0.0016 +
                    c.seed,
                    t * 0.03
                ) - 0.5
            ) * 1.7 +
            0.5 +
            0.12 * math.sin(
                t * 0.05 + c.seed
            )
        )

        p = int(
            constrain(
                v, 0, 0.999
            ) * NP
        )

        sA, sB, sC = pal_sprites[p][lvl]

        y_top = base - hgt
        y_mid = base - hgt * 0.5
        y_bot = base

        span = base - VPY

        # Perspective convergence
        xt0 = (
            x + (vpx - x) *
            (hgt / span)
        )

        xm0 = (
            x + (vpx - x) *
            (hgt * 0.5 / span)
        )

        # Interactive displacement
        dxt, dyt = samp(i, y_top)
        dxm, dym = samp(i, y_mid)
        dxb, dyb = samp(i, y_bot)

        s = c.dscale

        # Gentle lean toward the cursor
        pull = 0.0

        if mprox > 0.0:
            pull = (mx - x) * HOVER_PULL * mprox

        xt0 += pull
        xm0 += pull * 0.7

        xt = xt0 + xw + dxt * s
        yt = y_top + dyt * s

        xm = xm0 + xw * 0.7 + dxm * s
        ym = y_mid + dym * s

        xb = (
            x +
            xw * 0.35 +
            dxb * s * 0.8
        )

        yb = (
            y_bot +
            dyb * s * 0.8
        )

        # Draw silk-like glows
        if ym - yt > 2:
            buf.image(
                sA,
                (xt + xm) * 0.5 / S -
                wp / 2.0,
                yt / S,
                wp,
                (ym - yt) / S
            )

        if yb - ym > 2:
            buf.image(
                sB,
                (xm + xb) * 0.5 / S -
                wp / 2.0,
                ym / S,
                wp,
                (yb - ym) / S
            )

        buf.image(
            sC,
            xb / S - wp / 2.0,
            yb / S,
            wp,
            35.0 / S
        )

        # =================================================
        # SHIMMERING VERTICAL RAYS
        # =================================================

        if i % 3 == 0 and ym > yt + 10:

            shimmer = (
                math.sin(
                    x * 0.035 -
                    t * 2.7 +
                    c.seed
                ) * 0.5 + 0.5
            )

            shimmer *= (
                math.sin(
                    x * 0.012 +
                    t * 0.71 +
                    c.seed
                ) * 0.5 + 0.5
            )

            shimmer *= RAY_SHIMMER

            if shimmer > 0.18:

                alpha = (
                    (10 + 42 * shimmer) *
                    min(1.0, A) *
                    (1.0 + surge * 0.7)
                )

                buf.stroke(
                    255, 170, 225,
                    constrain(alpha * 0.4, 0, 28)
                )

                buf.strokeWeight(0.5)

                # A partial streak within
                # the upper curtain section
                f0 = 0.12
                f1 = 0.72

                rx0 = lerp(xt, xm, f0) / S
                ry0 = lerp(yt, ym, f0) / S

                rx1 = lerp(xt, xm, f1) / S
                ry1 = lerp(yt, ym, f1) / S

                buf.line(
                    rx0, ry0,
                    rx1, ry1
                )

    buf.noStroke()


# ============================================================
# DRAW AURORA INTO LOW-RESOLUTION BUFFER
# ============================================================

def horizon_haze():
    buf.noStroke()

    n = 22

    # Pink band rising from the horizon
    for j in range(n):
        k = j / float(n - 1)

        a = HAZE_PINK * math.exp(
            -((k - 0.62) / 0.30) ** 2
        ) * (
            0.85 + 0.15 * math.sin(t * 0.35 + k * 3.0)
        ) * breath

        buf.fill(255, 60, 150, a)

        buf.rect(
            0,
            (HORIZON - 340 + k * 300) / S,
            BW,
            300.0 / n / S + 0.5
        )

    # Yellow-green glow hugging the horizon
    for j in range(n):
        k = j / float(n - 1)

        a = HAZE_GREEN * (k ** 1.7) * (
            0.85 + 0.15 * math.sin(t * 0.5 + k * 2.0)
        ) * (0.9 + surge)

        buf.fill(170, 255, 50, a)

        buf.rect(
            0,
            (HORIZON - 200 + k * 200) / S,
            BW,
            200.0 / n / S + 0.5
        )


def draw_aurora_buffer():
    buf.beginDraw()
    buf.background(0)

    buf.blendMode(ADD)

    horizon_haze()

    for c in curtains:
        draw_curtain(c)

    # Mouse-created drifting wisps
    for p in wisps:
        a = p.life * p.life

        buf.tint(
            255, 150 * a
        )

        sz = p.size / S * 2.4

        buf.image(
            wisp_sprites[p.spr],
            p.x / S - sz / 2.0,
            p.y / S - sz * 0.35,
            sz,
            sz * 0.7
        )

    buf.noTint()
    buf.blendMode(BLEND)

    # Soften the buffer so neighbouring columns blend
    for _ in range(BLUR_PASSES):
        buf.filter(BLUR, 1)

    buf.endDraw()


# ============================================================
# SHOOTING STARS
# ============================================================

def draw_shooters():

    if (
        random(1) < 0.004 and
        len(shooters) < 2
    ):
        shooters.append(
            Shooter()
        )

    for s in shooters[:]:

        if not s.update():
            shooters.remove(s)
            continue

        for k in range(8):
            f = k / 8.0

            stroke(
                255, 255, 255,
                230 * (1 - f) * s.life
            )

            strokeWeight(
                2 * (1 - f) + 0.5
            )

            line(
                s.x - s.vx * f * 0.9,
                s.y - s.vy * f * 0.9,
                s.x - s.vx * (f + 0.125) * 0.9,
                s.y - s.vy * (f + 0.125) * 0.9
            )

    noStroke()


# ============================================================
# SCENERY
# ============================================================

def draw_scenery():

    image(
        far_l,
        -30 + par * 3,
        LY0
    )

    image(
        fog1,
        -150 +
        math.sin(t * 0.3) * 45 +
        par * 5,
        HORIZON - 65
    )

    image(
        mid_l,
        -30 + par * 6,
        LY0
    )

    image(
        fog2,
        -150 +
        math.cos(t * 0.25) * 48 +
        par * 8,
        HORIZON - 42
    )

    image(
        near_l,
        -30 + par * 10,
        LY0
    )

    image(
        water_img,
        0, HORIZON
    )


# ============================================================
# WATER REFLECTION
# ============================================================

def render_reflection_cache():

    refl.beginDraw()
    refl.background(0)
    refl.noStroke()

    y = HORIZON + 1
    ry = 0

    while y < WATER_BOTTOM:

        k = (
            y - HORIZON
        ) / float(
            WATER_BOTTOM - HORIZON
        )

        # Reflect higher sky colours
        # as distance from horizon grows
        src_y = (
            HORIZON -
            (y - HORIZON) * 3.2
        )

        # Two overlapping wave patterns
        # produce less repetitive motion
        dx = (
            math.sin(
                y * 0.18 +
                t * 1.6
            ) * (1.5 + 2.5 * k)
        )

        dx += (
            math.sin(
                y * 0.43 -
                t * 1.11
            ) * (0.5 + 1.6 * k)
        )

        dx += (
            math.sin(
                y * 0.067 +
                t * 0.46
            ) * 1.5
        )

        # Subtle moving vertical wobble
        vertical_wobble = (
            math.sin(
                y * 0.10 -
                t * 0.8
            ) * 1.8
        )

        # Interactive mouse ripples
        for wr in wripples:
            dyw = y - wr.y

            if abs(dyw) < 65:
                dx += (
                    wr.life * 7 *
                    math.sin(
                        dyw * 0.35 -
                        wr.r * 0.3
                    ) *
                    math.exp(
                        -abs(dyw) * 0.04
                    )
                )

        v2 = int(
            constrain(
                (
                    src_y +
                    vertical_wobble
                ) / S,
                3, BH
            )
        )

        # A gentle varying brightness
        light = (
            0.90 +
            0.10 * math.sin(
                y * 0.23 -
                t * 1.0
            )
        )

        alpha = (
            150 *
            (1 - 0.7 * k) *
            light
        )

        refl.image(
            buf,
            dx, ry,
            W, 4,
            0, v2 - 2,
            BW, v2
        )

        # Fade with a black overlay (same look as tint, far cheaper)
        refl.fill(
            0, 0, 0,
            255 - constrain(alpha, 0, 255)
        )

        refl.rect(0, ry, W, 4)

        ry += 4
        y += 4

    refl.endDraw()


def draw_reflection():

    # Reuse the reflection between updates
    if (
        frameCount <= 1 or
        frameCount % REFLECTION_INTERVAL == 0
    ):
        render_reflection_cache()

    blendMode(ADD)

    image(
        refl,
        0,
        HORIZON + 1
    )

    blendMode(BLEND)


# ============================================================
# MOONLIGHT REFLECTION
# ============================================================

def draw_glitter():
    if not MOON_ENABLED:
        return

    blendMode(ADD)
    noStroke()

    y = HORIZON + 3

    while y < WATER_BOTTOM:

        k = (
            y - HORIZON
        ) / float(
            WATER_BOTTOM - HORIZON
        )

        n = noise(
            y * 0.15,
            t * 0.8
        )

        w = (
            5 + 28 * k
        ) * (0.25 + n)

        cx = (
            MOON_X +
            math.sin(
                y * 0.35 +
                t * 1.2
            ) * (2 + 5 * k)
        )

        fill(
            210, 230, 255,
            120 *
            (1 - 0.55 * k) *
            n * 1.6
        )

        rect(
            cx - w / 2.0,
            y,
            w,
            1.6
        )

        y += 4

    blendMode(BLEND)


# ============================================================
# MOUSE-CONTROLLED WATER RIPPLES
# ============================================================

def draw_wripples():
    noFill()

    for wr in wripples[:]:
        wr.r += 1.8 * step
        wr.life *= 0.975 ** step

        if wr.life < 0.05:
            wripples.remove(wr)
            continue

        stroke(
            235, 170, 255,
            105 * wr.life
        )

        strokeWeight(1.0)

        ellipse(
            wr.x, wr.y,
            wr.r * 2,
            wr.r * 0.5
        )

        if wr.r > 14:
            stroke(
                200, 150, 230,
                60 * wr.life
            )

            ellipse(
                wr.x, wr.y,
                wr.r * 1.2,
                wr.r * 0.3
            )

    noStroke()


# ============================================================
# ATMOSPHERIC MIST
# ============================================================

def draw_mist():

    image(
        mist_a,
        -150 +
        math.sin(t * 0.17) * 60,
        HORIZON - 25
    )

    image(
        mist_b,
        -150 +
        math.cos(t * 0.11) * 70,
        HORIZON - 7
    )


# ============================================================
# SNOWFALL
# ============================================================

def draw_snow():
    noStroke()

    wind = (
        0.25 +
        (
            noise(t * 0.3) - 0.5
        ) * 0.8
    )

    for f in flakes:

        f[1] += (
            0.45 + f[2] * 0.6
        ) * step

        f[0] += (
            math.sin(
                t * 0.9 +
                f[3]
            ) * 0.4 +
            wind * (
                0.4 + f[2] * 0.4
            )
        ) * step

        if f[1] > H:
            f[1] = -4
            f[0] = random(W)

        if f[0] > W + 4:
            f[0] = -4

        elif f[0] < -4:
            f[0] = W + 4

        fill(
            255, 255, 255,
            70 + f[2] * 60
        )

        rect(
            f[0],
            f[1],
            f[2],
            f[2]
        )


# ============================================================
# MAIN ANIMATION LOOP
# ============================================================

def draw():
    global t, step
    global burst, brad
    global par, vpx
    global last_time_ms

    # --------------------------------------------
    # FRAME TIMING
    # --------------------------------------------
    # Limit time jumps so that a slow frame
    # doesn't make the aurora suddenly leap.

    now = millis()

    if last_time_ms is None:
        step = 1.0

    else:
        raw_step = constrain(
            (
                now - last_time_ms
            ) / (1000.0 / 60.0),
            0.3,
            3.0
        )

        # Ease toward the new value instead of jumping to it
        step += (raw_step - step) * 0.2

    last_time_ms = now

    t += TSPEED * step

    lap_reset()

    # --------------------------------------------
    # UPDATE INTERACTION
    # --------------------------------------------

    burst *= 0.994 ** step
    brad += 10.0 * step      # click wave travels a bit slower

    update_mouse()
    lap('mouse')

    # --------------------------------------------
    # UPDATE AURORA BREATHING AND SURGES
    # --------------------------------------------

    update_aurora_energy()

    # --------------------------------------------
    # CAMERA PARALLAX (uses smoothed mouse)
    # --------------------------------------------

    if hover > 0.1:
        target_par = (
            mx / float(W) - 0.5
        ) * 2.0

    else:
        target_par = 0.0

    par += (
        target_par - par
    ) * min(1.0, 0.03 * step)

    vpx += (
        (
            W * 0.5 +
            par * W * 0.18 +
            math.sin(
                t * 0.12
            ) * 75
        ) - vpx
    ) * min(1.0, 0.03 * step)

    # --------------------------------------------
    # SKY
    # --------------------------------------------

    image(sky, 0, 0)

    draw_stars(t * 0.0009)
    draw_clouds()
    lap('sky+stars+clouds')

    # --------------------------------------------
    # FLOWING AURORA
    # --------------------------------------------

    update_flow_grid()
    lap('flow grid')
    draw_aurora_buffer()
    lap('aurora buffer')

    blendMode(ADD)

    image(
        buf,
        0, 0,
        W, H
    )

    blendMode(BLEND)
    lap('aurora blit')

    # --------------------------------------------
    # SHOOTING STARS AND SCENERY
    # --------------------------------------------

    draw_shooters()
    draw_scenery()
    lap('scenery')

    # --------------------------------------------
    # WATER
    # --------------------------------------------

    draw_reflection()
    lap('reflection')
    draw_glitter()
    draw_wripples()
    lap('glitter+ripples')

    # --------------------------------------------
    # MIST, FOREGROUND AND SNOW
    # --------------------------------------------

    draw_mist()

    image(
        snowg,
        -30 + par * 15,
        SNOW_Y0
    )

    draw_snow()
    lap('mist+snow')

    # --------------------------------------------
    # INTRODUCTION TEXT
    # --------------------------------------------

    if (
        frameCount < 350 and
        hover < 0.5
    ):
        fill(
            255, 255, 255,
            130 *
            (1 - hover) *
            (1 - frameCount / 350.0)
        )

        textAlign(CENTER)
        textSize(12)

        text(
            "southern lights - move over the sky, click for a burst, move over the water",
            W / 2,
            32
        )

    # --------------------------------------------
    # FPS COUNTER
    # --------------------------------------------

    fill(255, 255, 255, 150)
    textAlign(LEFT)
    textSize(12)

    text(
        str(int(frameRate)) + " fps",
        10, 20
    )

    if SHOW_PROFILE:
        yy = 36

        for k, v in sorted(
            prof.items(),
            key=lambda kv: -kv[1]
        ):
            text(
                k + ": " + str(round(v, 1)) + " ms",
                10, yy
            )

            yy += 14
