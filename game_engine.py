import libtcodpy as libtcod

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
    libtcod.console_set_custom_font('arial10x10.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
    libtcod.console_init_root(constants['screen_width'], constants['screen_height'], constants['window_title'], False)
    con = libtcod.console_new(constants['screen_width'], constants['screen_height']) # The main console of the game.
    panel = libtcod.console_new(constants['screen_width'], constants['panel_height']) # A UI panel for the game.

    # Declare these variables here, but fill them according to functions below
    player = None
    entities = []
    game_map = None
    message_log = None
    game_state = None
    priority_queue = []
    ID = 1 # 0 belongs to the player. TODO: Find a better alternative to how the ID is currently done. Only Entities have IDs, so there should be a way to store it there...

    show_main_menu = True
    show_load_error_message = False

    main_menu_background_image = libtcod.image_load('menu_background.png')

    key = libtcod.Key()
    mouse = libtcod.Mouse()

    while not libtcod.console_is_window_closed():
        libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS | libtcod.EVENT_MOUSE, key, mouse)

        if show_main_menu:
            main_menu(con, main_menu_background_image, constants['screen_width'],
                      constants['screen_height'])

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
                player, entities, game_map, message_log, game_state, priority_queue = get_game_variables(constants, ID)
                show_main_menu = False
            elif load_saved_game:
                try:
                    player, entities, game_map, message_log, game_state, priority_queue = load_game()
                    show_main_menu = False
                except FileNotFoundError:
                    show_load_error_message = True
            elif exit_game:
                break

        else:
            libtcod.console_clear(con)
            play_game(player, entities, game_map, message_log, game_state, con, panel, constants, priority_queue)

            show_main_menu = True

def play_game(player, entities, game_map, message_log, game_state, con, panel, constants, priority_queue):
    fov_recompute = True

    fov_map = initialize_fov(game_map)

    key = libtcod.Key()
    mouse = libtcod.Mouse()

    targeting_item = None

    previous_game_state = game_state

    while not libtcod.console_is_window_closed():
        libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS | libtcod.EVENT_MOUSE, key, mouse)

        if fov_recompute:
            recompute_fov(fov_map, player.x, player.y, constants['fov_radius'], constants['fov_light_walls'], constants['fov_algorithm'])

        render_all(con, panel, entities, player, game_map, fov_map, fov_recompute, message_log,
                   constants['screen_width'], constants['screen_height'], constants['bar_width'],
                   constants['panel_height'], constants['panel_y'], mouse, constants['colors'], game_state)

        fov_recompute = False

        libtcod.console_flush()

        clear_all(con, entities)

        action = handle_keys(key, game_state)
        mouse_action = handle_mouse(mouse)

        #list of possible actions by the player
        move = action.get('move')
        pickup = action.get('pickup')
        show_inventory = action.get('show_inventory')
        drop_inventory = action.get('drop_inventory')
        inventory_index = action.get('inventory_index')
        exit = action.get('exit')
        fullscreen = action.get('fullscreen')

        left_click = mouse_action.get('left_click')
        right_click = mouse_action.get('right_click')

        player_turn_results = []
        enemy = None #if it's not the player's turn, it's this enemy's turn

        if not priority_queue.empty() and game_state == GameStates.NEUTRAL_TURN:
            queue_ID = priority_queue.get_ID() #this removes the topmost ID from the queue
            for entity in entities:
                if queue_ID == entity.ID and not entity.is_dead():
                    if entity.ai == None: #it's the player
                        game_state = GameStates.PLAYERS_TURN
                        break
                    else:
                        enemy = entity
                        game_state = GameStates.ENEMY_TURN
                        break
            else:
                game_state = GameStates.NEUTRAL_TURN

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

                priority_queue.put(player.fighter.speed, player.ID)
                game_state = GameStates.NEUTRAL_TURN

        elif pickup and game_state == GameStates.PLAYERS_TURN:
            for entity in entities:
                if entity.item and entity.x == player.x and entity.y == player.y:
                    pickup_results = player.inventory.add_item(entity)
                    player_turn_results.extend(pickup_results)

                    break
            else:
                message_log.add_message(Message('There is nothing here to pick up.', libtcod.yellow))
            
            priority_queue.put(player.fighter.speed, player.ID)
            game_state = GameStates.NEUTRAL_TURN

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
            if game_state in (GameStates.SHOW_INVENTORY, GameStates.DROP_INVENTORY):
                game_state = previous_game_state
            elif game_state == GameStates.TARGETING:
                player_turn_results.append({'targeting_cancelled': True})
            else:
                save_game(player, entities, game_map, message_log, game_state, priority_queue)
                return True

        if fullscreen:
            libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())

        for player_turn_result in player_turn_results:
            #list of possible results
            message = player_turn_result.get('message')
            dead_entity = player_turn_result.get('dead')
            item_added = player_turn_result.get('item_added')
            item_consumed = player_turn_result.get('consumed')
            item_dropped = player_turn_result.get('item_dropped')
            targeting = player_turn_result.get('targeting')
            targeting_cancelled = player_turn_result.get('targeting_cancelled')

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
                pass #normall we would have changed states, but this is handled elsewhere

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
                game_state = GameStates.NEUTRAL_TURN

if __name__ == '__main__':
    main()