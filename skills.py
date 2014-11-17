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

#NOTE:
#   COOLDOWN: How long it locks your character
#   DURATION: How long the particle lives

#   Do not worry about subtracting energy costs,
#   player input function will handle that.

#   RangeParticles can have two paths. The default
#   which just uses velocity and acceleration
#   It also pays attention to 'up' and 'down',
#   whether player pressed up or down.
#   Melee particles do not care about up or down.

def initialize_skill_table():
    #Meditate
    SKILLS_TABLE[-1] = {'type': None, 'start':blank_function, 'cooldown':3000, 'energy': 0}
    #Slap (Default auto attack)
    SKILLS_TABLE[1] = _auto_melee(30,30,math.pi/2, 35, 500,500,YELLOW,10,0)
    #Teleport
    SKILLS_TABLE[100] = {'type': None,'start':teleport_function,'cooldown':500,'energy': 5}
    #FIREBALL!
    SKILLS_TABLE[101] = _auto_range(50,50,5,2,500,10000,RED,10,2)
    #LIGHTNING BOLT!
    SKILLS_TABLE[102] = _auto_range(50,50,5,2,500,10000,BLUE,10,2)
    SKILLS_TABLE[102]["special_path"] = lightning_bolt

#Templates=================================================
def _auto_melee(width, height, arc, radius, cooldown, duration, color, dmg, energy):
    return {'type': MELEE,
            'start': (lambda sid,p,u,d : classes.MeleeParticle(sid,p)),
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
           
def _auto_range(width, height, speed, acceleration, cooldown, duration, color, dmg, energy):
    return {'type': RANGE,
            'start': (lambda sid,p,u,d : classes.RangeParticle(sid,p,u,d)),
            'width': width,
            'height': height,
            'speed' : speed,
            'acceleration': acceleration,
            'cooldown': cooldown,
            'duration': duration,
            'color': color,
            'dmg': dmg,
            'energy': energy
           }
           
#Individual skills =========================================   

#Used for meditation
def blank_function(sid,player,up = False, down = False):
    return None
    
def teleport_function(sid,player, up = False, down = False):
    if player.energy >= SKILLS_TABLE[sid]['energy']:
        if player.facing_direction == RIGHT:
            player.left += 100
        else:
            player.left -= 100
    return None

#Example of a special function
#Takes in two parameters: the particle object, and time  
#Returns new x and y  
def lightning_bolt(particle,time):
    x = particle.centerx
    if particle.direction == RIGHT:
        x += 5
    else:
        x -= 5
    y = particle.originy + 50*math.cos(x/10)
    return x,y