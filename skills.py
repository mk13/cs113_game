import math
import random
import pygame
from pygame.locals import *

from globals import *
import classes

SKILLS_TABLE = {}

# Skill ID guide:
#     -1 : meditate
#      0 : empty
#   1-99 : for auto attacks
# 100-999: for skills
# 1000+  : for ultimate

# IMPORTANT:: These attributes are MANDATORY
#   Name: Used later for scrolling texts
#   Cooldown: How long it locks your character
#   Duration: How long the particle lives
#   Energy: How much energy it costs; put 0 if no cost

# ADDING DEBUFFS TO PARTICLES (ex: slow on hit):
#   Example: DiseaseBall, id = 999
#       Create the base:
#           SKILLS_TABLE[999] = _auto_range(50,50,5,2,500,10000, YELLOW, 10, 2)
#       Add the debuffs:
#           SKILLS_TABLE[999]['conditions'] = [classes.Stun(5000), classes.Slow(5000,0.5), etc]

# CONDITIONS (Buff and DEBUFF):
# ALL DURATION IS IN MILLISECONDS.
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

# More information:
#   Do not worry about subtracting energy costs,
#   player input function will handle that.

#   RangeParticles can have two paths. The default
#   which just uses velocity and acceleration
#   It also pays attention to 'up' and 'down',
#   whether player pressed up or down.
#   Melee particles do not care about up or down.

#   "on_hit_f(current_particle, target, time)": Is the additional effects it will do on the
#   player instantly. All particle hits already deal damage
#   and place debuffs without 'on_hit_f'. Should be used for
#   instantaneous effects such as knock-back. Keep as 'None'
#   if not used.

#   "on_expire_f(current_particle)" : Additional effects it will do when the particle expires

#   "on_terrain_f(current_particle)" : Additional effects it will do when the particle hits wall

def initialize_skill_table():
    # -----------------------------------------------------------------------------------------
    # AUTO ATTACKS 1-99
    # -----------------------------------------------------------------------------------------

    # Monster Slayer (Default auto attack)
    SKILLS_TABLE[1] = _auto_melee('Monster Slayer',30, 30, math.pi / 2, 40, 40, 500, 500, YELLOW, 0, 0)
    SKILLS_TABLE[1]['on_hit_f'] = monster_slayer_on_hit
    # Peashooter
    SKILLS_TABLE[2] = _auto_range('Peashooter', 10, 10, 20, 0, 500, 5000, GREEN, 5, 0)
    # Spear
    SKILLS_TABLE[3] = _auto_melee('Spear', 10, 10, 0, 5, 60, 500, 500, DGREY, 15, 0, True)
    # Nail-on-plank
    SKILLS_TABLE[4] = _auto_melee('Nail-on-Plank', 20, 20, math.pi/2, 30, 30, 20, 500, BROWN, 2, 0)
    # -----------------------------------------------------------------------------------------
    # SKILLS 100-999
    # -----------------------------------------------------------------------------------------

    # Teleport
    SKILLS_TABLE[100] = {'name':'Teleport','type': None, 'start': teleport_start, 'cooldown': 200, 'energy': 5}
    # Fireball
    SKILLS_TABLE[101] = _auto_range('Fireball',50, 50, 5, 2, 500, 10000, RED, 10, 2)
    # Static Bolt
    SKILLS_TABLE[102] = _auto_range('Static Bolt',50, 50, 5, 2, 500, 10000, BLUE, 10, 2)
    SKILLS_TABLE[102]["special_path"] = lightning_bolt_path
    # Boulder Toss
    ADD_BOULDER_TOSS(103)
    # Mines
    SKILLS_TABLE[104] = _auto_range('Mines',40, 40, 0, 0, 500, 10000, DKGREEN, 25, 3)
    # Shrapnel Bomb
    ADD_SHRAPNEL_BOMB(105)
    # Shield
    ADD_SHIELD(106)
    # Flailing Flail
    SKILLS_TABLE[107] = _auto_melee('Flailing Flail',20, 20, math.pi*10, 35, 35, 200, 5000, RED, 3, 5)
    # Napalm
    ADD_NAPALM(108)
    # Fire and Ice
    ADD_FIRE_AND_ICE(109)
    # Machine Gun
    SKILLS_TABLE[110] = _auto_range('Machine Gun',10, 10, 7, 0.2, 20, 2000, BLACK, 2, 0)
    # Vile Breath
    ADD_VILE_BREATH(111)
    # Ice Bolt
    SKILLS_TABLE[112] = _auto_range('Ice Bolt',25, 25, 10, 0, 500, 5000, BLUE, 3, 4)
    SKILLS_TABLE[112]['conditions'] = [classes.Snare(2500)]
    # Shatter
    SKILLS_TABLE[113] = _auto_range('Shatter',25, 25, 15, 0, 250, 5000, LBLUE, 10, 3)
    SKILLS_TABLE[113]['on_hit_f'] = shatter_on_hit
    # Cropdust
    ADD_CROP_DUST(114)
    # Redirect Monster
    SKILLS_TABLE[115] = _auto_range('Redirect Monster', 25, 25, 15, 0, 250, 5000, GREEN, 5, 3)
    SKILLS_TABLE[115]['on_hit_f'] = redirect_on_hit
    # Personal Faerie
    ADD_SKILL_PERSONAL_FAERIE(116)
    # Junk Wall
    SKILLS_TABLE[117] = {'name':'Junk Wall','type': None, 'start': wall_start, 'cooldown': 200, 'energy': 5}
    # -----------------------------------------------------------------------------------------
    # ULTIMATES 1000+
    # -----------------------------------------------------------------------------------------

    # Big-Hammer
    ADD_BIG_HAMMER(1000)
    # Silver Bullet
    SKILLS_TABLE[1001] = _auto_range('Silver Bullet', 10, 10, 20, 1, 1500, 5000, WHITE, 10, 5)
    SKILLS_TABLE[1001]['on_hit_f'] = silver_bullet_on_hit
    # Electric Field
    ADD_ELECTRIC_FIELD(1002)
    # Polarity Shift
    ADD_POLARITY_SHIFT(1003)
    # Bee Hive
    ADD_BEE_HIVE(1004)
    # Epicenter
    ADD_EPICENTER(1005)
    # for k, v in sorted(SKILLS_TABLE.items(), key=lambda x: str(x)):
    #     print(k, v)

# Templates=================================================
def _auto_melee(name, width, height, arc, start_radius, max_radius, cooldown, duration, color, dmg, energy, extend = False):
    return {'name': name, 'type': MELEE, 'start': (lambda sid, p, u, d: classes.MeleeParticle(sid, p)),
            'width': width, 'height': height, 'arc': arc, 'start_radius': start_radius, 'max_radius':max_radius, 'cooldown': cooldown,
            'duration': duration, 'color': color, 'dmg': dmg, 'energy': energy, 'extend':extend}


def _auto_range(name, width, height, speed, acceleration, cooldown, duration, color, dmg, energy):
    return {'name': name, 'type': RANGE,
            'start': (lambda sid, player, up, down: classes.RangeParticle(sid, player, up, down)),
            'width': width, 'height': height, 'speed': speed, 'acceleration': acceleration,
            'cooldown': cooldown, 'duration': duration, 'color': color, 'dmg': dmg,
            'energy': energy}

def _auto_field(name, radius, cooldown, duration, color, dmg, energy):
    return {'name': name, 'type': FIELD,
            'start':(lambda sid, player: classes.FieldParticle(sid,player)),
            'radius':radius, 'width':radius*2, 'height':radius*2, 'cooldown':cooldown, 'duration':duration,
            'color':color, 'dmg':dmg, 'energy':energy}

# Individual skills =========================================

def monster_slayer_on_hit(particle, target, time):
    if isinstance(target, classes.Monster):
        handle_damage(target, 20, time)
    else:
        handle_damage(target, 2, time)

# 'start' function for teleport
def teleport_start(sid, player, up, down):
    if up and not down:
        player.top -= 100
    elif down and not up:
        player.top += 100
    if player.facing_direction == RIGHT:
        player.left += 100
    else:
        player.left -= 100
    out_of_arena_fix(player)
    return None

def shield_start(sid, player, up, down):
    sh = classes.Shield(10000, 10)
    return None

# Example of a special function
# Takes in two parameters: the particle object, and time
# Returns new x and y
def lightning_bolt_path(particle, time):
    x = particle.centerx
    if particle.direction == RIGHT:
        x += 10
    else:
        x -= 10
    y = particle.originy + 10 * math.cos(x / 10)
    return x, y

def lob_motion(particle, time):
    x = particle.centerx + particle.dx
    particle.dy += particle.ddy
    y = particle.centery + particle.dy
    return x,y

def ADD_BIG_HAMMER(i):
    SKILLS_TABLE[i] = _auto_melee("Big Hammer",75, 75, math.pi / 2, 125, 125, 500, 500, DGREY, 20, 5)
    SKILLS_TABLE[i]['on_hit_f'] = knock_back
    SKILLS_TABLE[i]['conditions'] = [classes.Stun(3000)]
    SKILLS_TABLE[i]['start'] = big_hammer
    SKILLS_TABLE["bighammer0"] = _auto_melee('',30, 30, math.pi / 2, 30, 30, 500, 500, BROWN, 10, 0)
    SKILLS_TABLE["bighammer1"] = _auto_melee('',30, 30, math.pi / 2, 60, 60, 500, 500, BROWN, 10, 0)
def big_hammer(sid, player, up=False, down=False):
    return [classes.MeleeParticle("bighammer0", player),
            classes.MeleeParticle("bighammer1", player), classes.MeleeParticle(sid, player)]
def knock_back(particle,target,time):
    if target.dx >= 0:
        target.x -= 50
    else:
        target.x += 50
    out_of_arena_fix(target)

def ADD_BOULDER_TOSS(i):
    SKILLS_TABLE[i] = {'name': "Boulder Toss", 'type': None, 'start':boulder_toss_start, 'cooldown':200, 'energy': 6}
    SKILLS_TABLE["boulder_toss"] = _auto_range('',30, 30, 5, 0, 500, 3000, BLACK, 2, 0)
    SKILLS_TABLE["boulder_toss"]["conditions"] = [classes.Stun(2000)]
    SKILLS_TABLE["boulder_toss"]["special_path"] = lob_motion
def boulder_toss_start(sid, player, up=False, down=False):
    obj = classes.RangeParticle("boulder_toss", player, up, down)
    obj.dy = -15
    if player.facing_direction == RIGHT:
        obj.dx = 15
    else:
        obj.dx = -15
    obj.ddy = 1
    return obj

def ADD_SHRAPNEL_BOMB(i):
    SKILLS_TABLE[i] = {'name': 'Shrapnel Bomb', 'type': None, 'start': shrapnel_bomb_start, 'cooldown': 200, 'energy':2}
    SKILLS_TABLE["shrapnel_base"] = _auto_range('',25, 25, 5, 0, 200, 3000, DGREY, 10, 0)
    SKILLS_TABLE["shrapnel_base"]["special_path"] = lob_motion
    SKILLS_TABLE["shrapnel_base"]["on_hit_f"] = shrapnel_on_hit
    SKILLS_TABLE["shrapnel_base"]["on_expire_f"] = shrapnel_on_expire
    SKILLS_TABLE["shrapnel_base"]["on_terrain_f"] = shrapnel_on_terrain
    SKILLS_TABLE["shrapnel_trigger"] = {'name':'','type': None, 'start':shrapnel_trigger_start, 'cooldown':100, 'energy':0}
    SKILLS_TABLE["shrapnel0"] = _auto_range('',10, 10, 2, 0, 500, 1000, DGREY, 5, 0)
    SKILLS_TABLE["shrapnel0"]["special_path"] = (lambda p,t: (p.centerx+10, p.centery))
    SKILLS_TABLE["shrapnel1"] = _auto_range('',10, 10, 2, 0, 500, 1000, DGREY, 5, 0)
    SKILLS_TABLE["shrapnel1"]["special_path"] = (lambda p,t: (p.centerx-10, p.centery))
    SKILLS_TABLE["shrapnel2"] = _auto_range('',10, 10, 2, 0, 500, 1000, DGREY, 5, 0)
    SKILLS_TABLE["shrapnel2"]["special_path"] = (lambda p,t: (p.centerx, p.centery+10))
    SKILLS_TABLE["shrapnel3"] = _auto_range('',10, 10, 2, 0, 500, 1000, DGREY, 5, 0)
    SKILLS_TABLE["shrapnel3"]["special_path"] = (lambda p,t: (p.centerx, p.centery-10))
    SKILLS_TABLE["shrapnel4"] = _auto_range('',10, 10, 2, 0, 500, 1000, DGREY, 5, 0)
    SKILLS_TABLE["shrapnel5"] = _auto_range('',10, 10, 2, 0, 500, 1000, DGREY, 5, 0)
    SKILLS_TABLE["shrapnel6"] = _auto_range('',10, 10, 2, 0, 500, 1000, DGREY, 5, 0)
    SKILLS_TABLE["shrapnel7"] = _auto_range('',10, 10, 2, 0, 500, 1000, DGREY, 5, 0)
    SKILLS_TABLE["shrapnel4"]["special_path"] = (lambda p,t: (p.centerx+10, p.centery+10))
    SKILLS_TABLE["shrapnel5"]["special_path"] = (lambda p,t: (p.centerx+10, p.centery-10))
    SKILLS_TABLE["shrapnel6"]["special_path"] = (lambda p,t: (p.centerx-10, p.centery+10))
    SKILLS_TABLE["shrapnel7"]["special_path"] = (lambda p,t: (p.centerx-10, p.centery-10))
def shrapnel_bomb_start(sid, player, up=False, down=False):
    if player.skill1_id == 105:
        player.skill1_id = "shrapnel_trigger"
    elif player.skill2_id == 105:
        player.skill2_id = "shrapnel_trigger"
    elif player.skill3_id == 105:
        player.skill3_id = "shrapnel_trigger"
    obj = classes.RangeParticle("shrapnel_base", player, up, down)
    obj.dy = -15
    if player.facing_direction == RIGHT:
        obj.dx = 10
    else:
        obj.dx = -10
    obj.ddy = 1
    player.temp_shrapnel = obj
    return obj
def shrapnel_trigger_start(sid, player, up=False, down=False):
    if player.skill1_id == 'shrapnel_trigger':
        player.skill1_id = 105
    elif player.skill2_id == 'shrapnel_trigger':
        player.skill2_id = 105
    elif player.skill3_id == 'shrapnel_trigger':
        player.skill3_id = 105

    obj = player.__dict__['temp_shrapnel']
    del player.__dict__['temp_shrapnel']
    if not obj.expired:
        x = obj.centerx
        y = obj.centery
        obj.expired = True

        p0 = classes.RangeParticle("shrapnel0", player, up, down)
        p1 = classes.RangeParticle("shrapnel1", player, up, down)
        p2 = classes.RangeParticle("shrapnel2", player, up, down)
        p3 = classes.RangeParticle("shrapnel3", player, up, down)
        p4 = classes.RangeParticle("shrapnel4", player, up, down)
        p5 = classes.RangeParticle("shrapnel5", player, up, down)
        p6 = classes.RangeParticle("shrapnel6", player, up, down)
        p7 = classes.RangeParticle("shrapnel7", player, up, down)

        p0.centerx = p1.centerx = p2.centerx = p3.centerx = p4.centerx = p5.centerx = p6.centerx = p7.centerx = x
        p0.centery = p1.centery = p2.centery = p3.centery = p4.centery = p5.centery = p6.centery = p7.centery = y

        return [p0,p1,p2,p3,p4,p5,p6,p7]
    else:
        return None
def shrapnel_on_hit(particle,target,time):
    p = particle.belongs_to
    if p.skill1_id == "shrapnel_trigger":
        p.skill1_id = 105
    elif p.skill2_id == "shrapnel_trigger":
        p.skill2_id = 105
    elif p.skill3_id == "shrapnel_trigger":
        p.skill3_id = 105
    if 'temp_shrapnel' in p.__dict__.keys():
        del p.__dict__['temp_shrapnel']
def shrapnel_on_expire(particle):
    p = particle.belongs_to
    if p.skill1_id == "shrapnel_trigger":
        p.skill1_id = 105
    elif p.skill2_id == "shrapnel_trigger":
        p.skill2_id = 105
    elif p.skill3_id == "shrapnel_trigger":
        p.skill3_id = 105
    if 'temp_shrapnel' in p.__dict__.keys():
        del p.__dict__['temp_shrapnel']
def shrapnel_on_terrain(particle):
    p = particle.belongs_to
    if p.skill1_id == "shrapnel_trigger":
        p.skill1_id = 105
    elif p.skill2_id == "shrapnel_trigger":
        p.skill2_id = 105
    elif p.skill3_id == "shrapnel_trigger":
        p.skill3_id = 105
    if 'temp_shrapnel' in p.__dict__.keys():
        del p.__dict__['temp_shrapnel']


def ADD_SHIELD(i):
    SKILLS_TABLE[i] = {'name':'Shield','type': None, 'start': shield_start, 'cooldown': 200, 'energy':6}
def shield_start(sid, player, up=False, down=False):
    sh = classes.Shield(10000,10)
    sh.begin(-1,player)
    return None
def ADD_NAPALM(i):
    SKILLS_TABLE[i] = {'name': 'Napalm', 'type': None, 'start': napalm_start, 'cooldown': 500, 'energy':5}
    SKILLS_TABLE['napalm_main'] = _auto_range('',30, 30, 2, 0, 500, 500, RED, 10, 0)
    SKILLS_TABLE['napalm0'] = _auto_range('',20, 20, 2, 0, 500, 3000, RED, 10, 0)
    SKILLS_TABLE['napalm1'] = _auto_range('',20, 20, 2, 0, 500, 3000, RED, 10, 0)
    SKILLS_TABLE['napalm2'] = _auto_range('',20, 20, 2, 0, 500, 3000, RED, 10, 0)
    SKILLS_TABLE['napalm_main']['special_path'] = lob_motion
    SKILLS_TABLE['napalm_main']['conditions'] = [classes.Dot(3, 5, 1000)]
    SKILLS_TABLE['napalm_main']['on_expire_f'] = napalm_on_expire
    SKILLS_TABLE['napalm0']['special_path'] = lob_motion
    SKILLS_TABLE['napalm1']['special_path'] = lob_motion
    SKILLS_TABLE['napalm0']['special_path'] = lob_motion
    SKILLS_TABLE['napalm1']['special_path'] = lob_motion

def napalm_start(sid,player,up=False,down=False):
    obj = classes.RangeParticle("napalm_main", player, up, down)
    obj.dy = -15
    if player.facing_direction == RIGHT:
        obj.dx = 10
    else:
        obj.dx = -10
    obj.ddy = 1
    return obj
def napalm_on_expire(p):
    sx = p.centerx
    sy = p.centery
    obj0 = classes.RangeParticle("napalm0",p.belongs_to,False,False)
    obj1 = classes.RangeParticle("napalm0",p.belongs_to,False,False)
    obj2 = classes.RangeParticle("napalm0",p.belongs_to,False,False)
    obj0.centerx = obj1.centerx = obj2.centerx = sx
    obj0.centery = obj1.centery = obj2.centery = sy
    obj0.dy = -15
    obj1.dy = -10
    obj2.dy = -5
    if p.dx > 0:
        obj0.dx = 4
        obj1.dx = 8
        obj2.dx = 12
    else:
        obj0.dx = -4
        obj1.dx = -8
        obj2.dx = -12
    obj0.ddy = obj1.ddy = obj2.ddy = 1
    if p.belongs_to.new_particle == None:
        p.belongs_to.new_particle = [obj0, obj1, obj2]
    elif isinstance(p.belongs_to.new_particle,list):
        p.belongs_to.new_particle.append(obj0)
        p.belongs_to.new_particle.append(obj1)
        p.belongs_to.new_particle.append(obj2)
    else:
        temp = p.belongs_to.new_particle
        p.belongs_to.new_particle = [temp, obj0, obj1, obj2]

def ADD_FIRE_AND_ICE(i):
    SKILLS_TABLE[i] = {'name':'Icy-Hot', 'type': None, 'start': fai_start, 'cooldown': 200, 'energy':5}
    SKILLS_TABLE['fai_fire'] = _auto_range('',20, 20, 5, 2, 500, 10000, RED, 10, 2)
    SKILLS_TABLE['fai_fire']['special_path'] = fai_fire_path
    SKILLS_TABLE['fai_fire']['conditions'] = [classes.Dot(5, 3, 1000)]
    SKILLS_TABLE['fai_ice']  = _auto_range('',20, 20, 5, 2, 500, 10000, LBLUE, 10, 2)
    SKILLS_TABLE['fai_ice']['special_path'] = fai_ice_path
    SKILLS_TABLE['fai_ice']['conditions'] = [classes.Snare(2500)]
def fai_start(sid,player,up=False,down=False):
    ice = classes.RangeParticle('fai_ice', player, up, down)
    fire = classes.RangeParticle('fai_fire', player, up, down)
    return [ice, fire]
def fai_fire_path(particle, time):
    x = particle.centerx
    if particle.direction == RIGHT:
        x += 10
    else:
        x -= 10
    y = particle.originy + 20 * math.cos(x / 50)
    return x, y
def fai_ice_path(particle, time):
    x = particle.centerx
    if particle.direction == RIGHT:
        x += 10
    else:
        x -= 10
    y = particle.originy + 20 * math.sin(x / 50)
    return x, y


def ADD_VILE_BREATH(i):
    SKILLS_TABLE[i] = {'name':'Vile Breath','type': None, 'start': vile_breath_start, 'cooldown':20, 'energy': 1}
    SKILLS_TABLE['vbreath'] = _auto_range('',10,10,5,0,500,1000,GREEN,2,1)
    SKILLS_TABLE['vbreath']['special_path'] = vile_breath_path
    SKILLS_TABLE['vbreath']['conditions'] = [classes.Weakened(random.randint(1,3)*1000),
                                             classes.Slow(random.randint(1,3)*1000, 0.5)]
def vile_breath_start(sid,player,up=False, down=False):
    b0 = classes.RangeParticle('vbreath',player,up,down)
    b1 = classes.RangeParticle('vbreath',player,up,down)
    b2 = classes.RangeParticle('vbreath',player,up,down)
    b0.centery = b0.belongs_to.top
    b1.centery = b1.belongs_to.top
    b2.centery = b2.belongs_to.top
    return [b0,b1,b2]
def vile_breath_path(particle, time):
    x = particle.centerx
    if particle.direction == RIGHT:
        x += 5 + random.randint(0,5)
    else:
        x -= 5 + random.randint(0,5)
    y = particle.centery + random.randint(-5,5)
    return x,y

def shatter_on_hit(particle,target,time):
    if target.conditions[SNARE]:
        handle_damage(target, 10, time+500)

def ADD_CROP_DUST(i):
    SKILLS_TABLE[i] = {'name':'Crop Dust', 'type': None, 'start': crop_dust_start, 'cooldown': 1, 'energy': 1}
    SKILLS_TABLE['cropdust'] = _auto_range('',10,10,5,0,500,1000,BROWN,1,1)
    SKILLS_TABLE['cropdust']['special_path'] = crop_dust_path
    SKILLS_TABLE['cropdust']['conditions'] = [classes.Slow(1500, 0.50)]
def crop_dust_start(sid,player,up=False,down=False):
    c0 = classes.RangeParticle('cropdust',player,up,down)
    c1 = classes.RangeParticle('cropdust',player,up,down)
    c2 = classes.RangeParticle('cropdust',player,up,down)
    c0.centery = c0.belongs_to.bottom-5
    c1.centery = c1.belongs_to.bottom-5
    c2.centery = c2.belongs_to.bottom-5
    return [c0,c1,c2]
def crop_dust_path(particle,time):
    x = particle.centerx
    if particle.direction == RIGHT:
        x -= 5 + random.randint(0,5)
    else:
        x += 5 + random.randint(0,5)
    y = particle.centery + random.randint(-5,5)
    return x,y

def silver_bullet_on_hit(particle,target,time):
    diff = target.hit_points_max - target.hit_points
    diff = int(diff/4)
    handle_damage(target,diff,time+500)

def redirect_on_hit(particle, target, time):
    if isinstance(target, classes.Monster):
        if target.status == IDLE:
            target.last_status_change = -10000 #Force hard reset
        target.target = particle.belongs_to.opposite

def ADD_ELECTRIC_FIELD(i):
    SKILLS_TABLE[i] = {'name':'Electric Field', 'type':None, 'start':electric_field_start, 'cooldown': 200, 'energy':4}
    SKILLS_TABLE['ef0'] = _auto_melee('', 20, 20, math.pi*3, 100, 100, 100, 5000, BLUE, 10, 1)
    SKILLS_TABLE['ef1'] = _auto_melee('', 10, 10, math.pi*4, 50, 50, 100, 5000, BLUE, 10, 1)
    SKILLS_TABLE['ef2'] = _auto_melee('', 5, 5, math.pi*5, 25, 25, 100, 5000, BLUE, 10, 1)
def electric_field_start(sid,player,up=False,down=False):
    ef0 = classes.MeleeParticle('ef0', player)
    ef1 = classes.MeleeParticle('ef1', player)
    ef2 = classes.MeleeParticle('ef2', player)
    return [ef0, ef1, ef2]

def ADD_POLARITY_SHIFT(i):
    SKILLS_TABLE[i] = {'name':'Polarity Shift', 'type':None, 'start':polarity_shift_start, 'cooldown': 200, 'energy':7}
def polarity_shift_start(sid, player,up=False, down =False):
    tar = player.opposite
    d = player.distance_from(tar)
    if d <= 500:
        if tar.facing_direction == RIGHT:
            tar.dx -= 100
        else:
            tar.dx += 100
        c = classes.Stun(2000)
        c.begin(-1, tar)
    return None


def ADD_BEE_HIVE(i):
    SKILLS_TABLE[i] = {'name':'Bee Hive', 'type': None, 'start':bee_hive_start, 'cooldown':300, 'energy':8}
    SKILLS_TABLE['beehive'] = _auto_range('',40,40, 3, 0, 500, 5000, WHITE, 4, 0)
    SKILLS_TABLE['beehive']['special_path'] = bee_hive_path
    SKILLS_TABLE['beehive']['conditions'] = [classes.Dot(3,5,1000)]
    SKILLS_TABLE['bee1'] = _auto_range('', 10, 10, 5, 0, 100, 500, YELLOW, 2, 0)
    SKILLS_TABLE['bee2'] = _auto_range('', 10, 10, 5, 0, 100, 500, YELLOW, 2, 0)
    SKILLS_TABLE['bee3'] = _auto_range('', 10, 10, 5, 0, 100, 500, YELLOW, 2, 0)
    SKILLS_TABLE['bee4'] = _auto_range('', 10, 10, 5, 0, 100, 500, YELLOW, 2, 0)
    SKILLS_TABLE['bee5'] = _auto_range('', 10, 10, 5, 0, 100, 500, YELLOW, 2, 0)
    SKILLS_TABLE['bee6'] = _auto_range('', 10, 10, 5, 0, 100, 500, YELLOW, 2, 0)
    SKILLS_TABLE['bee7'] = _auto_range('', 10, 10, 5, 0, 100, 500, YELLOW, 2, 0)
    SKILLS_TABLE['bee8'] = _auto_range('', 10, 10, 5, 0, 100, 500, YELLOW, 2, 0)

    SKILLS_TABLE["bee1"]["special_path"] = (lambda p,t: (p.centerx-10, p.centery-10))
    SKILLS_TABLE["bee2"]["special_path"] = (lambda p,t: (p.centerx, p.centery-10))
    SKILLS_TABLE["bee3"]["special_path"] = (lambda p,t: (p.centerx+10, p.centery-10))
    SKILLS_TABLE["bee4"]["special_path"] = (lambda p,t: (p.centerx+10, p.centery))
    SKILLS_TABLE["bee5"]["special_path"] = (lambda p,t: (p.centerx+10, p.centery+10))
    SKILLS_TABLE["bee6"]["special_path"] = (lambda p,t: (p.centerx, p.centery+10))
    SKILLS_TABLE["bee7"]["special_path"] = (lambda p,t: (p.centerx-10, p.centery+10))
    SKILLS_TABLE["bee8"]["special_path"] = (lambda p,t: (p.centerx-10, p.centery))
def bee_hive_start(sid, player, up=False, down=False):
    obj = classes.RangeParticle('beehive', player, up, down)
    obj.dx = 4 if player.facing_direction == RIGHT else -4
    obj.beeUpdate = -1
    return obj
def bee_hive_path(particle,time):
    if particle.beeUpdate == -1:
        particle.beeUpdate = time

    if time - particle.beeUpdate >= 250:
        particle.beeUpdate = time
        li = [classes.RangeParticle("bee1",particle.belongs_to,False,False),
              classes.RangeParticle("bee2",particle.belongs_to,False,False),
              classes.RangeParticle("bee3",particle.belongs_to,False,False),
              classes.RangeParticle("bee4",particle.belongs_to,False,False),
              classes.RangeParticle("bee5",particle.belongs_to,False,False),
              classes.RangeParticle("bee6",particle.belongs_to,False,False),
              classes.RangeParticle("bee7",particle.belongs_to,False,False),
              classes.RangeParticle("bee8",particle.belongs_to,False,False)]
        for i in range(0,8):
            li[i].centerx = particle.centerx
            li[i].centery = particle.centery

        if particle.belongs_to.new_particle == None:
            particle.belongs_to.new_particle = li
        elif isinstance(particle.belongs_to.new_particle,list):
            particle.belongs_to.new_particle += li
        else:
            temp = p.belongs_to.new_particle
            particle.belongs_to.new_particle = [temp] + li

    return particle.centerx + particle.dx, particle.centery

def ADD_SKILL_PERSONAL_FAERIE(i):
    SKILLS_TABLE[i] = {'name':'Personal Faerie', 'type': None, 'start':personal_faerie_start, 'cooldown':300, 'energy':5}
    SKILLS_TABLE['personal_faerie'] = _auto_melee('', 10, 10, 0, 5, 5, 300, 5000, LBLUE, 0, 6)
    SKILLS_TABLE['personal_faerie']['special_path'] = faerie_path
    SKILLS_TABLE['faerie_shoot'] = _auto_range('', 10, 10, 5, 0.5, 100, 1000, BLUE, 4, 0)
    SKILLS_TABLE['faerie_shoot']['special_path'] = faerie_shot_path
def personal_faerie_start(sid, player, up = False, down = False):
    obj = classes.MeleeParticle('personal_faerie',player)
    obj.timer = -1
    obj.centery = player.centery - 20
    obj.direction = player.facing_direction
    if player.facing_direction == RIGHT:
        obj.centerx = player.centerx + 15
    else:
        obj.centerx = player.centery - 15
    return obj
def faerie_path(p,t):
    if p.timer == -1:
        p.timer = t

    if t - p.timer >= 500:
        p.timer = t
        shot = classes.RangeParticle('faerie_shoot', p.belongs_to, False, False)
        shot.direction = p.direction
        shot.centerx = p.centerx
        shot.centery = p.centery
        shot.dx = 5
        shot.ddx = 0.5
        if shot.direction == LEFT:
            shot.dx *= -1
            shot.ddx *= -1
        force_add_particle_to_player(shot, p.belongs_to)

    y = p.belongs_to.centery - 20
    if p.direction == RIGHT:
        x = p.belongs_to.centerx + 15
    else:
        x = p.belongs_to.centerx - 15
    return x,y
def faerie_shot_path(p,t):
    y = p.centery
    x = p.centerx + p.dx
    p.dx += p.ddx
    return x,y
    
def ADD_EPICENTER(i):
    SKILLS_TABLE[i] = {'name':'Epicenter', 'type': None, 'start':epicenter_start, 'cooldown':300, 'energy':8}
    SKILLS_TABLE['epicenter'] = _auto_field('', radius=200, cooldown=200, duration=6000, color=BROWN, dmg=10, energy=2)
    SKILLS_TABLE['epicenter']['frequency'] = 2000
    SKILLS_TABLE['epicenter']['conditions'] = [classes.Slow(2000, 0.5)]
    SKILLS_TABLE['epicenter']['on_hit_f'] = epicenter_on_hit_f
def epicenter_start(sid, player, up=False, down=False):
    obj = classes.FieldParticle('epicenter', player)
    return obj
def epicenter_on_hit_f(particle, target, time):
    target.dx += (particle.centerx - target.centerx)/5
    target.dy += (particle.centery - target.centery)/5
    
def wall_start(sid, player, up, down):
    x1 = x2 = x3 = player.centerx -15
    y1 = y2 = y3 = player.centery -10
    
    if up and not down:
        y1 -= 50
        y2 -= 50
        y3 -= 50
        x2 -= 40
        x3 += 40
    elif not up and down:
        y1 += 50
        y2 += 50
        y3 += 50
        x2 -= 40
        x3 += 40
    elif up == down:
        x1 += 40 if player.facing_direction==RIGHT else -40
        x2 += 40 if player.facing_direction==RIGHT else -40
        x3 += 40 if player.facing_direction==RIGHT else -40
        y2 += 50
        y3 -= 50
    return [terrain_nt(x1, y1, 30, 30, BLACK, 1, False),
            terrain_nt(x2, y2, 30, 30, BLACK, 1, False),
            terrain_nt(x3, y3, 30, 30, BLACK, 1, False)]

# ----------------------------------------------------------------------------
def get_dropped_skill(monster):
    if monster.kind == WEAK:
        li = auto_attack_skills()
    elif monster.kind == MEDIUM:
        li = regular_skills()
    elif monster.kind == ULTIMATE:
        li = ultimate_skills()
    return random.choice(li)

def get_skill_type(skill_id):
    if 1 <= skill_id <= 99:
        return WEAK
    elif 100 <= skill_id <= 999:
        return MEDIUM
    elif skill_id >= 1000:
        return ULTIMATE

def auto_attack_skills():
    return list(filter(lambda x: type(x) is int and 2 <= x <= 99, SKILLS_TABLE.keys()))

def regular_skills():
    return list(filter(lambda x: type(x) is int and 100 <= x <= 999, SKILLS_TABLE.keys()))

def ultimate_skills():
    return list(filter(lambda x: type(x) is int and x >= 1000, SKILLS_TABLE.keys()))
