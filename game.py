import sys
import pygame
from scripts.entities import PhysicsEntity # Import just the PhysicsEntity class from this script
from scripts.utils import load_image, load_images
from scripts.tilemap import Tilemap
from scripts.clouds import Cloud, Clouds

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
            'clouds': load_images('clouds')
        }

        self.movement = [False,False]

        self.player = PhysicsEntity(self,'player',(50,50),(8,15))

        self.tilemap = Tilemap(self, 16)

        self.scroll = [0,0] # create a list representing the camera position

        self.clouds = Clouds(self.assets['clouds'], count=8)

    def run(self): # This is the game loop
        while True:

            self.display.blit(self.assets['background'],(0,0))

            self.scroll[0] += (self.player.rect().centerx - self.display.get_width() / 2 - self.scroll[0]) / 8
            self.scroll[1] += (self.player.rect().centery - self.display.get_height() / 2 - self.scroll[1]) / 8
            render_scroll = (int(self.scroll[0]),int(self.scroll[1])) # integer version of scroll position

            self.clouds.update() # move the clouds
            self.clouds.render(self.display, offset = render_scroll) # render the clouds

            self.tilemap.render(self.display, offset = render_scroll) # this renders every single tile from the tilemap
            
            self.player.update(self.tilemap, (2*(self.movement[1] - self.movement[0]),0))
            self.player.render(self.display, offset = render_scroll)
            
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

                    # Handle Jumping
                    if event.key == pygame.K_UP or event.key == pygame.K_w:
                        self.player.velocity[1] = -8

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