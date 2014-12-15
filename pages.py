# python standard library modules
import os
import sys
import textwrap
import pygbutton

# pygame
import pygame
from pygame.locals import *

# our modules
import globals as GL
from globals import *
from classes import *
from pygbutton import *


class StartMenu:
    def __init__(self):
        self.bg_image = pygame.image.load('data/background2.png')
        self.start_button = PygButton((325, 385, 140, 40), 'Start')
        self.help_button = PygButton((485, 385, 110, 40), 'Help')
        self.options_button = PygButton((615, 385, 175, 40), 'Options')
        self.exit_button = PygButton((810, 385, 105, 40), 'Exit')
        if AUDIO.music_on:
            AUDIO.turn_on_music()
        title_font = pygame.font.Font('data/Kremlin.ttf', 50)
        self.title_font1 = title_font.render('Famished', True, DKRED)
        self.title_font2 = title_font.render('Tournament', True, DKRED)

    def __call__(self):
        self.return_now = False
        while not self.return_now:
            self.draw()
            self.input()
            self.events()
            GL.CLOCK.tick(GL.FPS)

    def draw(self):
        GL.SCREEN.blit(self.bg_image, (0, 0))
        self.start_button.draw(GL.SCREEN)
        self.help_button.draw(GL.SCREEN)
        self.options_button.draw(GL.SCREEN)
        self.exit_button.draw(GL.SCREEN)
        GL.SCREEN.blit(self.title_font1, (495, 120))
        GL.SCREEN.blit(self.title_font2, (450, 175))
        pygame.display.update()

    def input(self):
        GL.INPUT1.refresh()
        if GL.INPUT1.SELECT:
            EXIT_GAME()
        if GL.INPUT1.START:
            GL.INPUT1.START = False
            self.return_now = True
            GL.NEXT_PAGE = 'playerSelect'

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                EXIT_GAME()
            if 'click' in self.exit_button.handleEvent(event):
                EXIT_GAME()
            if 'click' in self.start_button.handleEvent(event):
                self.return_now = True
                GL.NEXT_PAGE = 'playerSelect'
            if 'click' in self.help_button.handleEvent(event):
                self.return_now = True
                GL.NEXT_PAGE = 'help'
            if 'click' in self.options_button.handleEvent(event):
                self.return_now = True
                GL.NEXT_PAGE = 'options'

#----------------------------------------------------------------------------------------
class PlayerSelectPage:

    def __init__(self):
        def _setup_display():
            pygame.display.set_mode((1280, 600))
            pygame.display.set_caption('Famished Tournament')
            self.screen = pygame.display.get_surface()

            self.return_button = pygbutton.PygButton((0, 550, 300, 50), 'Main Menu')

            self.player1_spritesheet = None
            self.player2_spritesheet = None

        #def _setup_players():
            #self.player1 = Player(id=1, size=(30,40), input = GL.INPUT1)
           # self.player2 = Player(id=2, size=(30,40), input = GL.INPUT2)

        def _load_images():
            self.humanPortrait = pygame.image.load('data/portrait_human.png')
            self.elfPortrait = pygame.image.load('data/portrait_elf.png')
            self.androidPortrait = pygame.image.load('data/portrait_andriod.png')

            self.portraits = [self.humanPortrait, self.elfPortrait, self.androidPortrait]
            self.portraits2 = [self.humanPortrait, self.elfPortrait, self.androidPortrait] #SWITCH TO SAME ORDER ONCE WE HAVE OTHER SPRITES

            #show human portrait by default
            self.index = 0
            self.index2 = 0

        def _setup_fonts():
            self.start_font = pygame.font.Font('data/Kremlin.ttf', 50)
            self.start_font_xy = font_position_center(GL.SCREEN.get_rect(), self.start_font, '---------------Press Start when ready---------------')

        def _setup_flags():
            self.ready1 = False
            self.ready2 = True #FOR TESTING. SET BACK TO FALSE
            self.start = False

        _setup_display()
        _setup_fonts()
        _setup_flags()
        _load_images()

    def __call__(self):
        self.return_now = False
        while not self.return_now:
            self.draw()
            self.input()
            self.events()
            GL.CLOCK.tick(5)

    def draw(self):
        self.image = pygame.image.load('data/player_select_bkg.png')
        GL.SCREEN.blit(self.image, (0,0))

        self.return_button.draw(GL.SCREEN)

        GL.SCREEN.blit(self.portraits[self.index], (167, 106))
        GL.SCREEN.blit(self.portraits2[self.index2], (810, 106))

        pygame.display.update()


    def input(self):

        def refresh_inputs():
            GL.INPUT1.refresh()
            GL.INPUT2.refresh()

            if GL.INPUT1.SELECT or GL.INPUT2.SELECT:
                GL.NEXT_PAGE = 'start'

        def player_select_inputs():

            def check_other_player(player):
                if player == 'player1':
                    if self.index == self.index2 and self.ready2: #player 2 is using character, skip index
                        self.index = self.index + 1
                        if self.index >= len(self.portraits):
                            self.index = 0
                else:
                    if self.index == self.index2 and self.ready1: #player 2 is using character, skip index
                        self.index2 = self.index2 + 1
                        if self.index2 >= len(self.portraits2):
                            self.index2 = 0

            if GL.INPUT1.LEFT:
                self.index = self.index - 1
                if self.index < 0:
                    self.index = len(self.portraits) - 1

                check_other_player('player1')


            elif GL.INPUT1.RIGHT:
                self.index = self.index + 1
                if self.index >= len(self.portraits):
                    self.index = 0

                check_other_player('player1')

            if GL.INPUT2.LEFT:
                self.index2 = self.index2 - 1
                if self.index2 < 0:
                    self.index2 = len(self.portraits2)- 1

                check_other_player('player2')

            elif GL.INPUT2.RIGHT:
                self.index2 = self.index2 + 1
                if self.index2 >= len(self.portraits2):
                    self.index2 = 0

                check_other_player('player2')




        def player_done_selecting():
            #if player presses A
            #they selected sprite
            #set sprite to player
            #if they pressed select
            #they want to select a different sprite or return to start screen
            if GL.INPUT1.JUMP:
                GL.INPUT1.JUMP = False
                if self.ready2 and self.index2 == self.index:
                    print('Player 2 is using this character. Select a different one.')

                else:
                    print('player 1 ready')
                    self.ready1 = True

            elif GL.INPUT2.JUMP:
                GL.INPUT2.JUMP = False
                if self.ready1 and self.index2 == self.index:
                    print('Player 1 is using this character. Select a different one.')

                else:
                    print('player 2 ready')
                    self.ready2 = True

            elif GL.INPUT1.SELECT:
                self.ready1 = False

            elif GL.INPUT2.SELECT:
                self.ready2 = False

            elif (GL.INPUT1.SELECT and not self.ready1) or (GL.INPUT2.SELECT and not self.ready2):
                GL.NEXT_PAGE = 'start'

        def ready_for_start():

            if self.ready1 and self.ready2:

                start_font = self.start_font.render('---------------Press Start when ready---------------', True, YELLOW)
                GL.SCREEN.blit(start_font, self.start_font_xy)
                pygame.display.update()

                if GL.INPUT1.START or GL.INPUT2.START:
                    GL.INPUT1.START = False
                    GL.INPUT2.START = False
                #if self.ready1 == True and self.ready2 == True:
                    self.start = True
                    print('setting sprites')
                    set_sprites()
                    print('set sprites')
                    print('going to level select screen')
                    GL.NEXT_PAGE = 'levelSelect'
                    self.return_now = True

                #elif self.ready1 == True and self.ready2 == False:
                    #print ('Player 2 not ready')

                #elif self.ready1 ==False and self.ready2 == True:
                      #print('Player 1 not ready')

        def set_sprites():
            #set spritesheet for player1
            if self.index == 0: #human
                self.player1_spritesheet = 'data/p1_human_8bit.png'
            elif self.index == 1: #elf
                self.player1_spritesheet = 'data/p2_human_8bit.png' #NEED TO CHANGE THIS WITH ELF SPRITE SHEET
            elif self.index == 2:
                self.player1_spritesheet = 'data/green_human.png' #NEED TO CHANGED WITH ANDROID SPRITE

            if self.index2 == 0: #human
                self.player2_spritesheet = 'data/p1_human_8bit.png' #CHANGE ORDER WHEN WE HAVE FINAL SPRITES
            elif self.index2 == 1: #elf
                self.player2_spritesheet = 'data/p2_human_8bit.png'
            elif self.index2 == 2:
                self.player2_spritesheet = 'data/green_human.png'

            GL.set_player1_spritesheet(self.player1_spritesheet)
            GL.set_player2_spritesheet(self.player2_spritesheet)

        refresh_inputs()
        player_select_inputs()
        player_done_selecting()
        ready_for_start()

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                EXIT_GAME()
            if 'click' in self.return_button.handleEvent(event):
                self.return_now = True
                GL.NEXT_PAGE = 'start'

#----------------------------------------------------------------------------------------
class LevelSelectPage:

    def __init__(self):
        def _setup_display():
            pygame.display.set_mode((1280, 600))
            pygame.display.set_caption('Famished Tournament')
            self.screen = pygame.display.get_surface()

            self.return_button = pygbutton.PygButton((0, 550, 300, 50), 'Main Menu')

            self.ready = False

        def _load_images():
            self.humanLevel = pygame.image.load('data/humanLevel.png')
            self.elfLevel = pygame.image.load('data/vinesLevel.png')
            self.androidLevel = pygame.image.load('data/androidLevel.png')

            self.levels = [self.humanLevel, self.elfLevel, self.androidLevel]
            self.outerX = [19, 444, 874]
            self.innerX = [24, 450, 878]

            self.index = 0

        _setup_display()
        _load_images()

    def __call__(self):
        self.return_now = False
        while not self.return_now:
            self.input()
            self.draw()
            self.events()
            GL.CLOCK.tick(5)

    def draw(self):

        self.image = pygame.image.load('data/level_select_bkg.png')
        GL.SCREEN.blit(self.image, (0,0))

        outer_highlight = Rect2(topleft=(self.outerX[self.index], 184), size = (389, 173), color=(20, 118, 128))
        inner_highlight = Rect2(topleft=(self.innerX[self.index], 190), size=(379, 162), color=(80, 191, 201))

        pygame.draw.rect(GL.SCREEN, outer_highlight.color, outer_highlight)
        pygame.draw.rect(GL.SCREEN, inner_highlight.color, inner_highlight)

        self.image2 = pygame.image.load('data/level_select_bkg2.png')
        GL.SCREEN.blit(self.image2, (0,0))

        self.return_button.draw(GL.SCREEN)
        #GL.SCREEN.blit(self.levels[self.index], (60, 40))

        pygame.display.update()

    #only player 1 can select level
    def input(self):
        GL.INPUT1.refresh()

        if GL.INPUT1.LEFT:
            self.index = self.index - 1
            if self.index < 0:
                self.index = len(self.levels) - 1

        elif GL.INPUT1.RIGHT:
            self.index = self.index + 1
            if self.index >= len(self.levels):
                self.index = 0

        def ready_check():
            if GL.INPUT1.JUMP:
                print('ready to load')
                self.ready = True
                set_level()
                GL.NEXT_PAGE = 'GameLoop()'
                self.return_now = True

        def set_level():
            print ('setting level')
            if self.index == 0:
                arena = arena4
            elif self.index == 1:
                arena = arena3
            elif self.index == 2:
                arena = arena5

            GL.set_level(arena)
            print ('set level')

        ready_check()


    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                EXIT_GAME()
            if 'click' in self.return_button.handleEvent(event):
                self.return_now = True
                GL.NEXT_PAGE = 'start'
#----------------------------------------------------------------------------------------
class HelpPage:
    def __init__(self):
        self.return_button = pygbutton.PygButton((0, 550, 300, 50), 'Main Menu')
        self.section_font = pygame.font.Font('data/Kremlin.ttf', 40)
        self.font = pygame.font.Font('data/arial_narrow_7.ttf', 20)
        self.bg_image = pygame.image.load('data/help.png')
        self.bg_title = self.section_font.render('Background', True, WHITE)
        self.bg_text = textwrap.wrap('Under the tyranny of the dark overlord, the world' +
                                     'is in chaos and all the resources are nearly depleted. ' +
                                     'Entire populations have been subjugated to life in labor ' +
                                     'camps, brutally policed by the overlord\'s military forces. ' +
                                     'As your people\'s champion, you must fight to the death in the ' +
                                     'battle arena to win much needed resources.', width=50)
        self.goals_title = self.section_font.render('Goals', True, WHITE)
        self.goals_text = textwrap.wrap('Ultimately, you want to slay your opponent. ' +
                                        'To become a better fighter, kill the monsters, gain ' +
                                        'experience, and pick up skills. The player to land ' +
                                        'the last hit on the monster will receives the experience ' +
                                        'points. An ultimate boss will spawn every few ' +
                                        'minutes. These bosses drop ultimate skills which ' +
                                        'will help you humiliate and destroy your opponent.', width=50)

    def __call__(self):
        self.return_now = False
        while not self.return_now:
            self.draw()
            self.input()
            self.events()
            GL.CLOCK.tick(GL.FPS)

    def draw(self):
        GL.SCREEN.fill(BLACK)
        GL.SCREEN.blit(self.bg_image, (0, 0))

        GL.SCREEN.blit(self.bg_title, (800, 40))
        for num, text in enumerate(self.bg_text):
            line = self.font.render(text, True, DKRED)
            GL.SCREEN.blit(line, (800, 90 + (num * 20)))

        GL.SCREEN.blit(self.goals_title, (800, 250))
        for num, text in enumerate(self.goals_text):
            line = self.font.render(text, True, DKRED)
            GL.SCREEN.blit(line, (800, 300 + (num * 20)))

        self.return_button.draw(GL.SCREEN)
        pygame.display.update()

    def input(self):
        GL.INPUT1.refresh()
        if GL.INPUT1.SELECT:
            GL.INPUT1.SELECT = False
            self.return_now = True
            GL.NEXT_PAGE = 'start'

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                EXIT_GAME()
            if 'click' in self.return_button.handleEvent(event):
                self.return_now = True
                GL.NEXT_PAGE = 'start'


class OptionsPage:
    def __init__(self):
        self.bg_image = pygame.image.load('data/temp_start_bkg.png')
        self.active_colors = BLACK, DKRED
        self.inactive_colors = DKRED, BLACK
        self.music_on_button = pygbutton.PygButton((650, 200, 60, 50), 'ON')
        self.music_off_button = pygbutton.PygButton((730, 200, 80, 50), 'OFF')
        self.effects_on_button = pygbutton.PygButton((770, 260, 60, 50), 'ON')
        self.effects_off_button = pygbutton.PygButton((850, 260, 80, 50), 'OFF')
        self.return_button = pygbutton.PygButton((0, 550, 300, 50), 'Main Menu')
        font = pygame.font.Font('data/Kremlin.ttf', 40)
        self.bg_font = font.render('Music:', True, DKRED)
        self.se_font = font.render('Sound Effects:', True, DKRED)

    def __call__(self):
        self.return_now = False
        while not self.return_now:
            self.draw()
            self.input()
            self.events()
            GL.CLOCK.tick(GL.FPS)

    def draw(self):
        if AUDIO.music_on:
            self.music_on_button.fgcolor, self.music_on_button.bgcolor = self.active_colors
            self.music_off_button.fgcolor, self.music_off_button.bgcolor = self.inactive_colors
        else:
            self.music_on_button.fgcolor, self.music_on_button.bgcolor = self.inactive_colors
            self.music_off_button.fgcolor, self.music_off_button.bgcolor = self.active_colors

        if AUDIO.sound_on:
            self.effects_on_button.fgcolor, self.effects_on_button.bgcolor = self.active_colors
            self.effects_off_button.fgcolor, self.effects_off_button.bgcolor = self.inactive_colors
        else:
            self.effects_on_button.fgcolor, self.effects_on_button.bgcolor = self.inactive_colors
            self.effects_off_button.fgcolor, self.effects_off_button.bgcolor = self.active_colors

        GL.SCREEN.blit(self.bg_image, (0, 0))
        GL.SCREEN.blit(self.bg_font, (500, 200))
        GL.SCREEN.blit(self.se_font, (400, 260))
        self.music_on_button.draw(GL.SCREEN)
        self.music_off_button.draw(GL.SCREEN)
        self.effects_on_button.draw(GL.SCREEN)
        self.effects_off_button.draw(GL.SCREEN)
        self.return_button.draw(GL.SCREEN)
        pygame.display.update()

    def input(self):
        GL.INPUT1.refresh()
        if GL.INPUT1.SELECT:
            GL.INPUT1.SELECT = False
            self.return_now = True
            GL.NEXT_PAGE = 'start'

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                EXIT_GAME()

            if 'click' in self.music_on_button.handleEvent(event):
                AUDIO.turn_on_music()

            if 'click' in self.music_off_button.handleEvent(event):
                AUDIO.turn_off_music()

            if 'click' in self.effects_on_button.handleEvent(event):
                AUDIO.turn_on_effects()

            if 'click' in self.effects_off_button.handleEvent(event):
                AUDIO.turn_off_effects()

            if 'click' in self.return_button.handleEvent(event):
                self.return_now = True
                GL.NEXT_PAGE = 'start'