import libtcodpy as libtcod
import cProfile             # Debug import

from components.ai import BasicMonster
from death_functions import kill_monster, kill_player
from entity import get_blocking_entities_at_location
from fov_functions import initialize_fov, recompute_fov
from game_messages import Message
from game_states import GameStates
from input_handlers import handle_keys, handle_mouse, handle_main_menu
from loader_functions.initialize_new_game import get_constants, get_game_variables
from loader_functions.data_loaders import load_game, save_game
from menus import main_menu, message_box
from priority_queue import PriorityQueue
from render_functions import clear_all, render_all

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

    while not libtcod.console_is_window_closed():
        libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS | libtcod.EVENT_MOUSE, key, mouse)

        if fov_recompute:
            recompute_fov(fov_map, player.x, player.y, constants['fov_radius'], constants['fov_light_walls'], constants['fov_algorithm'])

        # Only render and recompute FOV while on the player's turn.
        if not game_state == GameStates.ENEMY_TURN:
            # Prepare camera.
            camera_h = constants['camera_height']
            camera_w = constants['camera_width']
            camera_x = player.x - int(camera_w / 2) - 1
            camera_y = player.y - int(camera_h / 2) - 1

            # Set camera max. It is implied that 0 is min.
            camera_x_max = game_map.width - camera_w
            camera_y_max = game_map.height - camera_h

            # Ensure the camera does not reveal things outside the map
            if camera_x < 0: camera_x = 0
            if camera_y < 0: camera_y = 0
            if camera_x > camera_x_max: camera_x = camera_x_max
            if camera_y > camera_y_max: camera_y = camera_y_max


            render_all(con, panel, entities, player, game_map, fov_map, fov_recompute, message_log,
                    constants['screen_width'], constants['screen_height'], constants['bar_width'],
                    constants['panel_height'], constants['panel_y'], mouse, constants['colors'], game_state,
                    camera_x, camera_y, constants['camera_width'], constants['camera_height'])

            fov_recompute = False

            libtcod.console_flush()

            # The console is cleared, but it will only be flushed on the player's turn. 
            clear_all(con, entities, camera_x, camera_y)

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

        # List of possible actions taken by the player.
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

        left_click = mouse_action.get('left_click')
        right_click = mouse_action.get('right_click')

        player_turn_results = []

        if move and game_state == GameStates.PLAYERS_TURN:
            dx, dy = move
            destination_x = player.x + dx
            destination_y = player.y + dy

            if not game_map.is_blocked(destination_x, destination_y):
                target = get_blocking_entities_at_location(entities, destination_x, destination_y)

                if target:
                    attack_results = player.fighter.attack(target)
                    player_turn_results.extend(attack_results)
                else:
                    player.move(dx, dy)
                    
                    fov_recompute = True

                priority_queue.put(player.fighter.speed, player.ID) # The player spends their turn to move/attack.
                game_state = GameStates.ENEMY_TURN

        elif wait:
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
       
        if game_state == GameStates.TARGETING:
            if left_click:
                target_x, target_y = left_click

                item_use_results = player.inventory.use(targeting_item, entities=entities, fov_map=fov_map,
                                                        target_x=target_x, target_y=target_y)
                player_turn_results.extend(item_use_results)
            elif right_click:
                player_turn_results.append({'targeting_cancelled': True})
        
        if exit:
            if game_state in (GameStates.SHOW_INVENTORY, GameStates.DROP_INVENTORY, GameStates.CHARACTER_SCREEN):
                game_state = previous_game_state
            elif game_state == GameStates.TARGETING:
                player_turn_results.append({'targeting_cancelled': True})
            else:
                save_game(player, entities, game_map, message_log, game_state, priority_queue, global_variables, world)
                return True

        if fullscreen:
            libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())

        if level_up:
            if level_up == 'hp':
                player.fighter.max_hp += 20
                player.fighter.hp += 20
            elif level_up == 'str':
                player.fighter.power += 1
            elif level_up == 'def':
                player.fighter.defense += 1

            game_state = previous_game_state

        if show_character_screen:
            previous_game_state = game_state
            game_state = GameStates.CHARACTER_SCREEN

        for player_turn_result in player_turn_results:
            # List of possible results.
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