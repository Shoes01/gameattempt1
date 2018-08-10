import libtcodpy as libtcod

from components.fighter import Fighter
from components.inventory import Inventory
from entity import Entity
from game_messages import MessageLog
from game_states import GameStates
from global_variables import GlobalVariables
from map_objects.game_map import GameMap
from priority_queue import PriorityQueue
from render_functions import RenderOrder

def get_constants():
    window_title = 'Pokemon Wild pre-alpha'

    screen_width = 80
    screen_height = 50

    bar_width = 20
    panel_height = 7
    panel_y = screen_height - panel_height

    message_x = bar_width + 2
    message_width = screen_width - bar_width - 2
    message_height = panel_height - 1

    map_width = 80
    map_height = 43

    fov_algorithm = 0
    fov_light_walls = True
    fov_radius = 10
    
    monster_spawn_chance = 990
    item_spawn_chance = 990

    colors = {
        'dark_wall': libtcod.Color(0, 0, 100),
        'dark_ground': libtcod.Color(50, 50, 150),
        'dark_dirt': libtcod.Color(63, 50, 31),
        'dark_grass': libtcod.Color(0, 64, 0),
        'light_dirt': libtcod.Color(127, 101, 63),
        'light_grass': libtcod.Color(0, 191, 0)
    }

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
        'fov_algorithm': fov_algorithm,
        'fov_light_walls': fov_light_walls,
        'fov_radius': fov_radius,
        'monster_spawn_chance': monster_spawn_chance,
        'item_spawn_chance': item_spawn_chance,
        'colors': colors
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
    player = Entity(0, 0, '@', libtcod.red, 'Red', global_variables.get_new_ID(), blocks=True, render_order=RenderOrder.ACTOR, fighter=fighter_component, inventory=inventory_component)
    priority_queue.put(action_points=player.fighter.speed, ID=player.ID)
    entities = [player]

    # Define the Game Map.
    game_map = GameMap(constants['map_width'], constants['map_height'])
    game_map.make_map(constants['map_width'], constants['map_height'], player, entities, global_variables, priority_queue, constants['monster_spawn_chance'], constants['item_spawn_chance']) # TODO: Spawn chances should be biome variables

    # Define the Message Log.
    message_log = MessageLog(constants['message_x'], constants['message_width'], constants['message_height'])

    # Set the Game State.
    game_state = GameStates.NEUTRAL_TURN

    return player, entities, game_map, message_log, game_state, priority_queue, global_variables