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

#NOTE:: These attributes are MANDATORY
#   Cooldown: How long it locks your character
#   Duration: How long the particle lives
#   Energy: How much energy it costs; put 0 if no cost

#More information:
#   Do not worry about subtracting energy costs,
#   player input function will handle that.

#   RangeParticles can have two paths. The default
#   which just uses velocity and acceleration
#   It also pays attention to 'up' and 'down',
#   whether player pressed up or down.
#   Melee particles do not care about up or down.

#   "on_hit_f(target)": Is the additional effects it will do on the
#   player instantly. All particle hits already deal damage
#   and place debuffs without 'on_hit_f'. Should be used for
#   instantaneous effects such as knock-back. Keep as 'None'
#   if not used.

def initialize_skill_table():
    #Meditate
    SKILLS_TABLE[-1] = {'type': None, 'start':blank_function, 'cooldown':3000, 'energy': 0}
    #Slap (Default auto attack)
    SKILLS_TABLE[1] = _auto_melee(30,30,math.pi/2, 35, 500,500,YELLOW,10,0)
    #Teleport
    SKILLS_TABLE[100] = {'type': None,'start':teleport_start,'cooldown':500,'energy': 5}
    #FIREBALL!
    SKILLS_TABLE[101] = _auto_range(50,50,5,2,500,10000,RED,10,2)
    #LIGHTNING BOLT!
    SKILLS_TABLE[102] = _auto_range(50,50,5,2,500,10000,BLUE,10,2)
    SKILLS_TABLE[102]["special_path"] = lightning_bolt_start

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
            'start': (lambda sid,player,up,down : classes.RangeParticle(sid,player,up,down)),
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

#'start' function for teleport    
def teleport_start(sid,player, up, down):
    if up and not down:
        player.top -= 100
    elif down and not up:
        player.bottom += 100
    if player.facing_direction == RIGHT:
        player.left += 100
    else:
        player.left -= 100
    out_of_arena_fix(player)
    return None

#Example of a special function
#Takes in two parameters: the particle object, and time  
#Returns new x and y  
def lightning_bolt_start(particle,time):
    x = particle.centerx
    if particle.direction == RIGHT:
        x += 10
    else:
        x -= 10
    y = particle.originy + 10*math.cos(x/10)
    return x,y