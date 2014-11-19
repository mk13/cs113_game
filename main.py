# python standard library modules
import os
import sys

# pygame
import pygame
from pygame.locals import *

# our modules
from classes import *
from globals import *
from skills import * 

# set window starting position for my desktop which has multiple monitors, this
# is a convenience thing for me.  You guys can add your own setting here if
# it's useful for you
if os.environ['COMPUTERNAME'] == 'BRIAN-DESKTOP':
    os.environ['SDL_VIDEO_WINDOW_POS'] = '{},{}'.format(1920, 90)
if os.environ['COMPUTERNAME'] == 'MAX-LT':
    os.environ['SDL_VIDEO_WINDOW_POS'] = '{},{}'.format(50, 30)

# @PYGAMERUNSPECIAL  setting for my IDE
# -------------------------------------------------------------------------


class GameLoop:
    def __init__(self):
        def _setup_display():
            # set the window size - can add the NOFRAME arg if we don't want a
            # window frame but then we have to figure out how to move the
            # window since it won't have a menu bar to grab
            pygame.display.set_mode((1280, 600))
            pygame.display.set_caption('Famished Tournament')
            self.surface = pygame.display.get_surface()

        def _setup_time():
            self.clock = pygame.time.Clock()
            self.fps = 30
            pygame.time.set_timer(TIME_TICK_EVENT, 250)
            pygame.time.set_timer(REGENERATION_EVENT, 1000)
            self.game_time = GameTime()

        def _setup_input():
            pygame.key.set_repeat(100, 10)  # allow multiple KEYDOWN events
            self.input = Input()

        def _setup_Rects():
            self.window = self.surface.get_rect()
            self.window_border = Rect2(left=0, top=0, width=1278, height=600)
            self.play_area = Rect2(left=65, top=0, width=1150, height=475)
            self.play_area_border = Rect2(left=40, top=0, width=1200, height=500)
            self.player = Player(id=1, left=200, top=150, width=30, height=40)
            self.player_eyeball = Rect2(left=200, top=150, width=5, height=5)
            self.arena = arena1

        def _setup_fonts():
            self.timer_font = pygame.font.Font('data/gigi.ttf', 36)
            self.timer_font_xy = 640, 500
            self.health_font = pygame.font.Font('data/gigi.ttf', 55)
            self.health_font_xy = 60, 480
            self.energy_font = pygame.font.Font('data/gigi.ttf', 55)
            self.energy_font_xy = 80, 525
            self.pause_font = pygame.font.Font('data/gigi.ttf', 200)
            self.pause_font_xy = font_position_center((self.window.w, self.window.h), self.pause_font, '-PAUSE-')
            self.debug_font = pygame.font.SysFont('consolas', 20)  # monospace
            self.debug_font_xy1 = 1000, 505
            self.debug_font_xy2 = 1000, 520
            self.debug_font_xy3 = 1000, 540
            self.debug_font_xy4 = 1000, 560

        def _setup_particles():
            self.active_particles = []

        pygame.init()
        initialize_skill_table()
        _setup_display()
        _setup_time()
        _setup_input()
        _setup_Rects()
        _setup_fonts()
        _setup_particles()

    # ------------------------------------------------------------------------
    def __call__(self):
        while True:
            self.handle_player_input()
            self.handle_particles()
            self.draw_screen()
            self.handle_event_queue()
            self.clock.tick(self.fps)

    # -------------------------------------------------------------------------
    def handle_player_input(self):

        def _special_input():
            if self.input.RESET:
                self.player.topleft = self.player.topleft_initial

            if self.input.DEBUG:
                rendered_font = self.pause_font.render('-PAUSE-', True, RED)
                self.surface.blit(rendered_font, self.pause_font_xy)
                pygame.display.update()
                try:
                    exec(input('\nEnter something to exec: '))
                except Exception as err:
                    print('>> {}: {} <<'.format(type(err).__name__, err))

            if self.input.EXIT:
                # Add the QUIT event to the pygame event queue to be handled
                # later, at the same time the QUIT event from clicking the
                # window X is handled
                pygame.event.post(pygame.event.Event(QUIT))
        
        self.input.refresh()
        self.player(self.input, self.arena)
        _special_input()

    def handle_particles(self):

        def _update_active_particles():
            if self.player.new_particle:
                self.active_particles.append(self.player.new_particle)
                self.player.new_particle = None
                #Added this part into player inputs; causing bugs if skill doesn't create particle
                #pygame.time.set_timer(USEREVENT + 2, self.player.new_particle.cooldown)

        def _update_particles():
            for p in self.active_particles:
                if p.expired:
                    self.active_particles.remove(p)
                else:
                    p.update(self.game_time.msec)#, self.player)

        _update_active_particles()
        _update_particles()

    # -------------------------------------------------------------------------
    def draw_screen(self):
        def _draw_ui():
            # fill background dark grey
            self.surface.fill(DGREY)

            # thin green border of surface
            pygame.draw.rect(self.surface, GREEN, self.window_border, 1)

            # red border of playable movement space
            pygame.draw.rect(self.surface, DKRED, self.play_area_border)

            # font for health indicator, for testing purposes only
            health_display = self.health_font.render(str(self.player.hit_points), True, RED)
            energy_display = self.energy_font.render(str(self.player.energy), True, YELLOW)
            self.surface.blit(health_display, self.health_font_xy)
            self.surface.blit(energy_display, self.energy_font_xy)

        def _draw_timer():
            time_display = self.timer_font.render(str(self.game_time), True, BLUE)
            self.surface.blit(time_display, self.timer_font_xy)

        def _draw_debug():
            x = '| x:{:>8.2f}|'.format(self.player.x)
            y = '| y:{:>8.2f}|'.format(self.player.y)
            dx = '|dx:{:>8.2f}|'.format(self.player.dx)
            dy = '|dy:{:>8.2f}|'.format(self.player.dy)

            debug_font = self.debug_font.render(x, True, GREEN)
            self.surface.blit(debug_font, self.debug_font_xy1)

            debug_font = self.debug_font.render(y, True, GREEN)
            self.surface.blit(debug_font, self.debug_font_xy2)

            debug_font = self.debug_font.render(dx, True, GREEN)
            self.surface.blit(debug_font, self.debug_font_xy3)

            debug_font = self.debug_font.render(dy, True, GREEN)
            self.surface.blit(debug_font, self.debug_font_xy4)

        def _draw_map():
            for rect, rect_color in self.arena:
                if rect_color is not None:
                    pygame.draw.rect(self.surface, rect_color, rect)

        def _draw_players():
            # placeholder for a playable character; is movable
            pygame.draw.rect(self.surface, LBLUE, self.player)
            if self.player.facing_direction == LEFT:
                self.player_eyeball.topleft = self.player.topleft
                self.player_eyeball.move_ip((+3, 3))
            else:
                self.player_eyeball.topright = self.player.topright
                self.player_eyeball.move_ip((-3, 3))
            pygame.draw.rect(self.surface, DKRED, self.player_eyeball)

        def _draw_particles():
            for p in self.active_particles:
                pygame.draw.rect(self.surface, p.color, p)

        _draw_ui()
        _draw_timer()
        _draw_debug()
        _draw_map()
        _draw_players()
        _draw_particles()
        pygame.display.update()  # necessary to update the display

    # -------------------------------------------------------------------------
    def handle_event_queue(self):
        # loop through all pygame events
        for event in pygame.event.get():
            # update game timer
            if event.type == TIME_TICK_EVENT:
                self.game_time.inc()

            if event.type == REGENERATION_EVENT:
                self.player.hit_points += self.player.level/10
                if self.player.hit_points > 100:
                    self.player.hit_points = 100
                self.player.energy += self.player.level/5
                if self.player.energy > 10:
                    self.player.energy = 10

            # player 1 skill lock timer
            if event.type == PLAYER1_LOCK_EVENT:
                self.player.attack_cooldown_expired = True
                pygame.time.set_timer(PLAYER1_LOCK_EVENT, 0)

            if event.type == PLAYER1_MEDITATE_EVENT:
                self.player.energy += 5
                if self.player.energy > 10:
                    self.player.energy = 10
                pygame.time.set_timer(PLAYER1_MEDITATE_EVENT, 0)
                
            # QUIT event occurs when click X on window bar
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

# -------------------------------------------------------------------------
if __name__ == '__main__':
    GameLoop()()
