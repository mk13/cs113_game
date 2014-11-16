import math

import pygame
from pygame.locals import *

from globals import *

# -------------------------------------------------------------------------


class Rect2(pygame.Rect):
    def __init__(self, *args, **kargs):
        if args != tuple():
            if all_isinstance(args, tuple) and len(args) is 2:
                super().__init__(args[0], args[1])

            if all_isinstance(args, tuple) and len(args) is 1:
                super().__init__(args[0][0], args[0][1], args[0][2], args[0][3])

            elif all_isinstance(args, int):
                super().__init__(args[0], args[1], args[2], args[3])
        else:
            if all_in('top,left,width,height'.split(','), kargs.keys()):
                super().__init__(kargs['left'], kargs['top'], kargs['width'], kargs['height'])

            elif all_in(('topleft', 'size'), kargs):
                super().__init__(kargs['topleft'], kargs['size'])
# -------------------------------------------------------------------------


class Player(Rect2):
    def __init__(self, left, top, width, height):

        # position
        super().__init__(left, top, width, height)
        self.topleft_initial = self.topleft

        # speed
        self.dx, self.dy = 10, 4  # initial rates
        self.dx_max, self.dy_max = 15, 15  # max speed, max fall rate

        # acceleration - player input
        self.dx_movement = 2  # +/- applied when player moves
        self.dy_jump = 35  # applied when player jumps
        self.dx_wall_jump = 15  # +/- applied when player wall jumps

        # acceleration - physics
        self.dx_friction = 0.5  # applied every frame
        self.dy_gravity = 4  # applied every frame

        # misc.
        self.touching_ground = False  # for jumping
        self.hit_wall_from = None  # for wall jumping

        # character stats
        self.hit_points = self.hit_points_max = 100
        self.energy = self.energy_max = 10

        # attacking
        self.facing_direction = RIGHT
        self.attack_cooldown_expired = True
        self.new_particle = None

    def copy(self):
        return Player(self.left, self.top, self.width, self.height)

    def move_ip(self, dxdy):
        super().move_ip(dxdy)

    def __call__(self, input, arena_map):
        self._handle_facing_direction(input)
        self._handle_acceleration(input)
        self._handle_movement(arena_map)
        self._handle_attack(input)

    def _handle_facing_direction(self, input):
        self.facing_direction = RIGHT if input.RIGHT \
            else LEFT if input.LEFT \
            else self.facing_direction

    def _handle_acceleration(self, input):

        def _apply_accel_left_right_input(input):
            self.dx += self.dx_movement if input.RIGHT \
                else -self.dx_movement if input.LEFT \
                else 0

        def _apply_friction():
            self.dx += self.dx_friction if self.dx < 0 \
                else -self.dx_friction if self.dx > 0 \
                else 0

        def _apply_accel_jump_input(input):
            if input.JUMP:
                self.dy -= self.dy_jump if self.touching_ground or self.hit_wall_from \
                    else 0
                self.dx += self.dx_wall_jump if self.hit_wall_from == LEFT \
                    else -self.dx_wall_jump if self.hit_wall_from == RIGHT \
                    else 0

        def _apply_gravity():
            self.dy += self.dy_gravity

        def _apply_limits():
            self.dx = eval('{:+}'.format(self.dx)[0] + str(min(abs(self.dx), self.dx_max)))
            self.dy = min(self.dy, self.dy_max)

        _apply_accel_left_right_input(input)
        _apply_friction()
        _apply_accel_jump_input(input)
        _apply_gravity()
        _apply_limits()

    def _handle_movement(self, arena):
        self.hit_wall_from = None  # reset every frame
        self.touching_ground = False  # reset every frame
        self.move_ip((self.dx, self.dy))  # move then check for collisions
        for terrain in arena.rects:

            # (player's bottom in between terrain top and bottom) or (player's top in between terrain top and bottom)
            if (terrain.top < self.bottom < terrain.bottom) or (terrain.bottom > self.top > terrain.top):

                # (player's left "to the left of" terrain's right) and (player's right "to the right of" terrain's right)
                if (self.left < terrain.right) and (self.right > terrain.right):
                    # move player so it's left is flush with terrain's right
                    self.left = terrain.right
                    self.hit_wall_from = LEFT
                    self.dx = self.dy = 0

                # (player's left "to the left of" terrain's left) and (player's right "to the right of" terrain's left)
                elif (self.left < terrain.left) and (self.right > terrain.left):
                    # move player so it's right is flush with terrain's left
                    self.right = terrain.left
                    self.hit_wall_from = RIGHT
                    self.dx = self.dy = 0

            # (player's left in between terrain right and left) or (player's right in between terrain left and right)
            if (terrain.right > self.left > terrain.left) or (terrain.left < self.right < terrain.right):

                # (if player's bottom lower than terrain bottom) and (player's top above terrain's bottom)
                if (self.bottom > terrain.bottom) and (self.top < terrain.bottom):
                    # move player so it's top is flush with terrain's bottom
                    self.top = terrain.bottom

                # (if player's bottom lower than terrain top) and (player's top above terrain's top)
                elif (self.bottom > terrain.top) and (self.top < terrain.top):
                    # move player so it's bottom is flush with terrain's top
                    self.bottom = terrain.top
                    self.dy, self.touching_ground = 0, True

    def _handle_attack(self, input):
        self.new_particle = None
        if input.ATTACK:
            if self.attack_cooldown_expired:
                self.attack_cooldown_expired = False
                self.new_particle = MeleeParticle(attack_particle)
# -------------------------------------------------------------------------


class Input:
    def __init__(self):
        try:
            self.gamepad = pygame.joystick.Joystick(0)
            self.gamepad.init()
            self.gamepad_found = True
        except pygame.error:
            self.gamepad_found = False

    def refresh(self):
        self._get_gamepad_input()
        self._get_keyboard_input()
        self._update_attributes()

    def _get_gamepad_input(self):
        if self.gamepad_found:
            self.left_right_axis = round(self.gamepad.get_axis(0))
            self.up_down_axis = round(self.gamepad.get_axis(1))
            #     Y
            #   X   B
            #     A
            self.y_button = self.gamepad.get_button(3)
            self.x_button = self.gamepad.get_button(0)
            self.b_button = self.gamepad.get_button(2)
            self.a_button = self.gamepad.get_button(1)
            self.start_button = self.gamepad.get_button(9)
            self.back_button = self.gamepad.get_button(8)

    def _get_keyboard_input(self):
        self.kb_input = pygame.key.get_pressed()

    def _update_attributes(self):
        self.LEFT = self.kb_input[K_LEFT] or self.left_right_axis == -1
        self.RIGHT = self.kb_input[K_RIGHT] or self.left_right_axis == +1
        self.UP = self.kb_input[K_UP] or self.up_down_axis == -1
        self.DOWN = self.kb_input[K_DOWN] or self.up_down_axis == +1
        self.JUMP = self.kb_input[K_SPACE] or self.a_button
        self.ATTACK = self.kb_input[K_a] or self.x_button
        self.RESET = self.kb_input[K_r] or self.y_button
        self.DEBUG = self.kb_input[K_F12] or (self.start_button and self.back_button)
        self.EXIT = self.kb_input[K_q] or self.kb_input[K_ESCAPE] or self.back_button

    def __getattr__(self, name):
        return None
# -------------------------------------------------------------------------


class Arena:
    def __init__(self, *color_rects):
        rects = [Rect2(rect) for rect, color in color_rects]
        colors = [color for rect, color in color_rects]
        self.play_area_rect = rects[0]
        self.play_area_color = colors[0]
        self.rects = rects[1:]
        self.colors = colors[1:]

    def __iter__(self):
        # currently only time iteration is used is when the rects are drawn
        for rect, rect_color in zip([self.play_area_rect] + self.rects, [self.play_area_color] + self.colors):
            yield rect, rect_color

arena1 = Arena(
    ((65, 0, 1150, 475), SKYBLUE),  # play_area (must be first)
    ((0, 475, 1280, 50), None),  # floor
    ((15, 0, 50, 600), None),  # left wall
    ((1215, 0, 50, 600), None),  # right wall
    ((65, 270, 300, 60), DKGREEN),
    ((915, 270, 300, 60), DKGREEN),
    ((610, 150, 60, 230), DKGREEN),
    ((205, 100, 150, 20), DKGREEN),
    ((925, 100, 150, 20), DKGREEN),
)


class Particle(Rect2):
    def __init__(self, width, height, radius, cooldown, duration, color):
        super().__init__(left=0, top=0, width=width, height=height)
        self.radius = radius
        self.cooldown = cooldown
        self.duration = duration
        self.color = color


class MeleeParticle(Particle):
    def __init__(self, particle):
        super().__init__(particle.width, particle.height, particle.radius, particle.cooldown, particle.duration, particle.color)
        self.total_time = particle.cooldown + particle.duration
        self.expired = False
        self.spawn_time = 0

    def update(self, time, player):
        if self.spawn_time == 0:
            self.spawn_time = time

        elapsed_time = time - self.spawn_time
        self.expired = (elapsed_time >= self.duration)
        r = (elapsed_time / self.duration)
        arc = math.pi / 2

        if player.facing_direction == RIGHT:
            self.centerx = player.centerx + self.radius * math.cos((1 - r) * arc)
        else:
            self.centerx = player.centerx - self.radius * math.cos((1 - r) * arc)

        self.centery = player.centery - self.radius * math.sin((1 - r) * arc)


attack_particle = Particle(width=30, height=30, radius=35, cooldown=1000, duration=500, color=YELLOW)
# -------------------------------------------------------------------------


class GameTime:
    def __init__(self):
        self.qsec = 0

    def __call__(self):
        return self.qsec

    def inc(self):
        self.qsec += 1

    @property
    def msec(self):
        return self.qsec * 250

    def as_seconds(self):
        return self.qsec / 4

    def as_half_seconds(self):
        return self.qsec / 2

    def as_quarter_seconds(self):
        return self.qsec

    def __str__(self):
        sec = self.qsec / 4
        return '{:>2}:{:0>2}'.format(str(int(sec / 60)), str(int(sec % 60)))