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
            
            self.player1 = Player(id=1, left=200, top=150, width=30, height=40)
            self.player1_eyeball = Rect2(left=200, top=150, width=5, height=5)
            #self.player2 = Player(id=2, left=1080, top=150, width=30, height=40)
            #self.player2_eyeball = Rect2(left=1080, top=150, width=5, height=5)
            
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
            #Scrolling text font
            self.st_font = pygame.font.Font('data/gigi.ttf', 30)

        def _setup_particles():
            self.active_particles = []
            
        def _setup_monsters():
            self.active_monsters = []
            
            #TEST - Monster
            self.active_monsters.append(Monster(ULTIMATE, 400, 150, self.player1, self.player1))
            #self.active_monsters.append(Monster(MEDIUM, 400, 150, self.player1, self.player1))
            #self.active_monsters.append(Monster(WEAK, 400, 150, self.player1, self.player1))
                    
        pygame.init()
        initialize_skill_table()
        _setup_display()
        _setup_time()
        _setup_input()
        _setup_Rects()
        _setup_monsters()
        _setup_fonts()
        _setup_particles()

    # ------------------------------------------------------------------------
    def __call__(self):
        while True:
            self.handle_player_input()
            self.handle_monsters()
            self.handle_particles()
            self.draw_screen()
            self.handle_event_queue()
            self.clock.tick(self.fps)

    # -------------------------------------------------------------------------
    def handle_player_input(self):

        def _special_input():
            if self.input.RESET:
                self.player1.topleft = self.player1.topleft_initial

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
        self.player1(self.input, self.arena)
        _special_input()

    def handle_particles(self):

        def _update_active_particles():
            if self.player1.new_particle:
                self.active_particles.append(self.player1.new_particle)
                self.player1.new_particle = None
                #Added this part into player inputs; causing bugs if skill doesn't create particle
                #pygame.time.set_timer(USEREVENT + 2, self.player1.new_particle.cooldown)

        def _update_particles():
            for p in self.active_particles:
                if p.expired:
                    self.active_particles.remove(p)
                else:
                    p.update(self.game_time.msec)#, self.player1)
                    
        def _check_particle_collisions():
            for p in self.active_particles:
                #opposite = self.player2 if p.belongs_to == self.player1 else \
                #           self.player1
                if isinstance(p,RangeParticle):
                    if p.p_collidelist(self.arena.rects) != -1:
                        self.active_particles.remove(p)
                    #else: destructible terrain collision here
                    else:
                        first_hit = p.collidelist(self.active_monsters)
                        if first_hit != -1:
                            p.on_hit(self.active_monsters[first_hit], self.game_time.msec)
                            self.active_particles.remove(p)
                        #else:
                        #    if p.colliderect(opposite):
                        #        p.on_hit(opposite, self.game_time.msec)
                        #        self.active_particles.remove(p)
                else:
                    allhit = p.collidelistall(self.active_monsters)
                    for i in allhit:
                        p.on_hit(self.active_monsters[i], self.game_time.msec)
                    #if p.colliderect(opposite):
                    #    p.on_hit(opposite, self.game_time.msec)
                        

        _update_active_particles()
        _update_particles()
        _check_particle_collisions()
    # -------------------------------------------------------------------------
    def handle_monsters(self):
        for m in self.active_monsters:
            if m.is_dead():
                self.active_monsters.remove(m)
            else:
                m(self.game_time.msec, self.arena)
    
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
            health_display = self.health_font.render(str(self.player1.hit_points), True, RED)
            energy_display = self.energy_font.render(str(int(self.player1.energy)), True, YELLOW)
            self.surface.blit(health_display, self.health_font_xy)
            self.surface.blit(energy_display, self.energy_font_xy)

        def _draw_timer():
            time_display = self.timer_font.render(str(self.game_time), True, BLUE)
            self.surface.blit(time_display, self.timer_font_xy)

        def _draw_debug():
            x = '| x:{:>8.2f}|'.format(self.player1.x)
            y = '| y:{:>8.2f}|'.format(self.player1.y)
            dx = '|dx:{:>8.2f}|'.format(self.player1.dx)
            dy = '|dy:{:>8.2f}|'.format(self.player1.dy)

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
            pygame.draw.rect(self.surface, LBLUE, self.player1)
            if self.player1.facing_direction == LEFT:
                self.player1_eyeball.topleft = self.player1.topleft
                self.player1_eyeball.move_ip((+3, 3))
            else:
                self.player1_eyeball.topright = self.player1.topright
                self.player1_eyeball.move_ip((-3, 3))
            pygame.draw.rect(self.surface, DKRED, self.player1_eyeball)
            
        def _draw_monsters():
            for m in self.active_monsters:
                pygame.draw.rect(self.surface, ORANGE, m)

        def _draw_particles():
            for p in self.active_particles:
                pygame.draw.rect(self.surface, p.color, p)
                
        def _draw_scrolling_text():
            for t in self.player1.st_buffer:
                self.surface.blit(self.st_font.render("-"+str(int(t[0])), True, RED), \
                (self.player1.centerx, self.player1.top - (3000 - t[1] + self.game_time.msec)/50))
                if t[1] <= self.game_time.msec: 
                    self.player1.st_buffer.remove(t)
            #for t in self.player2.st_buffer:
            #    self.surface.blit(self.st_font.render("-"+str(int(t[0])), True, RED), \
            #    (self.player2.centerx, self.player2.top - (3000 - t[1] + self.game_time.msec)/50))
            #    if t[1] <= self.game_time.msec: 
            #        self.player2.st_buffer.remove(t)
            for m in self.active_monsters:
                for t in m.st_buffer:
                    self.surface.blit(self.st_font.render("-"+str(int(t[0])), True, RED), \
                    (m.centerx, m.top - (3000 - t[1] + self.game_time.msec)/50))
                    if t[1] <= self.game_time.msec: 
                        m.st_buffer.remove(t)
                

        _draw_ui()
        _draw_timer()
        _draw_debug()
        _draw_map()
        _draw_monsters()
        _draw_players()
        _draw_particles()
        _draw_scrolling_text()
        pygame.display.update()  # necessary to update the display

    # -------------------------------------------------------------------------
    def handle_event_queue(self):
        # loop through all pygame events
        for event in pygame.event.get():
            # update game timer
            # handle conditions
            if event.type == TIME_TICK_EVENT:
                self.game_time.inc()
                
                #Player 1 conditions
                for k,v in self.player1.conditions.items():
                    for e in v:
                        if e.is_expired(self.game_time.msec):
                            self.player1.conditions[k].remove(e)
                            
                #Player 2 conditions
                #for k,v in self.player2.conditions.items():
                #    for e in v:
                #        if e.is_expired(self.game_time.msec):
                #            self.player2.conditions[k].remove(e)
                
                #Monster conditions
                for m in self.active_monsters:
                    for k,v in m.conditions.items():
                        for e in v:
                            if e.is_expired(self.game_time.msec):
                                m.conditions[k].remove(e)

            if event.type == REGENERATION_EVENT:
                if self.player1.conditions[WOUNDED] and not self.player1.conditions[INVIGORATED]:
                    self.player1.hit_points += self.player1.level/20
                elif not self.player1.conditions[WOUNDED] and self.player1.conditions[INVIGORATED]:
                    self.player1.hit_points += self.player1.level/5
                else:
                    self.player1.hit_points += self.player1.level/10
                if self.player1.hit_points > 100:
                    self.player1.hit_points = 100
                
                if self.player1.conditions[WEAKENED] and not self.player1.conditions[EMPOWERED]:
                    self.player1.energy += self.player1.level/10
                elif not self.player1.conditions[WEAKENED] and self.player1.conditions[EMPOWERED]:
                    self.player1.energy += self.player1.level/2.5
                else:
                    self.player1.energy += self.player1.level/5
                if self.player1.energy > 10:
                    self.player1.energy = 10

            # player 1 skill lock timer
            if event.type == PLAYER1_LOCK_EVENT:
                self.player1.attack_cooldown_expired = True
                pygame.time.set_timer(PLAYER1_LOCK_EVENT, 0)

            if event.type == PLAYER1_MEDITATE_EVENT:
                self.player1.energy += 5
                if self.player1.energy > 10:
                    self.player1.energy = 10
                pygame.time.set_timer(PLAYER1_MEDITATE_EVENT, 0)
                
            # QUIT event occurs when click X on window bar
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

# -------------------------------------------------------------------------
if __name__ == '__main__':
    GameLoop()()
