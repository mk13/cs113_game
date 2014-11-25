import pygame
from pygame import Color
from pygame.locals import *  # for event timers

# Colors
BLACK = Color(0, 0, 0)
DGREY = Color(64, 64, 64)
WHITE = Color(255, 255, 255)
BROWN = Color(139, 69, 19)
RED = Color(255, 0, 0)
DKRED = Color(128, 0, 0)
DKGREEN = Color(0, 128, 0)
GREEN = Color(0, 255, 0)
BLUE = Color(0, 0, 255)
LBLUE = Color(0, 128, 255)
SKYBLUE = Color(128, 223, 223)
YELLOW = Color(255, 255, 0)
PURPLE = Color(255, 0, 255)
ORANGE = Color(255, 153, 0)

# Music Flags
MUSIC_ON = False
EFFECTS_ON = False

# Monster Types and Globals
ALL = 'ALL'
WEAK = 'WEAK'
MEDIUM = 'MEDIUM'
ULTIMATE = 'ULTIMATE'
CHASING = 'CHASING'
IDLE = 'IDLE'

# Inputs
LEFT = 'LEFT'
RIGHT = 'RIGHT'
UP = 'UP'
DOWN = 'DOWN'
JUMP = 'JUMP'
ATTACK = 'ATTACK'
DEBUG = 'DEBUG'
EXIT = 'EXIT'
RESET = 'RESET'
MELEE = 'MELEE'
RANGE = 'RANGED'

# Conditions
STUN = 'STUN'
SLOW = 'SLOW'
SNARE = 'SNARE'
DOT = 'DOT'
SILENCE = 'SILENCE'
WOUNDED = 'WOUNDED'
WEAKENED = 'WEAKENED'
SPEED = 'SPEED'
SHIELD = 'SHIELD'
INVIGORATED = 'INVIGORATED'
EMPOWERED = 'EMPOWERED'

# Events
TIME_TICK_EVENT = USEREVENT + 0
PLAYER1_LOCK_EVENT = USEREVENT + 1
PLAYER2_LOCK_EVENT = USEREVENT + 2
PLAYER1_MEDITATE_EVENT = USEREVENT + 3
PLAYER2_MEDITATE_EVENT = USEREVENT + 4
REGENERATION_EVENT = USEREVENT + 5
MORE_RAIN_EVENT = USEREVENT + 6
MONSTER_SPAWN_EVENT = USEREVENT + 7
SONG_END_EVENT = USEREVENT + 8

# Global Functions
def all_in(items_want_inside, container_being_checked):
    for thing in items_want_inside:
        if thing not in container_being_checked:
            return False
    return True

def all_isinstance(items_checking, instance_wanted):
    for thing in items_checking:
        if isinstance(thing, instance_wanted) is False:
            return False
    return True

def font_position_center(rect, font, text):
    x = (rect.width - font.size(text)[0]) // 2
    y = (rect.height - font.size(text)[1]) // 2
    return rect.left + x, rect.top + y

def out_of_arena_fix(r):
    """Global to handle players from reaching out of arena."""
    fixed = False  # Can be used for out-of-bounds checking since it returns true
    if r.left < 65:
        r.left = 65
        fixed = True
    if r.bottom > 475:
        r.bottom = 475
        fixed = True
    if r.right > 1215:
        r.right = 1215
        fixed = True
    return fixed

def handle_damage(target, value, time):
    target.hit_points -= value
    target.shield_trigger()
    target.st_buffer.append((value, time + 2000))

def turn_off_music():
    global MUSIC_ON
    MUSIC_ON = False
    pygame.mixer.music.stop()

def turn_on_music():
    global MUSIC_ON
    if MUSIC_ON == True:
        pass
    else:
        MUSIC_ON = True
        pygame.mixer.pre_init(44100)
        pygame.mixer.init()
        pygame.mixer.music.load('data/404error.mp3')
        pygame.mixer.music.play(-1)

def turn_off_effects():
    global SOUND_ON
    SOUND_ON = False

def turn_on_effects():
    global SOUND_ON
    SOUND_ON = True

def get_music_on():
    global MUSIC_ON
    return MUSIC_ON