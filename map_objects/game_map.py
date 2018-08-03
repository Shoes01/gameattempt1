import libtcodpy as libtcod
from random import randint

from components.ai import BasicMonster
from components.fighter import Fighter

from entity import Entity

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

    def make_map(self, map_width, map_height, player, entities):
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
                    player.y = int(map_height/2 + 2)
                #vertical road
                elif chance < 50 and x > map_width/2 - 3 and x < map_width/2 + 3:
                    self.tiles[x][y].tile_type = 'dirt'
                    player.x = int(map_width/2)
                    player.y = 2
        
        self.place_entities(map_height, map_width, entities)

    def place_entities(self, map_height, map_width, entities):
        #place monsters according to the tile they are found in
        for y in range(map_height):
            for x in range(map_width):
                spawn_chance = randint(0, 100)
                if spawn_chance > 99:
                    #a monster spawns here!
                    if self.tiles[x][y].tile_type == 'dirt':
                        fighter_component = Fighter(hp=3, defense=3, power=1)
                        ai_component = BasicMonster()
                        monster = Entity(x, y, 'g', libtcod.light_grey, 'Geodude', blocks=True, fighter=fighter_component, ai=ai_component)
                    elif self.tiles[x][y].tile_type == 'grass':
                        fighter_component = Fighter(hp=2, defense=0, power=0)
                        ai_component = BasicMonster()
                        monster = Entity(x, y, 'c', libtcod.light_green, 'Caterpie', blocks=True, fighter=fighter_component, ai=ai_component)
                    
                    entities.append(monster)

    def is_blocked(self, x, y):
        if self.tiles[x][y].blocked:
            return True

        return False