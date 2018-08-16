import libtcodpy as libtcod
from random import randint

from components.ai import BasicMonster
from components.fighter import Fighter
from components.item import Item
from entity import Entity
from global_variables import GlobalVariables
from item_functions import heal
from map_objects.tile import Tile
from priority_queue import PriorityQueue
from render_functions import RenderOrder


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

    def make_map(self, map_width, map_height, player, entities, global_variables, priority_queue, monster_spawn_chance, item_spawn_chance):
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
        
        self.place_entities(map_height, map_width, entities, global_variables, priority_queue, monster_spawn_chance, item_spawn_chance)

    def place_entities(self, map_height, map_width, entities, global_variables, priority_queue, monster_spawn_chance, item_spawn_chance):        
        #place monsters according to the tile they are found in
        for y in range(map_height):
            for x in range(map_width):
                monster_chance = randint(0, 1000)
                item_chance = randint(0, 1000)
                if monster_chance > monster_spawn_chance:
                    #a monster spawns here!
                    if self.tiles[x][y].tile_type == 'dirt':
                        fighter_component = Fighter(hp=3, defense=3, power=1, speed=100, xp=35)
                        ai_component = BasicMonster()
                        monster = Entity(x, y, 'g', libtcod.light_grey, 'Geodude', global_variables.get_new_ID(), blocks=True, render_order=RenderOrder.ACTOR, fighter=fighter_component, ai=ai_component)
                        priority_queue.put(action_points=monster.fighter.speed, ID=monster.ID)
                    elif self.tiles[x][y].tile_type == 'grass':
                        fighter_component = Fighter(hp=2, defense=0, power=0, speed=600, xp=10)
                        ai_component = BasicMonster()
                        monster = Entity(x, y, 'c', libtcod.light_green, 'Caterpie', global_variables.get_new_ID(), blocks=True, render_order=RenderOrder.ACTOR, fighter=fighter_component, ai=ai_component)
                        priority_queue.put(action_points=monster.fighter.speed, ID=monster.ID)
                    
                    entities.append(monster)
                    
                if item_chance > item_spawn_chance:
                    #an item spawns here!
                    if not any([entity for entity in entities if entity.x == x and entity.y == y]):
                        item_component = Item(use_function=heal, amount=4)
                        item = Entity(x, y, '!', libtcod.violet, 'Healing Potion', global_variables.get_new_ID(), render_order=RenderOrder.ITEM, item=item_component)

                        entities.append(item)

    def is_blocked(self, x, y):
        if self.tiles[x][y].blocked:
            return True

        return False