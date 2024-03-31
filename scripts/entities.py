import pygame

GRAVITY = 0.4
TERMINAL_VELOCITY = 8

class PhysicsEntity:
    def __init__(self, game, e_type, pos, size): # pass the entire game into this to give access to the entire game
        self.game = game
        self.type = e_type
        self.pos = list(pos) # ensures position is always a unique class parameter rather than a reference to a list
        self.size = size
        self.velocity = [0, 0]
        self.collisions = {'up': False, 'down': False, 'left': False, 'right': False}
    def rect(self): # this function returns the player rectangle
        return pygame.Rect(self.pos[0],self.pos[1],self.size[0], self.size[1])

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

        if self.collisions['down'] or self.collisions['up']:
            self.velocity[1] = 0 # set y-velocity = 0 after collision occurs
        if self.collisions['left'] or self.collisions['right']:
            self.velocity[0] = 0 # set x-velocity = 0 after collision occurs


    def render(self,surf,offset):
        surf.blit(self.game.assets['player'],(self.pos[0]-offset[0],self.pos[1]-offset[1]))