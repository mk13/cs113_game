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
NEXT_PAGE = ''

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

# Gamepad Buttons
GP_LEFT = 'GP_LEFT'
GP_RIGHT = 'GP_RIGHT'
GP_UP = 'GP_UP'
GP_DOWN = 'GP_DOWN'

GP_Y = 'GP_Y'
GP_X = 'GP_X'
GP_B = 'GP_B'
GP_A = 'GP_A'

GP_BACK = 'GP_BACK'
GP_START = 'GP_START'

GP_L1 = 'GP_L1'
GP_R1 = 'GP_R1'
GP_L2 = 'GP_L2'
GP_R2 = 'GP_R2'


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
        try:
            self.gamepad = pygame.joystick.Joystick(player_id - 1)
            self.gamepad.init()
            self.gamepad_found = True
            print('"{}"'.format(self.gamepad.get_name()))
        except pygame.error:
            pass
        self.gp_input = defaultdict(bool)
        self.kb_input = defaultdict(bool)
        self.player_id = player_id

    def refresh(self):
        if self.player_id == 1:
            self._get_keyboard_keys_pressed()
            self._handle_keyboard_updown_events()
        self._get_gamepad_axis_buttons_pressed()
        self._handle_gamepad_updown_events()
        self._update_attributes()
        if self.player_id == 1:
            self._handle_mouse_visibility()
            self._handle_exit_input()

    def _get_gamepad_axis_buttons_pressed(self):
        if self.gamepad_found:

            if self.gamepad.get_name() == "Gioteck PS3 Wired Controller":
                # Max's gamepad
                self.gp_input[GP_LEFT] = round(self.gamepad.get_axis(0)) == -1
                self.gp_input[GP_RIGHT] = round(self.gamepad.get_axis(0)) == +1
                self.gp_input[GP_UP] = round(self.gamepad.get_axis(1)) == -1
                self.gp_input[GP_DOWN] = round(self.gamepad.get_axis(1)) == +1

                # self.gp_input[GP_LEFT] = self.gamepad.get_hat(i)
                # self.gp_input[GP_RIGHT] = self.gamepad.get_hat(1)[0] == 1
                # self.gp_input[GP_UP] = self.gamepad.get_hat(1)[1] == 1
                # self.gp_input[GP_DOWN] = self.gamepad.get_hat(1)[1] == -1

                self.gp_input['attack'] = self.gamepad.get_button(3)
                self.gp_input['jump'] = self.gamepad.get_button(2)
                self.gp_input['skill1'] = self.gamepad.get_button(1)
                self.gp_input['skill2'] = self.gamepad.get_button(0)
                self.gp_input['skill3'] = self.gamepad.get_button(5)
                self.gp_input['ult'] = self.gamepad.get_button(7)
                self.gp_input['drop'] = self.gamepad.get_button(4)

            elif self.gamepad.get_name() == 'Logitech Cordless RumblePad 2 USB':  # if switched to "D"

                #  L2                                     R2
                #  L1                                     R1
                #        U                           Y
                #      L   R     back    start     X   B
                #        D                           A

                self.gp_input[GP_LEFT] = self.gamepad.get_hat(0)[0] == -1
                self.gp_input[GP_RIGHT] = self.gamepad.get_hat(0)[0] == +1
                self.gp_input[GP_UP] = self.gamepad.get_hat(0)[1] == +1
                self.gp_input[GP_DOWN] = self.gamepad.get_hat(0)[1] == -1

                self.gp_input[GP_Y] = self.gamepad.get_button(3)
                self.gp_input[GP_X] = self.gamepad.get_button(0)
                self.gp_input[GP_B] = self.gamepad.get_button(2)
                self.gp_input[GP_A] = self.gamepad.get_button(1)

                self.gp_input[GP_BACK] = self.gamepad.get_button(8)
                self.gp_input[GP_START] = self.gamepad.get_button(9)

                self.gp_input[GP_L1] = self.gamepad.get_button(4)
                self.gp_input[GP_R1] = self.gamepad.get_button(5)
                self.gp_input[GP_L2] = self.gamepad.get_button(6)
                self.gp_input[GP_R2] = self.gamepad.get_button(7)

            elif self.gamepad.get_name() == 'Wireless Gamepad F710 (Controller)':  # if switched to "X"

                #  L2                                     R2
                #  L1                                     R1
                #        U                           Y
                #      L   R     back    start     X   B
                #        D                           A

                self.gp_input[GP_LEFT] = self.gamepad.get_hat(0)[0] == -1
                self.gp_input[GP_RIGHT] = self.gamepad.get_hat(0)[0] == +1
                self.gp_input[GP_UP] = self.gamepad.get_hat(0)[1] == +1
                self.gp_input[GP_DOWN] = self.gamepad.get_hat(0)[1] == -1

                self.gp_input[GP_Y] = self.gamepad.get_button(3)
                self.gp_input[GP_X] = self.gamepad.get_button(2)
                self.gp_input[GP_B] = self.gamepad.get_button(1)
                self.gp_input[GP_A] = self.gamepad.get_button(0)

                self.gp_input[GP_BACK] = self.gamepad.get_button(6)
                self.gp_input[GP_START] = self.gamepad.get_button(7)

                self.gp_input[GP_L1] = self.gamepad.get_button(4)
                self.gp_input[GP_R1] = self.gamepad.get_button(5)
                self.gp_input[GP_L2] = round(self.gamepad.get_axis(2)) == +1
                self.gp_input[GP_R2] = round(self.gamepad.get_axis(2)) == -1

    def _get_keyboard_keys_pressed(self):
        self.kb_input = pygame.key.get_pressed()

    def _handle_keyboard_updown_events(self):
        for event in pygame.event.get(KEYDOWN):
            if event.key in (K_BACKQUOTE, K_F12):
                self.DEBUG_VIEW = not self.DEBUG_VIEW
            if event.key == K_PAUSE:
                self.PAUSED = not self.PAUSED
            if event.key == K_RETURN:
                self.ENTER_LEAVE = not self.ENTER_LEAVE

    def _handle_gamepad_updown_events(self):
        if self.gamepad_found:
            # Push A and Y at same time in order for the ENTER_LEAVE input to register from gamepad
            # ENTER_LEAVE input enters game/menu from menu/game
            joy_button_down_events = pygame.event.get(JOYBUTTONDOWN)
            if len(list(filter(lambda e: e.button in [self.G_A_BUTTON, self.G_Y_BUTTON], joy_button_down_events))) == 2:
                self.ENTER_LEAVE = not self.ENTER_LEAVE
            for event in joy_button_down_events:
                if event.button == GP_START:
                    self.PAUSED = not self.PAUSED
                if event.button == GP_BACK:
                    self.DEBUG_VIEW = not self.DEBUG_VIEW

    def _update_attributes(self):
        self.LEFT = self.kb_input[K_LEFT] or self.gp_input[GP_LEFT]
        self.RIGHT = self.kb_input[K_RIGHT] or self.gp_input[GP_RIGHT]
        self.UP = self.kb_input[K_UP] or self.gp_input[GP_UP]
        self.DOWN = self.kb_input[K_DOWN] or self.gp_input[GP_DOWN]

        self.JUMP = self.kb_input[K_SPACE] or self.gp_input[GP_A] or self.gp_input['jump']
        self.ATTACK = self.kb_input[K_a] or self.gp_input[GP_X] or self.gp_input['attack']
        self.SKILL1 = self.kb_input[K_s] or self.gp_input[GP_B] or self.gp_input['skill1']
        self.SKILL2 = self.kb_input[K_d] or self.gp_input[GP_Y] or self.gp_input['skill2']

        self.SKILL3 = self.kb_input[K_f] or self.gp_input[GP_R1] or self.gp_input['skill3']
        self.ULT = self.kb_input[K_g] or self.gp_input[GP_R2] or self.gp_input['ult']

        self.DROP_SKILL = self.kb_input[K_q] or self.gp_input[GP_L1] or self.gp_input['drop']

        self.EXIT = self.kb_input[K_ESCAPE] or (self.gp_input[GP_START] and self.gp_input[GP_BACK])
        self.RESPAWN = self.kb_input[K_r]
        self.ENTER = self.kb_input[K_RETURN]
        self.KILLALL = self.kb_input[K_k]

    def _handle_mouse_visibility(self):
        if self.DEBUG_VIEW and NEXT_PAGE not in ('start, options, help'.split(', ')):
            pygame.mouse.set_visible(False)
        else:
            pygame.mouse.set_visible(True)

    def _handle_exit_input(self):
        # Add the QUIT event to the pygame event queue to be handled
        # later, at the same time the QUIT event from clicking the
        # window X is handled
        if self.EXIT:
            pygame.event.post(pygame.event.Event(QUIT))

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





