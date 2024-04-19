import pygame
import math
import random
from scripts.particle import Particle

GRAVITY = 0.4
TERMINAL_VELOCITY = 12

class PhysicsEntity:
    def __init__(self, game, e_type, pos, size): # pass the entire game into this to give access to the entire game
        self.game = game
        self.type = e_type
        self.pos = list(pos) # ensures position is always a unique class parameter rather than a reference to a list
        self.size = size
        self.velocity = [0, 0]
        self.collisions = {'up': False, 'down': False, 'left': False, 'right': False}
        self.last_movement = [0,0]

        # Animation properties
        self.action = ''
        self.anim_offset = (-3, -3)
        self.flip = False
        self.set_action('idle')

    def rect(self): # this function returns the player rectangle
        return pygame.Rect(self.pos[0],self.pos[1],self.size[0], self.size[1])

    def set_action(self, action):
        if action != self.action: # check if animation action has changed
            self.action = action
            self.animation = self.game.assets[self.type + '/' + self.action].copy() # grab the new animation

    def update(self, tilemap, movement = (0,0)):
        self.collisions = {'up': False, 'down': False, 'left': False, 'right': False}
        # Apply acceleration due to gravity
        self.velocity[1] = min(TERMINAL_VELOCITY, self.velocity[1]+GRAVITY) # include a cap for terminal velocity
        
        # Determine total movement for this frame
        frame_movement = (movement[0] + self.velocity[0], movement[1] + self.velocity[1])

        # Attempt to move the player along the x-axis
        self.pos[0] += frame_movement[0]
        entity_rect = self.rect()
    
        # Check for collisions with tilemap physics objects 
        for rect in tilemap.physics_rects_around(self.pos):
            # resolve collisions in the x-axis
            if entity_rect.colliderect(rect):
                if frame_movement[0] > 0:
                    entity_rect.right = rect.left
                    self.collisions['right'] = True
                if frame_movement[0] < 0:
                    entity_rect.left = rect.right
                    self.collisions['left'] = True
                self.pos[0] = entity_rect.x

        # Attempt to move the player along the y-axis
        self.pos[1] += frame_movement[1]
        entity_rect = self.rect()
        for rect in tilemap.physics_rects_around(self.pos):
            if entity_rect.colliderect(rect):
                if frame_movement[1] > 0:
                    entity_rect.bottom = rect.top
                    self.collisions['down'] = True
                if frame_movement[1] < 0:
                    entity_rect.top = rect.bottom
                    self.collisions['up'] = True
                self.pos[1] = entity_rect.y

        if movement[0] > 0:
            self.flip = False
        if movement[0] < 0: 
            self.flip = True

        self.last_movement = movement # Store the last movement input

        if self.collisions['down'] or self.collisions['up']:
            self.velocity[1] = 0 # set y-velocity = 0 after collision occurs
        if self.collisions['left'] or self.collisions['right']:
            self.velocity[0] = 0 # set x-velocity = 0 after collision occurs

        self.animation.update()
        # print(movement)

    def render(self,surf,offset):
        # print(self.flip)
        surf.blit(pygame.transform.flip(self.animation.img(),self.flip,False),\
                  (self.pos[0]-offset[0]+self.anim_offset[0],self.pos[1]-offset[1]+self.anim_offset[1]))
        # surf.blit(self.game.assets['player'],(self.pos[0]-offset[0],self.pos[1]-offset[1]))

class Player(PhysicsEntity):
    def __init__(self, game, pos, size):
        super().__init__(game, 'player', pos, size)
        self.air_time = 0
        self.jumps = 2
        self.wall_slide = False
        self.dashing = False

    def render(self, surf, offset = (0,0)):
        if abs(self.dashing) <= 50:
            super().render(surf,offset)

    def update(self, tilemap, movement=(0,0)):
        super().update(tilemap, movement=movement)
        

        # control animation states
        self.air_time += 1
        if self.collisions['down']:
            self.air_time = 0
            self.jumps = 2 # reset your double jump when you hit the ground

        self.wall_slide = False
        if (self.collisions['right'] or self.collisions['left']) and self.air_time > 4:
            self.wall_slide = True
            self.velocity[1] = min(self.velocity[1],0.5) # Saturate the downwards velocity when in a wall-slide state
            
            # Show the correct animation based on which side the wall is relative to the player
            if self.collisions['right']:
                self.flip = False
            else:
                self.flip = True
            self.set_action('wall_slide') # set the animation state

        if not self.wall_slide:
            if self.air_time > 1: 
                self.set_action('jump')
            elif movement[0] != 0 and not (self.collisions['left'] or self.collisions['right']):
                self.set_action('run')
            else:
                self.set_action('idle')

        # take away your first jump once you've been in the air for a few frames
        if self.air_time > 4 and self.jumps == 2:
            self.jumps -=1

        # Dashing logic
        # Generate a burst of particles for the dash at self.dashing == 60 and 50 (start/end of dash)
        if abs(self.dashing) in {60,50}:
            for i in range(20): # repeat 20 times
                angle = random.random() * math.pi * 2 # 0 to 2pi
                speed = random.random() * 0.5 + 0.5 # 0.5 to 1
                particle_vel = [math.cos(angle) * speed, math.sin(angle) * speed]
                # Spawn the particle
                self.game.particles.append(Particle(self.game,'particle',self.rect().center,velocity=particle_vel,frame=random.randint(0,7))) 
        
        # Handle Dashing Movement
        if self.dashing > 0:
            self.dashing = max(0,self.dashing - 1)
        elif self.dashing < 0:
            self.dashing = min(0,self.dashing + 1)
        if abs(self.dashing) > 50:
            # for first 10 frames of a dash, do this
            self.velocity[0] = abs(self.dashing) / self.dashing * 10
            if abs(self.dashing) == 51:
                   self.velocity[0] *= 0.1 # take away 90% of dash velocity after 9 frames (let air drag remove the remaining velocity)
            # Generate a stream of particles for the duration of the dash
            particle_vel = [abs(self.dashing)/self.dashing * random.random()*3, 0]
            self.game.particles.append(Particle(self.game,'particle',self.rect().center,velocity=particle_vel,frame=random.randint(0,7))) 



        # The remaining 50 frames are for the dash cooldown! (can't dash until self.dashing == 0)




        # Add air drag to reduce x-velocity from wall jumps
        if self.velocity[0] > 0:
            self.velocity[0] = max(self.velocity[0] - 0.5, 0) # upper bound at 0
        elif self.velocity[0] < 0:
            self.velocity[0] = min(self.velocity[0] + 0.5, 0) # lower bound at 0


    def jump(self):
        if self.wall_slide:
            if self.flip and self.last_movement[0] < 0:
                self.velocity[0] = 6 # push away from the wall
                self.velocity[1] = -6 # jump vertically
                self.air_time = 5
                self.jumps = max(0,self.jumps-1) # lower bound number of jumps at 0
                return True
            elif not self.flip and self.last_movement[0] > 0:
                self.velocity[0] = -6 # push away from the wall
                self.velocity[1] = -6 # jump vertically
                self.air_time = 5
                self.jumps = max(0,self.jumps-1) # lower bound number of jumps at 0
                return True
        # normal jumping
        elif self.jumps: 
            self.velocity[1] = -8
            self.jumps -= 1 # take away one of the player's available jumps
            self.air_time = 5 # this forces the player to enter the jumping animation
            return True
        
        # Returns true when a jump is completed in order to have certain events activate on jumping (if you so desire)

    def dash(self):
        if not self.dashing:
            if self.flip:
                self.dashing = -60
            else:
                self.dashing = 60
