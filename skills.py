from globals import *

import pygame
from pygame.locals import *

import math
import classes
SKILLS_TABLE = {}

#Skill ID guide: 
#     -1 : meditate
#      0 : empty
#   1-99 : for auto attacks
# 100-999: for skills
# 1000+  : for ultimate


def initialize_skill_table():
    #Meditate
    SKILLS_TABLE[-1] = {'type': None, 'start':blank_function, 'cooldown':3000}
    #Slap (Default auto attack)
    SKILLS_TABLE[1] = _auto_melee(30,30,math.pi/2, 35, 500,500,YELLOW,10,0)
    #Teleport
    SKILLS_TABLE[100] = {'type': None,'start':teleport_function,'cooldown':500,'energy': 5}


#Templates=================================================
def _auto_melee(width, height, arc, radius, cooldown, duration, color, dmg, energy):
    return {'type': MELEE,
            'start': (lambda sid,p : classes.MeleeParticle(sid,p)),
            'width': width,
            'height': height,
            'arc': arc,
            'radius': radius,
            'cooldown': cooldown,
            'duration': duration,
            'color': color,
            'dmg': dmg,
            'energy': energy
           }
           
#Individual skills =========================================   

#Used for meditation
def blank_function(sid,player):
    return None
    
def teleport_function(sid,player):
    if player.energy >= SKILLS_TABLE[sid]['energy']:
        if player.facing_direction == RIGHT:
            player.left += 100
        else:
            player.left -= 100
        player.energy -= SKILLS_TABLE[sid]['energy']
    return None