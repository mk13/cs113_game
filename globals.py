import datetime
import os
import random
import sys
from collections import namedtuple
from collections import defaultdict

import pygame
from pygame import Color
from pygame.locals import *  # for event timers

if os.environ['COMPUTERNAME'] == 'BRIAN-DESKTOP':
    os.environ['SDL_VIDEO_WINDOW_POS'] = '{},{}'.format(1920, 90)
if os.environ['COMPUTERNAME'] in ('MAX-LT', 'BRIAN-LAPTOP'):
    os.environ['SDL_VIDEO_WINDOW_POS'] = '{},{}'.format(50, 30)

pygame.init()
pygame.display.set_caption('Famished Tournament')
SCREEN = pygame.display.set_mode((1280, 600))
CLOCK = pygame.time.Clock()
FPS = 30
NEXT_PAGE = 'start'

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
LLBLUE = Color(0, 0, 128)
LBLUE = Color(0, 128, 255)
SKYBLUE = Color(128, 223, 223)
YELLOW = Color(255, 255, 0)
DKYELLOW = Color(153, 153, 0)
DKDKYELLOW = Color(128, 128, 0)
PURPLE = Color(255, 0, 255)
DKPURPLE = Color(153, 0, 153)
ORANGE = Color(255, 153, 0)
DKORANGE = Color(153, 92, 0)

# Music
SONGS = ['data/pneumatic_driller.mp3', 'data/euglena_zielona.mp3',
         'data/drilldance.mp3', 'data/running_emu.mp3', 'data/wooboodoo.mp3',
         'data/accident.mp3']

# Monster Types and Globals
ALL = 'ALL'
WEAK = 'WEAK'
MEDIUM = 'MEDIUM'
ULTIMATE = 'ULTIMATE'
CHASING = 'CHASING'
IDLE = 'IDLE'
ULTIMATE_SPAWN_RATE = 5000

# Player States (for animation)
STAND = 'STAND'
LWALK = 'LWALK'
RWALK = 'RWALK'
JUMP = 'JUMP'
FALL = 'FALL'
DEATH = 'DEATH'
ATTACK = 'ATTACK'
CAST = 'CAST'

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
FIELD = 'FIELD'

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
BUFFS = [SPEED, SHIELD, INVIGORATED, EMPOWERED]
DEBUFFS = [STUN, SLOW, SNARE, DOT, SILENCE, WOUNDED, WEAKENED]

# Buttons
ATTACKBUTTON = "attack_id"
SKILL1BUTTON = "skill1_id"
SKILL2BUTTON = "skill2_id"
SKILL3BUTTON = "skill3_id"
ULTBUTTON    = "ult_id"

# Events
TIME_TICK_EVENT = USEREVENT + 0
PLAYER1_LOCK_EVENT = USEREVENT + 1
PLAYER2_LOCK_EVENT = USEREVENT + 2
PLAYER1_PICKUP_EVENT = USEREVENT + 3
PLAYER2_PICKUP_EVENT = USEREVENT + 4
REGENERATION_EVENT = USEREVENT + 5
MONSTER_SPAWN_EVENT = USEREVENT + 6
SONG_END_EVENT = USEREVENT + 7
MORE_RAIN_EVENT = USEREVENT + 8

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

def out_of_arena_fix(player):
    """Global to handle players from reaching out of arena."""
    global arena_in_use  # set in GameLoop._setup_arena of main.py
    play_area = arena_in_use.play_area_rect
    fixed = False  # Can be used for out-of-bounds checking since it returns true
    if player.left < play_area.left:
        player.left = play_area.left
        fixed = True
    if player.bottom > play_area.bottom:
        player.bottom = play_area.bottom
        fixed = True
    if player.right > play_area.right:
        player.right = play_area.right
        fixed = True
    return fixed

def handle_damage(target, value, time):
    if value != 0:
        target.hit_points -= value
        target.shield_trigger(value)
        target.st_buffer.append((value, time + 2000))

def condition_string(cond, value):
    st = cond + ": "
    left = 0 + int(value/1000)
    right = 0 + int( (value%1000) / 100)
    st += str(left)
    st += "."
    st += str(right)
    return st

def force_add_particle_to_player(particle,player):
    if isinstance(particle,list):
        if player.new_particle is None:
            player.new_particle = particle
        elif isinstance(player.new_particle, list):
            player.new_particle += particle
        else:
            player.new_particle = [player.new_particle] + particle

    else:
        if player.new_particle is None:
            player.new_particle = particle
        elif isinstance(player.new_particle, list):
            player.new_particle.append(particle)
        else:
            player.new_particle = [player.new_particle, particle]

def EXIT_GAME():
    pygame.quit()
    sys.exit()

# Music and Sound
class Audio:
    def __init__(self):
        try:
            pygame.mixer.init(44100)
            self.audio_device_found = True
        except pygame.error:
            self.audio_device_found = False
        self.menu_song = self.curr_song = 'data/404error.mp3'
        self.music_on = self.sound_on = False

    def restart_music(self):
        if self.audio_device_found:
            self.turn_off_music()
            self.turn_on_music()

    def turn_on_music(self):
        if self.audio_device_found:
            self.music_on = True
            self.curr_song = self.menu_song
            pygame.mixer.music.load(self.curr_song)
            pygame.mixer.music.play(-1)
            print(self)

    def turn_off_music(self):
        if self.audio_device_found:
            self.music_on = False
            pygame.mixer.music.stop()

    def turn_on_effects(self):
        if self.audio_device_found:
            self.sound_on = True

    def turn_off_effects(self):
        if self.audio_device_found:
            self.sound_on = False

    def play_next_random_song(self):
        if self.audio_device_found:
            self.curr_song = random.choice([s for s in SONGS if s != self.curr_song])
            pygame.mixer.music.load(self.curr_song)
            pygame.mixer.music.play()
            pygame.mixer.music.set_endevent(SONG_END_EVENT)
            print(self)

    def __str__(self):
        t = datetime.datetime.now().strftime('%H:%M:%S')
        return 'new song: "{}"    started at: {}'.format(self.curr_song.replace('data/', '').replace('.mp3', ''), t)
AUDIO = Audio()

class Input:

    def __init__(self, player_id=1):
        self.gp_input = defaultdict(bool)
        self.kb_input = defaultdict(bool)
        self.player_id = player_id
        try:
            self.gamepad = pygame.joystick.Joystick(player_id - 1)
            self.gamepad.init()
            self.gamepad_found = True
            print('"{}"'.format(self.gamepad.get_name()))
            self.__setup_gamepad_buttons__()
        except pygame.error:
            pass

    def __setup_gamepad_buttons__(self):
        input_nt = namedtuple('input_nt', 'kind, number, value1, value2')

        #  L2                                  R2
        #     L1                            R1
        #         U                      Y
        #       L   R   SELCT  START   X   B
        #         D                      A

        #         self.gp_input['skill2'] = self.gamepad.get_button(0)        Y
        #         self.gp_input['attack'] = self.gamepad.get_button(3)        X
        #         self.gp_input['skill1'] = self.gamepad.get_button(1)        B
        #         self.gp_input['jump'] = self.gamepad.get_button(2)          A
        #         self.gp_input['drop'] = self.gamepad.get_button(4)          L1
        #         self.gp_input['skill3'] = self.gamepad.get_button(5)        R1
        #         self.gp_input['ult'] = self.gamepad.get_button(7)           R2

        if self.gamepad.get_name() == "Gioteck PS3 Wired Controller":  # Max's gamepad
            di = {'GP_LEFT': input_nt(kind='hat', number=0, value1=0, value2=-1),  # guessing
                  'GP_RIGHT': input_nt(kind='hat', number=0, value1=0, value2=+1),  # guessing
                  'GP_UP': input_nt(kind='hat', number=0, value1=1, value2=+1),  # guessing
                  'GP_DOWN': input_nt(kind='hat', number=0, value1=1, value2=-1),  # guessing
                  'GP_Y': input_nt(kind='button', number=0, value1=None, value2=None),
                  'GP_X': input_nt(kind='button', number=3, value1=None, value2=None),
                  'GP_B': input_nt(kind='button', number=1, value1=None, value2=None),
                  'GP_A': input_nt(kind='button', number=2, value1=None, value2=None),
                  'GP_SELECT': input_nt(kind='button', number=8, value1=None, value2=None),  # guessing
                  'GP_START': input_nt(kind='button', number=9, value1=None, value2=None),  # guessing
                  'GP_L1': input_nt(kind='button', number=4, value1=None, value2=None),
                  'GP_R1': input_nt(kind='button', number=5, value1=None, value2=None),
                  'GP_L2': input_nt(kind='button', number=6, value1=None, value2=None),  # guessing
                  'GP_R2': input_nt(kind='button', number=7, value1=None, value2=None)}

        elif self.gamepad.get_name() == 'Logitech Cordless RumblePad 2 USB':  # Brian's gamepad if switched to "D"
            di = {'GP_LEFT': input_nt(kind='hat', number=0, value1=0, value2=-1),
                  'GP_RIGHT': input_nt(kind='hat', number=0, value1=0, value2=+1),
                  'GP_UP': input_nt(kind='hat', number=0, value1=1, value2=+1),
                  'GP_DOWN': input_nt(kind='hat', number=0, value1=1, value2=-1),
                  'GP_Y': input_nt(kind='button', number=3, value1=None, value2=None),
                  'GP_X': input_nt(kind='button', number=0, value1=None, value2=None),
                  'GP_B': input_nt(kind='button', number=2, value1=None, value2=None),
                  'GP_A': input_nt(kind='button', number=1, value1=None, value2=None),
                  'GP_SELECT': input_nt(kind='button', number=8, value1=None, value2=None),
                  'GP_START': input_nt(kind='button', number=9, value1=None, value2=None),
                  'GP_L1': input_nt(kind='button', number=4, value1=None, value2=None),
                  'GP_R1': input_nt(kind='button', number=5, value1=None, value2=None),
                  'GP_L2': input_nt(kind='button', number=6, value1=None, value2=None),
                  'GP_R2': input_nt(kind='button', number=7, value1=None, value2=None)}

        elif self.gamepad.get_name() == 'Wireless Gamepad F710 (Controller)':  # Brian's gamepad if switched to "X"
            di = {'GP_LEFT': input_nt(kind='hat', number=0, value1=0, value2=-1),
                  'GP_RIGHT': input_nt(kind='hat', number=0, value1=0, value2=+1),
                  'GP_UP': input_nt(kind='hat', number=0, value1=1, value2=+1),
                  'GP_DOWN': input_nt(kind='hat', number=0, value1=1, value2=-1),
                  'GP_Y': input_nt(kind='button', number=3, value1=None, value2=None),
                  'GP_X': input_nt(kind='button', number=2, value1=None, value2=None),
                  'GP_B': input_nt(kind='button', number=1, value1=None, value2=None),
                  'GP_A': input_nt(kind='button', number=0, value1=None, value2=None),
                  'GP_SELECT': input_nt(kind='button', number=6, value1=None, value2=None),
                  'GP_START': input_nt(kind='button', number=7, value1=None, value2=None),
                  'GP_L1': input_nt(kind='button', number=4, value1=None, value2=None),
                  'GP_R1': input_nt(kind='button', number=5, value1=None, value2=None),
                  'GP_L2': input_nt(kind='axis', number=2, value1=+1, value2=None),
                  'GP_R2': input_nt(kind='axis', number=2, value1=-1, value2=None)}

        self.GP_INPUTS_at_setup = di

    def refresh(self):
        if self.player_id == 1:
            self._get_keyboard_pressed()
            self._get_keyboard_events()
        self._get_gamepad_pressed()
        self._get_gamepad_events()
        self._combine_all_pressed()
        if self.player_id == 1:
            self._handle_mouse_visibility()

    def refresh_during_pause(self):
        if self.player_id == 1:
            for event in pygame.event.get(KEYDOWN):
                if event.key == K_RETURN:
                    self.START = not self.START
        if self.gamepad_found:
            for event in pygame.event.get(JOYBUTTONDOWN):
                if event.button == self.GP_INPUTS_at_setup['GP_START'].number:
                    self.START = not self.START

    def _get_keyboard_pressed(self):
        # self.kb_input = pygame.key.get_pressed()
        sucky_kb_input = pygame.key.get_pressed()
        self.kb_input['K_RETURN'] = sucky_kb_input[K_RETURN]
        self.kb_input['K_ESCAPE'] = sucky_kb_input[K_ESCAPE]
        self.kb_input['K_BACKQUOTE'] = sucky_kb_input[K_BACKQUOTE]
        self.kb_input['K_F12'] = sucky_kb_input[K_F12]
        self.kb_input['K_LEFT'] = sucky_kb_input[K_LEFT]
        self.kb_input['K_RIGHT'] = sucky_kb_input[K_RIGHT]
        self.kb_input['K_UP'] = sucky_kb_input[K_UP]
        self.kb_input['K_DOWN'] = sucky_kb_input[K_DOWN]
        self.kb_input['K_SPACE'] = sucky_kb_input[K_SPACE]
        self.kb_input['K_a'] = sucky_kb_input[K_a]
        self.kb_input['K_s'] = sucky_kb_input[K_s]
        self.kb_input['K_d'] = sucky_kb_input[K_d]
        self.kb_input['K_f'] = sucky_kb_input[K_f]
        self.kb_input['K_g'] = sucky_kb_input[K_g]
        self.kb_input['K_q'] = sucky_kb_input[K_q]
        self.kb_input['K_r'] = sucky_kb_input[K_r]
        self.kb_input['K_k'] = sucky_kb_input[K_k]

    def _get_keyboard_events(self):
        for event in pygame.event.get(KEYDOWN):
            if event.key == K_RETURN:
                self.START = not self.START
            if event.key == K_ESCAPE:
                self.SELECT = not self.SELECT
            if event.key in (K_BACKQUOTE, K_F12):
                self.DEBUG_VIEW = not self.DEBUG_VIEW

    def _get_gamepad_pressed(self):
        if self.gamepad_found:
            for name, info in self.GP_INPUTS_at_setup.items():
                if info.kind == 'button':
                    self.gp_input[name] = self.gamepad.get_button(info.number)
                elif info.kind == 'axis':
                    self.gp_input[name] = round(self.gamepad.get_axis(info.number)) == info.value1
                elif info.kind == 'hat':
                    self.gp_input[name] = self.gamepad.get_hat(info.number)[info.value1] == info.value2

    def _get_gamepad_events(self):
        if self.gamepad_found:
            for event in pygame.event.get(JOYBUTTONDOWN):
                if event.button == self.GP_INPUTS_at_setup['GP_START'].number:
                    self.START = not self.START
                if event.button == self.GP_INPUTS_at_setup['GP_SELECT'].number:
                    self.SELECT = not self.SELECT

    def _combine_all_pressed(self):
        self.LEFT = self.kb_input['K_LEFT'] or self.gp_input['GP_LEFT']
        self.RIGHT = self.kb_input['K_RIGHT'] or self.gp_input['GP_RIGHT']
        self.UP = self.kb_input['K_UP'] or self.gp_input['GP_UP']
        self.DOWN = self.kb_input['K_DOWN'] or self.gp_input['GP_DOWN']
        self.JUMP = self.kb_input['K_SPACE'] or self.gp_input['GP_A']
        self.ATTACK = self.kb_input['K_a'] or self.gp_input['GP_X']
        self.SKILL1 = self.kb_input['K_s'] or self.gp_input['GP_B']
        self.SKILL2 = self.kb_input['K_d'] or self.gp_input['GP_Y']
        self.SKILL3 = self.kb_input['K_f'] or self.gp_input['GP_R1']
        self.ULT = self.kb_input['K_g'] or self.gp_input['GP_R2']
        self.DROP_SKILL = self.kb_input['K_q'] or self.gp_input['GP_L1']
        self.RESPAWN = self.kb_input['K_r']
        self.KILLALL = self.kb_input['K_k']

    def _handle_mouse_visibility(self):
        global NEXT_PAGE
        if self.DEBUG_VIEW and NEXT_PAGE not in ('start, options, help'.split(', ')):
            pygame.mouse.set_visible(False)
        else:
            pygame.mouse.set_visible(True)

    def __getattr__(self, name):
        # initializes any missing variables to False
        exec('self.{} = False'.format(name))
        return eval('self.{}'.format(name))

INPUT1 = Input(player_id=1)
INPUT2 = Input(player_id=2)



# Arenas
arena_nt = namedtuple('arena_nt', 'left_wall_x, right_wall_x, floor_y, platforms, max_monsters, possible_monsters, background, p1_spawn, p2_spawn')
terrain_nt = namedtuple('terrain_nt', 'left, top, width, height, color, hits_to_destroy, spawn_point')

arena1 = arena_nt(
    left_wall_x=65, right_wall_x=1215, floor_y=475,
    platforms=[
        terrain_nt(0, 270, 300, 60, DKGREEN, -1, False),
        terrain_nt(850, 270, 300, 60, DKGREEN, -1, False),
        terrain_nt(545, 150, 60, 230, DKGREEN, -1, False),
        terrain_nt(140, 100, 150, 20, DKGREEN, -1, False),
        terrain_nt(860, 100, 150, 20, DKGREEN, -1, False),
        terrain_nt(30, 240, 40, 20, WHITE, 5, False),
        terrain_nt(1145, 465, -5, 5, None, -1, True),
        terrain_nt(15, 465, -5, 5, None, -1, True), ],
    max_monsters=3, possible_monsters=(WEAK, MEDIUM),
    background=None, p1_spawn=(135, 150), p2_spawn=(985, 150))

arena2 = arena_nt(
    left_wall_x=65, right_wall_x=1215, floor_y=475,
    platforms=[
        terrain_nt(50, 100, 50, 300, DKGREEN, -1, False),
        terrain_nt(240, 40, 50, 300, DKGREEN, -1, False),
        terrain_nt(500, 135, 100, 25, DKGREEN, -1, False),
        terrain_nt(725, 255, 175, 25, DKGREEN, -1, False),
        terrain_nt(1050, 375, 100, 25, DKGREEN, -1, False),
        terrain_nt(400, 434, 300, 41, DKGREEN, -1, False),
        terrain_nt(485, 394, 300, 41, DKGREEN, -1, False),
        terrain_nt(970, 65, 80, 10, DKGREEN, -1, False),
        terrain_nt(150, 465, -5, 5, None, -1, True),
        terrain_nt(930, 465, -5, 5, None, -1, True), ],
    max_monsters=3, possible_monsters=(WEAK, MEDIUM),  # ALL
    background=None, p1_spawn=(135, 150), p2_spawn=(985, 150))

arena3 = arena_nt(
    left_wall_x=65, right_wall_x=1215, floor_y=458,
    platforms=[
        terrain_nt(425, 80, 73, 40, None, -1, False),
        terrain_nt(555, 80, 100, 40, None, -1, False),
        terrain_nt(85, 140, 228, 40, None, -1, False),
        terrain_nt(85, 180, 40, 142, None, -1, False),
        terrain_nt(85, 322, 95, 40, None, -1, False),
        terrain_nt(332, 241, 220, 40, None, -1, False),
        terrain_nt(595, 319, 417, 40, None, -1, False),
        terrain_nt(972, 156, 40, 163, None, -1, False),
        terrain_nt(785, 120, 227, 40, None, -1, False),
        terrain_nt(150, 465, -5, 5, None, -1, True),
        terrain_nt(930, 465, -5, 5, None, -1, True), ],
    max_monsters=3, possible_monsters=(WEAK, MEDIUM),  # ALL
    background='data/vines-copy2.png', p1_spawn=(75, 50), p2_spawn=(992, 50))

# Monsters
monster_info_nt = namedtuple('monster_info_nt', 'kind, w, h, dx, dy, hp, chase, idle, exp_value, dmg')
MONSTER_TABLE = {
    WEAK: monster_info_nt(WEAK, 30, 40, 2, 10, 100, 5000, 5000, 10, 10),
    MEDIUM: monster_info_nt(MEDIUM, 50, 60, 3, 12, 250, 7000, 5000, 15, 15),
    ULTIMATE: monster_info_nt(ULTIMATE, 80, 80, 4, 13, 500, 10000, 5000, 25, 30)}





