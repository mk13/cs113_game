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
from pygbutton import *


class StartMenu:
    def __init__(self):
        self.bg_image = pygame.image.load('data/temp_start_bkg.png')
        self.start_button = PygButton((325, 395, 140, 40), 'Start')
        self.help_button = PygButton((485, 395, 110, 40), 'Help')
        self.options_button = PygButton((615, 395, 175, 40), 'Options')
        self.exit_button = PygButton((810, 395, 105, 40), 'Exit')
        AUDIO.turn_on_music()
        title_font = pygame.font.Font('data/Kremlin.ttf', 50)
        self.title_font1 = title_font.render('Famished', True, DKRED)
        self.title_font2 = title_font.render('Tournament', True, DKRED)

    def __call__(self):
        self.return_now = False
        while not self.return_now:
            self.draw()
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

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                EXIT_GAME()
            if 'click' in self.exit_button.handleEvent(event):
                EXIT_GAME()
            if 'click' in self.start_button.handleEvent(event):
                self.return_now = True
                # GL.NEXT_PAGE = 'game'
                GL.NEXT_PAGE = 'GameLoop()'
            if 'click' in self.help_button.handleEvent(event):
                self.return_now = True
                GL.NEXT_PAGE = 'help'
            if 'click' in self.options_button.handleEvent(event):
                self.return_now = True
                GL.NEXT_PAGE = 'options'


class HelpPage:
    def __init__(self):
        self.return_button = pygbutton.PygButton((0, 550, 300, 50), 'Main Menu')
        self.section_font = pygame.font.Font('data/Kremlin.ttf', 40)
        self.font = pygame.font.Font('data/arial_narrow_7.ttf', 20)
        self.bg_image = pygame.image.load('data/Evil_Eyes.png')
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
            self.events()
            GL.CLOCK.tick(GL.FPS)

    def draw(self):
        GL.SCREEN.fill(BLACK)
        GL.SCREEN.blit(self.bg_image, (0, 245))

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
