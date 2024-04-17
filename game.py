import sys
import random
import pygame
from scripts.entities import PhysicsEntity, Player
from scripts.utils import load_image, load_images
from scripts.tilemap import Tilemap
from scripts.clouds import Cloud, Clouds
from scripts.utils import Animation
from scripts.particle import Particle
import math

class Game:
    def __init__(self):

        pygame.init()

        
        pygame.display.set_caption('ninja game')
        self.screen = pygame.display.set_mode((640,480)) # This is what is shown on the computer screen

        self.display = pygame.Surface((320,240)) # This is the game graphics display

        self.clock = pygame.time.Clock()

        # Create a Dictionary containing all the game assets
        self.assets = {
            'decor': load_images('tiles/decor'),
            'grass': load_images('tiles/grass'),
            'large_decor': load_images('tiles/large_decor'),
            'stone': load_images('tiles/stone'),
            'player': load_image('entities/player.png'),
            'background': load_image('background.png'),
            'clouds': load_images('clouds'),
            'player/idle': Animation(load_images('entities/player/idle'),img_dur = 6),
            'player/run': Animation(load_images('entities/player/run'),img_dur = 4),
            'player/jump': Animation(load_images('entities/player/jump')),
            'player/slide': Animation(load_images('entities/player/slide')),
            'player/wall_slide': Animation(load_images('entities/player/wall_slide')),
            'particle/leaf': Animation(load_images('particles/leaf'), img_dur = 20, loop=False),
        }

        self.movement = [False,False]

        self.player = Player(self,(50,50),(8,15))

        self.tilemap = Tilemap(self, 16)

        # Load a level
        self.tilemap.load('map.json')

        self.scroll = [0,0] # create a list representing the camera position

        self.clouds = Clouds(self.assets['clouds'], count=8)

        self.leaf_spawners = []

        # Create rectangles representing leaf spawning areas of all the trees
        for tree in self.tilemap.extract([('large_decor',2)], keep=True):
                self.leaf_spawners.append(pygame.Rect(4 + tree['pos'][0], 4 + tree['pos'][1], 23, 13))

        self.particles = []


    def run(self): # This is the game loop
        while True:

            self.display.blit(self.assets['background'],(0,0))

            self.scroll[0] += (self.player.rect().centerx - self.display.get_width() / 2 - self.scroll[0]) / 1
            self.scroll[1] += (self.player.rect().centery - self.display.get_height() / 2 - self.scroll[1]) / 1
            render_scroll = (int(self.scroll[0]),int(self.scroll[1])) # integer version of scroll position

            # Spawn Particles
            for rect in self.leaf_spawners:
                # Note: spawn rate of particles is proportional to the size of the particle emitter rectangle
                if random.random() * 49999 < rect.width * rect.height: 
                    pos = (rect.x + random.random() * rect.width, rect.y + random.random() * rect.height)
                    self.particles.append(Particle(self, 'leaf', pos, velocity = [-0.1, 0.3], frame = random.randint(0,20)))


            self.clouds.update() # move the clouds
            self.clouds.render(self.display, offset = render_scroll) # render the clouds

            self.tilemap.render(self.display, offset = render_scroll) # render tilemap objects

            self.player.update(self.tilemap, (2*(self.movement[1] - self.movement[0]),0))
            self.player.render(self.display, offset = render_scroll)

            # Update and Render Particles
            for particle in self.particles.copy(): # work with a copy of the particles list because we are removing items!
                kill = particle.update() # update particle and check if it is EOL
                particle.render(self.display,offset = render_scroll) # render each particle
                if particle.type == 'leaf':
                    particle.pos[0] += math.sin(particle.animation.frame * 0.035) * 0.3 # add some oscillations in x-axis movement

                if kill: self.particles.remove(particle) # remove EOL particles

            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                # This input detection logic is similar to axis() in unity
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                        self.movement[0] = True
                    if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        self.movement[1] = True

                    # Handle Jumping (Allows multiple jumps)
                    if (event.key == pygame.K_UP or event.key == pygame.K_w) and self.player.jumps > 0:
                        self.player.velocity[1] = -8
                        self.player.jumps -= 1 # take away one of the player's available jumps
                        # print(self.player.jumps)

                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                        self.movement[0] = False
                    if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        self.movement[1] = False

            # self.screen.blit(self.img,self.img_pos)
            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()),(0,0)) # Render the game graphics onto an up-scaled display
            pygame.display.update()
            self.clock.tick(60)


Game().run()