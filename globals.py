#COLOR = (RRR, GGG, BBB)
from pygame import Color
from pygame.locals import *  # for event timers


BLACK = Color(0, 0, 0)
DGREY = Color(64, 64, 64)
WHITE = Color(255, 255, 255)

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

#monster types and globals
WEAK = 'WEAK'
MEDIUM = 'MEDIUM'
ULTIMATE = 'ULTIMATE'
CHASING = 'CHASING'
IDLE = 'IDLE'

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

#EVENTS:
TIME_TICK_EVENT = USEREVENT + 1
PLAYER1_LOCK_EVENT = USEREVENT + 2
PLAYER2_LOCK_EVENT = USEREVENT + 3
PLAYER1_MEDITATE_EVENT = USEREVENT + 4
PLAYER2_MEDITATE_EVENT = USEREVENT + 5
REGENERATION_EVENT = USEREVENT + 6


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


def font_position_center(center_within_size, font, text):
    x = (center_within_size[0] - font.size(text)[0]) // 2
    y = (center_within_size[1] - font.size(text)[1]) // 2
    return x, y

#Global to handle players from reaching out of 
#arena.     
def out_of_arena_fix(r):
    fixed = False   #Can be used for out-of-bounds checking since it returns true
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