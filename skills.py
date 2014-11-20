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

#IMPORTANT:: These attributes are MANDATORY
#   Cooldown: How long it locks your character
#   Duration: How long the particle lives
#   Energy: How much energy it costs; put 0 if no cost

#ADDING DEBUFFS TO PARTICLES (ex: slow on hit):
#   Example: DiseaseBall, id = 999
#       Create the base:
#           SKILLS_TABLE[999] = _auto_range(50,50,5,2,500,10000, YELLOW, 10, 2)
#       Add the debuffs:
#           SKILLS_TABLE[999]['conditions'] = [Stun(5000), Slow(5000,0.5), etc]

#CONDITIONS (Buff and DEBUFF):
#ALL DURATION IS IN MILLISECONDS.
#   Stun(duration)
#       Disables ALL inputs. They may still trickle move and gravity affects stunned.
#   Slow(duration, magnitude)
#       Reduces movement by magnitude; doesn't affect gravity.
#       Magnitude should be decimal between 0 and 1.
#   Snare(duration)
#       Freezes target in place; affects gravity
#   Dot(magnitude, ticks, frequency)
#       Deals <magnitude> damage every <frequency> for <ticks> times
#       Magnitude should be the flat dmg applied every tick.
#       Tick should be an integer.
#       Frequency should be milliseconds, factor of 250. (Ex: 1000, 500, etc.)
#   Silence(duration)
#       Doesn't affect Monsters. Prevents all attacks/skill inputs.
#   Wounded(duration)
#       Doesn't affect Monsters. Reduces Health regen by half.
#   Weakened(duration)
#       Doesn't affect Monsters. Reduces Energy regen by half.
#   Speed(duration, magnitude)
#       Increases movement by magnitude; doesn't affect gravity.
#   Shield(duration,magnitude)
#       Places a protective shield that takes damage instead of hit_points
#   Invigorate(duration)
#       Doesn't affect Monsters. Increases Health regen to 2x.
#   Empowered(duration)
#       Doesn't affect Monsters. Increases Energy regen to 2x.

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
    #Peashooter
    SKILLS_TABLE[2] = _auto_range(10,10,20,0,500,5000,GREEN,10,0)
    #Teleport
    SKILLS_TABLE[100] = {'type': None,'start':teleport_start,'cooldown':500,'energy': 5}
    #FIREBALL!
    SKILLS_TABLE[101] = _auto_range(50,50,5,2,500,10000,RED,10,2)
    #LIGHTNING BOLT!
    SKILLS_TABLE[102] = _auto_range(50,50,5,2,500,10000,BLUE,10,2)
    SKILLS_TABLE[102]["special_path"] = lightning_bolt_start
    #Big-Hammer
    SKILLS_TABLE[1000] = _auto_melee(75,75, math.pi/2, 125, 500,500,DGREY, 20, 5)
    SKILLS_TABLE[1000]['on_hit_f'] = knock_back
    SKILLS_TABLE[1000]['start'] = big_hammer
    SKILLS_TABLE["bighammer0"] = _auto_melee(30,30,math.pi/2,30,500,500,BROWN, 10, 0)
    SKILLS_TABLE["bighammer1"] = _auto_melee(30,30,math.pi/2,60,500,500,BROWN, 10, 0)

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
    
def big_hammer(sid, player, up = False, down = False):
    return [classes.MeleeParticle("bighammer0",player),
            classes.MeleeParticle("bighammer1",player),
            classes.MeleeParticle(sid,player)]
    
def knock_back(target):
    if target.dx >= 0:
        target.x -= 50
    else:
        target.x += 50
    out_of_arena_fix(target)