import libtcodpy as libtcod
from random import randint

from components.fighter import Fighter
from components.inventory import Inventory
from components.item import Item
from components.level import Level
from entity import Entity
from game_messages import MessageLog, Message
from game_states import GameStates
from global_variables import GlobalVariables
from item_functions import catch
from map_objects.game_map import GameMap
from map_objects.world_gen import World
from priority_queue import PriorityQueue
from render_functions import RenderOrder

def get_constants():
    window_title = 'Pokemon Wild pre-alpha'

    # Size of the terminal window.
    screen_width = 80
    screen_height = 50

    bar_width = 20
    panel_height = 7
    panel_y = screen_height - panel_height

    message_x = bar_width + 2
    message_width = screen_width - bar_width - 2
    message_height = panel_height - 1

    # Size of the playable area.
    map_width = 90
    map_height = 53

    # Size of the camera viewport.
    camera_width = 80
    camera_height = 43

    fov_algorithm = 0
    fov_light_walls = True
    fov_radius = 10
    
    monster_spawn_chance = 990
    item_spawn_chance = 990

    colors = {
        'dark_wall': libtcod.Color(0, 0, 100),
        'dark_ground': libtcod.Color(50, 50, 150),

        # Vegetation biome colors.
        'dark_dirt': libtcod.darker_sepia,
        'light_dirt': libtcod.sepia,

        'dark_grass': libtcod.darker_green,
        'light_grass': libtcod.green,

        'dark_tall_grass': libtcod.dark_chartreuse,
        'light_tall_grass': libtcod.chartreuse,

        'dark_shrub': libtcod.darkest_lime,
        'light_shrub': libtcod.dark_lime
    }

    # Generate seeds used for world gen.
    seeds = []
    for i in range(5):
        seeds.append(randint(0, 10000))

    world = World(map_width, map_height, seeds)

    constants = {
        'window_title': window_title,
        'screen_width': screen_width,
        'screen_height': screen_height,
        'bar_width': bar_width,
        'panel_height': panel_height,
        'panel_y': panel_y,
        'message_x': message_x,
        'message_width': message_width,
        'message_height': message_height,
        'map_width': map_width,
        'map_height': map_height,
        'camera_width': camera_width,
        'camera_height': camera_height,
        'fov_algorithm': fov_algorithm,
        'fov_light_walls': fov_light_walls,
        'fov_radius': fov_radius,
        'monster_spawn_chance': monster_spawn_chance,
        'item_spawn_chance': item_spawn_chance,
        'colors': colors,
        'world': world
    }

    return constants

def get_game_variables(constants):
    # Start the priority queue.
    priority_queue = PriorityQueue()

    # Start tracking some global variables
    global_variables = GlobalVariables()

    # Initialize Player entity.
    fighter_component = Fighter(hp=30, defense=2, power=5)
    inventory_component = Inventory(26)
    level_component = Level()
    x = randint(2, constants['map_width'] - 2)
    y = randint(2, constants['map_height'] - 2)
    player = Entity(x, y, '@', libtcod.red, 'Red', global_variables.get_new_ID(), blocks=True, render_order=RenderOrder.ACTOR, fighter=fighter_component, inventory=inventory_component, level=level_component)
    priority_queue.put(action_points=player.fighter.speed, ID=player.ID) # Add the player to the queue for the first time.
    entities = [player]

    # Add a pokeball to the Player inventory.
    item_component = Item(use_function=catch, targeting=True, can_contain=True,
                            targeting_message=Message('Left-click a target tile to throw the pokeball, or right-click to cancel. The target must have less than 100 hp.', libtcod.light_cyan),
                            alt_targeting_message=Message('Left-click a target tile to throw the pokeball, or right-click to cancel. The tile must be empty.', libtcod.light_cyan),
                            power=100)
    item = Entity(0, 0, 'o', libtcod.red, 'Pokeball', global_variables.get_new_ID(), render_order=RenderOrder.ITEM, item=item_component)
    player.inventory.start_with_item(item)

    # Generate world map.
    game_map = GameMap(constants['world'].width, constants['world'].height)
    game_map.make_map(constants['map_width'], constants['map_height'], player, entities, global_variables,
                        priority_queue, constants['monster_spawn_chance'], constants['item_spawn_chance'], constants['world']) # TODO: Spawn chances should be biome variables
    
    # Define the Message Log.
    message_log = MessageLog(constants['message_x'], constants['message_width'], constants['message_height'])

    # Set the Game State.
    game_state = GameStates.ENEMY_TURN # The player is not guaranteed to go first.

    return player, entities, game_map, message_log, game_state, priority_queue, global_variables, constants['world']