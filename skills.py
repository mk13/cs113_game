from globals import *
import math
import classes
SKILLS_TABLE = {}

def initialize_skill_table():
    SKILLS_TABLE[1] = _auto_melee(30,30,math.pi/2, 35, 500,500,YELLOW,10,0)



def _auto_melee(width, height, arc, radius, cooldown, duration, color, dmg, energy):
    return {'type': MELEE,
            'start': (lambda p,sid : classes.MeleeParticle(p,sid)),
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
    