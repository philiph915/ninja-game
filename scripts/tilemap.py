import pygame

NEIGHBOR_OFFSETS = [(-1,0),(-1,-1),(0,-1),(1,-1),(1,0),(0,0),(1,1),(0,1),(-1,1)] # get all the tiles in these grid positions relative to the player
PHYSICS_TILES = {'grass','stone'} # this is a set; it is faster to check if a value is in a set rather than if a value is in a list

class Tilemap:
    def __init__(self, game, tile_size = 16): # 16 is the default tile size
        self.game = game
        self.tile_size = tile_size
        self.tilemap = {} # this is a dictionary to map each tile to a location
        self.offgrid_tiles = []

        # Template for putting tiles into a dictionary
        # {(0,0): 'grass', (0,1): 'dirt', (9999, 0): 'grass'} # save individual tile locations as specific tiles (this allows you to not have to code empty spaces into a list)

        # generate tile data
        for i in range(10):
            # results in positions 3 thru 12 on x, 10 on y being grass tiles
            self.tilemap[str(3+i) + ';10'] = {'type': 'grass', 'variant': 1, 'pos': (3+i,10)} # keep pos as a tuple, everything else is a string
            self.tilemap['10;' + str(5+i)] = {'type': 'stone', 'variant': 1, 'pos': (10,5+i)}

    def render(self,surf, offset = (0,0)):

        # Render Decorations first
        for tile in self.offgrid_tiles:
            surf.blit(self.game.assets[tile['type']][tile['variant']],(tile['pos'][0] - offset[0], tile['pos'][1] - offset[1])) # position is in pixels for off-grid graphics
        
        for loc in self.tilemap:
            tile = self.tilemap[loc]
             # get the correct surface (type and varant) and blit at the correct position for the current tile
            surf.blit(self.game.assets[tile['type']][tile['variant']],(tile['pos'][0]*self.tile_size - offset[0], tile['pos'][1]*self.tile_size - offset[1]))

    def tiles_around(self,pos): # get the neighboring tiles relative to a given position in the game world
        
        tiles = [] # initialize list of tiles to return
        # converta pixel position into a grid position
        tile_loc = (int(pos[0] // self.tile_size),int(pos[1] // self.tile_size)) # double slash is integer division, which drops the decimals after division
        for offset in NEIGHBOR_OFFSETS:
            check_loc = str(tile_loc[0] + offset[0]) + ';' + str(tile_loc[1] + offset[1])
            if check_loc in self.tilemap: # check if there is a tile in this location ( I guess this already knows to check the 'pos' key)
                tiles.append(self.tilemap[check_loc])
        return tiles
    
    # filter tiles that have physics enabled
    def physics_rects_around(self, pos):
        rects = []
        for tile in self.tiles_around(pos):
            if tile['type'] in PHYSICS_TILES:
                rects.append(pygame.Rect(tile['pos'][0]*self.tile_size, tile['pos'][1]*self.tile_size,self.tile_size,self.tile_size))
        return rects