import tcod as libtcod
from random import randint

from components.ai import BasicMonster
from components.fighter import Fighter
from components.item import Item
from entity import Entity
from global_variables import GlobalVariables
from item_functions import heal
from map_objects.tile import Tile
from map_objects.world_gen import World
from priority_queue import PriorityQueue
from render_functions import RenderOrder


class GameMap:
    """
    Import data from World. Generate GameMap with it.
    """
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.tiles = self.initialize_tiles()

    def initialize_tiles(self):
        # Set the size of the tiles of the map (I think?)
        tiles = [[Tile(False) for y in range(self.height)] for x in range(self.width)]          

        return tiles

    def make_map(self, map_width, map_height, player, entities, global_variables, priority_queue, monster_spawn_chance, item_spawn_chance, world):
        """
        Attempt to use biomes. 
        There is only one biome at the moment.
        """
        for y in range(map_height):
            for x in range(map_width):
                self.tiles[x][y].tile_type = world.get_biome_at_xy(x, y)
        
        self.place_entities(map_height, map_width, entities, global_variables, priority_queue, monster_spawn_chance, item_spawn_chance)

    def place_entities(self, map_height, map_width, entities, global_variables, priority_queue, monster_spawn_chance, item_spawn_chance):        
        #place monsters according to the tile they are found in
        for y in range(map_height):
            for x in range(map_width):
                monster_chance = randint(0, 1000)
                item_chance = randint(0, 1000)
                if monster_chance > monster_spawn_chance:
                    #a monster spawns here!
                    if self.tiles[x][y].tile_type == 'fire':
                        fighter_component = Fighter(hp=3, defense=3, power=1, speed=100, xp=35)
                        ai_component = BasicMonster()
                        materia = ('rock', 1)
                        monster = Entity(x, y, 'g', libtcod.light_grey, 'Geodude', global_variables.get_new_ID(), blocks=True, render_order=RenderOrder.ACTOR, fighter=fighter_component, ai=ai_component, materia=materia)
                        priority_queue.put(action_points=monster.fighter.speed, ID=monster.ID)
                    elif self.tiles[x][y].tile_type == 'wind':
                        fighter_component = Fighter(hp=1, defense=0, power=2, speed=80, xp=10)
                        ai_component = BasicMonster()
                        materia = ('poison', 1)
                        monster = Entity(x, y, 'b', libtcod.yellow, 'Beedrill', global_variables.get_new_ID(), blocks=True, render_order=RenderOrder.ACTOR, fighter=fighter_component, ai=ai_component, materia=materia)
                        priority_queue.put(action_points=monster.fighter.speed, ID=monster.ID)
                    elif self.tiles[x][y].tile_type == 'earth':
                        fighter_component = Fighter(hp=2, defense=2, power=2, speed=200, xp=20)
                        ai_component = BasicMonster()
                        materia = ('life', 1)
                        monster = Entity(x, y, 'b', libtcod.darker_sea, 'Bulbasaur', global_variables.get_new_ID(), blocks=True, render_order=RenderOrder.ACTOR, fighter=fighter_component, ai=ai_component, materia=materia)
                        priority_queue.put(action_points=monster.fighter.speed, ID=monster.ID)
                    elif self.tiles[x][y].tile_type == 'water':
                        fighter_component = Fighter(hp=2, defense=1, power=1, speed=300, xp=15)
                        ai_component = BasicMonster()
                        materia = ('poison', 2)
                        monster = Entity(x, y, 'o', libtcod.darker_azure, 'Oddish', global_variables.get_new_ID(), blocks=True, render_order=RenderOrder.ACTOR, fighter=fighter_component, ai=ai_component, materia=materia)
                        priority_queue.put(action_points=monster.fighter.speed, ID=monster.ID)
                    
                    else: monster = None
                    
                    if monster:
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