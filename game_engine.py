import tcod as libtcod
import cProfile             # Debug import

from components.ai import BasicMonster
from components.inventory import Inventory
from components.item import Item
from death_functions import kill_monster, kill_player
from entity import Entity, get_blocking_entities_at_location
from fov_functions import initialize_fov, recompute_fov
from game_messages import Message
from game_states import GameStates
from input_handlers import handle_keys, handle_mouse, handle_main_menu
from item_functions import materia
from loader_functions.initialize_new_game import get_constants, get_game_variables
from loader_functions.data_loaders import load_game, save_game
from map_objects.camera import Camera
from menus import main_menu, message_box
from priority_queue import PriorityQueue
from render_functions import clear_all, render_all, RenderOrder

def main():
    constants = get_constants()

    # Initialize console stuff
    libtcod.console_set_custom_font('arial10x10.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD) # The font.
    libtcod.console_init_root(constants['screen_width'], constants['screen_height'], constants['window_title'], False) #The size of the root console.
    con = libtcod.console_new(constants['screen_width'], constants['screen_height']) # The main console of the game.
    panel = libtcod.console_new(constants['screen_width'], constants['panel_height']) # A UI panel for the game.

    # Declare these variables here, but fill them later
    player = None   
    entities = []
    game_map = None
    message_log = None
    game_state = None
    priority_queue = []
    global_variables = None

    show_main_menu = True
    show_load_error_message = False

    main_menu_background_image = libtcod.image_load('menu_background.png')

    key = libtcod.Key()
    mouse = libtcod.Mouse()

    while not libtcod.console_is_window_closed():
        libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS | libtcod.EVENT_MOUSE, key, mouse)

        if show_main_menu:
            main_menu(con, main_menu_background_image, constants['screen_width'], constants['screen_height'])

            if show_load_error_message:
                message_box(con, 'No save game to load', 50, constants['screen_width'], constants['screen_height'])

            libtcod.console_flush()

            action = handle_main_menu(key)

            new_game = action.get('new_game')
            load_saved_game = action.get('load_game')
            exit_game = action.get('exit')

            if show_load_error_message and (new_game or load_saved_game or exit_game):
                show_load_error_message = False
            elif new_game:
                player, entities, game_map, message_log, game_state, priority_queue, global_variables, world = get_game_variables(constants)
                show_main_menu = False
            elif load_saved_game:
                try:
                    player, entities, game_map, message_log, game_state, priority_queue, global_variables, world = load_game()
                    show_main_menu = False
                except FileNotFoundError:
                    show_load_error_message = True
            elif exit_game:
                break

        else:
            libtcod.console_clear(con)
            play_game(player, entities, game_map, message_log, game_state, con, panel, constants, priority_queue, global_variables, world)

            show_main_menu = True # When play_game() is done, the menu reappears.

def play_game(player, entities, game_map, message_log, game_state, con, panel, constants, priority_queue, global_variables, world):
    fov_recompute = True

    fov_map = initialize_fov(game_map)

    key = libtcod.Key()
    mouse = libtcod.Mouse()

    # Variables used to make decisions during the game.
    targeting_item = None
    previous_game_state = game_state

    # Turn on camera.
    camera = Camera(constants['camera_width'], constants['camera_height'], player.x, player.y, constants['map_width'], constants['map_height'])

    while not libtcod.console_is_window_closed():
        libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS | libtcod.EVENT_MOUSE, key, mouse)

        if fov_recompute:
            recompute_fov(fov_map, player.x, player.y, constants['fov_radius'], constants['fov_light_walls'], constants['fov_algorithm'])

        # Only render and recompute FOV while on the player's turn.
        if not game_state == GameStates.ENEMY_TURN:
            render_all(con, panel, entities, player, game_map, fov_map, fov_recompute, message_log,
                    constants['screen_width'], constants['screen_height'], constants['bar_width'],
                    constants['panel_height'], constants['panel_y'], mouse, constants['colors'], game_state,
                    camera)

            fov_recompute = False

            libtcod.console_flush()

            # The console is cleared, but it will only be flushed on the player's turn. 
            clear_all(con, entities, camera.x, camera.y)

        action = handle_keys(key, game_state)
        mouse_action = handle_mouse(mouse)

        enemy = None # If it's not the player's turn, it's _this_ enemy's turn.

        # Decide the entity's turn.
        if not priority_queue.empty() and game_state == GameStates.ENEMY_TURN:
            queue_ID = priority_queue.get_ID() # This removes the topmost ID from the queue.
            for entity in entities:
                if queue_ID == entity.ID and not entity.is_dead(): # If the entity is dead, do nothing. It has already been removed from the queue.
                    if entity.ai == None: #it's the player
                        # The player gets reinserted into the queue after their action.
                        game_state = GameStates.PLAYERS_TURN
                        break
                    else:
                        # The enemy gets reinserted into the queue after their action.
                        enemy = entity
                        break

        """

        List of possible actions taken by the player.

        """
        move = action.get('move')
        wait = action.get('wait')
        pickup = action.get('pickup')
        show_inventory = action.get('show_inventory')
        drop_inventory = action.get('drop_inventory')
        inventory_index = action.get('inventory_index')
        exit = action.get('exit')
        fullscreen = action.get('fullscreen')
        level_up = action.get('level_up')
        show_character_screen = action.get('show_character_screen')
        show_extract_materia_menu = action.get('show_extract_materia_menu') # Prompt the player to extra materia from creature.
        extraction_index = action.get('extraction_index')                   # Select this entry from the extraction menu.

        left_click = mouse_action.get('left_click')
        right_click = mouse_action.get('right_click')

        player_turn_results = []

        # TODO: Put all of these behind a "if game_state == GameStates.PLAYERS_TURN" loop.
        if move and game_state == GameStates.PLAYERS_TURN:
            # TODO: Prevent player from moving outside the map.
            dx, dy = move
            destination_x = player.x + dx
            destination_y = player.y + dy

            if not game_map.is_blocked(destination_x, destination_y):
                target = get_blocking_entities_at_location(entities, destination_x, destination_y)

                if target:
                    attack_results = player.fighter.attack(target)
                    player_turn_results.extend(attack_results)
                else:
                    # Check to see if the player is lined up with the center.
                    # If so, move the camera with the player.
                    camera_x, camera_y = camera.absolute_center()
                    if player.x == camera_x:
                        camera.move(dx, 0)
                    if player.y == camera_y:
                        camera.move(0, dy)
                    
                    player.move(dx, dy)
                    
                    fov_recompute = True

                priority_queue.put(player.fighter.speed, player.ID) # The player spends their turn to move/attack.
                game_state = GameStates.ENEMY_TURN

        elif wait and game_state == GameStates.PLAYERS_TURN:
            # Puts the player second in queue. 
            priority_queue.put_next(player.ID)
            game_state = GameStates.ENEMY_TURN

        elif pickup and game_state == GameStates.PLAYERS_TURN:
            for entity in entities:
                if entity.item and entity.x == player.x and entity.y == player.y:
                    pickup_results = player.inventory.add_item(entity)
                    player_turn_results.extend(pickup_results)
                    priority_queue.put(player.fighter.speed, player.ID) # The player spends their turn picking up stuff.
                    game_state = GameStates.ENEMY_TURN

                    break
            else:
                message_log.add_message(Message('There is nothing here to pick up.', libtcod.yellow))

        if show_inventory and game_state == GameStates.PLAYERS_TURN:
            previous_game_state = game_state
            game_state = GameStates.SHOW_INVENTORY

        if drop_inventory and game_state == GameStates.PLAYERS_TURN:
            previous_game_state = game_state
            game_state = GameStates.DROP_INVENTORY

        if inventory_index is not None and previous_game_state != GameStates.PLAYER_DEAD and inventory_index < len(player.inventory.items):
            item = player.inventory.items[inventory_index]
            if game_state == GameStates.SHOW_INVENTORY:
                player_turn_results.extend(player.inventory.use(item))
            elif game_state == GameStates.DROP_INVENTORY:
                player_turn_results.extend(player.inventory.drop_item(item))
       
        if game_state == GameStates.TARGETING and game_state == GameStates.PLAYERS_TURN:
            if left_click:
                target_x, target_y = left_click
                target_x += camera.x
                target_y += camera.y

                item_use_results = player.inventory.use(targeting_item, entities=entities, fov_map=fov_map,
                                                        target_x=target_x, target_y=target_y)
                player_turn_results.extend(item_use_results)
            elif right_click:
                player_turn_results.append({'targeting_cancelled': True})
        
        if exit:
            if game_state in (GameStates.SHOW_INVENTORY, GameStates.DROP_INVENTORY, GameStates.CHARACTER_SCREEN, GameStates.MATERIA_SCREEN):
                game_state = previous_game_state
            elif game_state == GameStates.TARGETING:
                player_turn_results.append({'targeting_cancelled': True})
            else:
                save_game(player, entities, game_map, message_log, game_state, priority_queue, global_variables, world)
                return True

        if fullscreen:
            libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())

        if level_up and game_state == GameStates.PLAYERS_TURN:
            if level_up == 'hp':
                player.fighter.max_hp += 20
                player.fighter.hp += 20
            elif level_up == 'str':
                player.fighter.power += 1
            elif level_up == 'def':
                player.fighter.defense += 1

            game_state = previous_game_state

        if show_character_screen and game_state == GameStates.PLAYERS_TURN:
            previous_game_state = game_state
            game_state = GameStates.CHARACTER_SCREEN

        if show_extract_materia_menu and game_state == GameStates.PLAYERS_TURN:
            previous_game_state = game_state
            game_state = GameStates.MATERIA_SCREEN

        if extraction_index is not None and previous_game_state != GameStates.PLAYER_DEAD: 
            # Create the list of items that have materia
            item_list = player.inventory.item_list_with_property('materia')
            # Check to see the index is inside this list
            if extraction_index < len(item_list):
                # Create an item called "type Materia (lvl n)"
                extracting_item = item_list[extraction_index] # This is the pokeball.
                materia_type = extracting_item.item.caught_entity.materia[0]
                materia_level = extracting_item.item.caught_entity.materia[1]
                materia_name = materia_type.capitalize() + 'Materia (lvl ' + str(materia_level)
                
                item_component = Item(use_function=materia, type=materia_type, level=materia_level)
                materia_item = Entity(0, 0, '*', libtcod.white, materia_name, global_variables.get_new_ID(), RenderOrder.ITEM, item=item_component)

                # Add it to the inventory
                player.inventory.add_item(materia_item)
                entities.append(materia_item)

                # Remove the entity from which it came from the parent entity holding it
                extracting_item.caught_entity = None

        """

        List of possible results from actions taken by the player.

        """
        for player_turn_result in player_turn_results:
            message = player_turn_result.get('message')
            dead_entity = player_turn_result.get('dead')
            item_added = player_turn_result.get('item_added')
            item_consumed = player_turn_result.get('consumed')
            item_dropped = player_turn_result.get('item_dropped')
            targeting = player_turn_result.get('targeting')
            targeting_cancelled = player_turn_result.get('targeting_cancelled')
            thrown = player_turn_result.get('thrown')                               # This item was thrown. Returns the item entity.
            catch = player_turn_result.get('catch')                                 # This item catches pokemon. Returns the caught entity.
            release = player_turn_result.get('release')                             # This item released pokemon. Returns the released entity.
            xp = player_turn_result.get('xp')

            if message:
                message_log.add_message(message)

            if dead_entity:
                if dead_entity == player:
                    message, game_state = kill_player(dead_entity)
                else:
                    message = kill_monster(dead_entity)
                message_log.add_message(message)

            if item_added:
                entities.remove(item_added)

            if item_consumed:
                # Removed from inventory in inventory.py
                pass

            if item_dropped:
                entities.append(item_dropped)

            if targeting:
                previous_game_state = GameStates.PLAYERS_TURN
                game_state = GameStates.TARGETING

                targeting_item = targeting

                message_log.add_message(targeting_item.item.targeting_message)

            if targeting_cancelled:
                game_state = previous_game_state

                message_log.add_message(Message('Targeting cancelled'))

            if thrown:
                # Removed from inventory in inventory.py
                thrown.x, thrown.y = player_turn_result.get('target_xy')
                entities.append(thrown)
                game_state = GameStates.PLAYERS_TURN

            if catch:
                entities.remove(catch)

            if release:
                release.x, release.y = player_turn_result.get('target_xy')
                entities.append(release)
                priority_queue.put(release.fighter.speed, release.ID)
            
            if xp:
                leveled_up = player.level.add_xp(xp)
                message_log.add_message(Message('You gain {0} experience points.'.format(xp)))

                if leveled_up:
                    message_log.add_message(Message(
                        'Your battle skills grow stronger! You reached level {0}'.format(player.level.current_level) + '!', libtcod.yellow))
                    previous_game_state = game_state
                    game_state = GameStates.LEVEL_UP

        if game_state == GameStates.ENEMY_TURN and enemy:
            enemy_turn_results = enemy.ai.take_turn(player, fov_map, game_map, entities)

            for enemy_turn_result in enemy_turn_results:
                message = enemy_turn_result.get('message')
                dead_entity = enemy_turn_result.get('dead')

                if message:
                    message_log.add_message(message)

                if dead_entity:
                    if dead_entity == player:
                        message, game_state = kill_player(dead_entity)
                    else:
                        message = kill_monster(dead_entity)                        

                    message_log.add_message(message)

                    if game_state == GameStates.PLAYER_DEAD:
                        break

            if game_state == GameStates.PLAYER_DEAD:
                break

            elif not enemy.ai == None:
                priority_queue.put(enemy.fighter.speed, enemy.ID)

if __name__ == '__main__':
    """
    Replace "main()" with "cProfile.run('main()')" to run a profiler.
    """
    main()