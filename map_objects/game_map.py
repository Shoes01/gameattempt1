from random import randint

from map_objects.tile import Tile


class GameMap:
    """
    The GameMap will consist of a road that passes through the center of the screen.
    Choose a start point, draw from start to middle.
    Choose an end point, draw from middle to end.
    TODO: Remember endpoint for next map gen

    BUT FOR NOW it will just be a hand made road.

    """
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.tiles = self.initialize_tiles()

    def initialize_tiles(self):
        #Fill everything with grass
        tiles = [[Tile(False) for y in range(self.height)] for x in range(self.width)]          

        return tiles

    def make_map(self, map_width, map_height, player):
        """
        At first, the road will have a 50% chance to be E-W or N-S. 
        """
        chance = randint(0, 100)
    
        for y in range(map_height):
            for x in range(map_width):
                #horizontal road
                if chance >= 50 and y > map_height/2 - 3 + 2 and y < map_height/2 + 3 + 2: #Plus two to offset the fact that map height is not console height
                    self.tiles[x][y].tile_type = 'dirt'
                    player.x = 2
                    #player.y doesn't change
                #vertical road
                elif chance < 50 and x > map_width/2 - 3 and x < map_width/2 + 3:
                    self.tiles[x][y].tile_type = 'dirt'
                    #player.x doesn't change
                    player.y = 2

    def is_blocked(self, x, y):
        if self.tiles[x][y].blocked:
            return True

        return False