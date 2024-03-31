import sys
import pygame
from scripts.entities import PhysicsEntity # Import just the PhysicsEntity class from this script
from scripts.utils import load_image, load_images
from scripts.tilemap import Tilemap

class Game:
    def __init__(self):

        pygame.init()

        pygame.display.set_caption('ninja game')
        self.screen = pygame.display.set_mode((640,480)) # This is what is shown on the computer screen

        self.display = pygame.Surface((320,240)) # This is the game graphics display

        self.clock = pygame.time.Clock()

        self.movement = [False,False]

        self.player = PhysicsEntity(self,'player',(50,50),(8,15))

        self.tilemap = Tilemap(self, 16)

        # Create a Dictionary containing all the game assets
        self.assets = {
            'decor': load_images('tiles/decor'),
            'grass': load_images('tiles/grass'),
            'large_decor': load_images('tiles/large_decor'),
            'stone': load_images('tiles/stone'),
            'player': load_image('entities/player.png')
        }


    def run(self): # This is the game loop
        while True:

            self.display.fill((14,219,248)) # clear the screen
            
            self.player.update(self.tilemap, (2*(self.movement[1] - self.movement[0]),0))
            self.player.render(self.display)
            self.tilemap.render(self.display)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                # This input detection logic is similar to axis() in unity
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        self.movement[0] = True
                    if event.key == pygame.K_RIGHT:
                        self.movement[1] = True

                    # Handle Jumping
                    if event.key == pygame.K_UP:
                        self.player.velocity[1] = -8

                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT:
                        self.movement[0] = False
                    if event.key == pygame.K_RIGHT:
                        self.movement[1] = False

            # self.screen.blit(self.img,self.img_pos)
            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()),(0,0)) # Render the game graphics onto an up-scaled display
            pygame.display.update()
            self.clock.tick(60)


Game().run()