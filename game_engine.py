import libtcodpy as libtcod

from components.ai import BasicMonster
from components.fighter import Fighter
from death_functions import kill_monster, kill_player
from entity import Entity, get_blocking_entities_at_location
from fov_functions import initialize_fov, recompute_fov
from game_messages import MessageLog
from game_states import GameStates
from input_handlers import handle_keys
from map_objects.game_map import GameMap
from priority_queue import PriorityQueue
from render_functions import clear_all, render_all, RenderOrder

def main():
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
    ID = 1 #0 belong to the player

    fov_algorithm = 0
    fov_light_walls = True
    fov_radius = 10

    priority_queue = PriorityQueue() #start a queue

    game_state = GameStates.NEUTRAL_TURN

    colors = {
        'dark_wall': libtcod.Color(0, 0, 100),
        'dark_ground': libtcod.Color(50, 50, 150),
        'dark_dirt': libtcod.Color(63, 50, 31),
        'dark_grass': libtcod.Color(0, 64, 0),
        'light_dirt': libtcod.Color(127, 101, 63),
        'light_grass': libtcod.Color(0, 191, 0)
    }

    fighter_component = Fighter(hp=30, defense=2, power=5)
    player = Entity(0, 0, '@', libtcod.red, 'Red', ID=0, blocks=True, render_order=RenderOrder.ACTOR, fighter=fighter_component)
    priority_queue.put(action_points=player.fighter.speed, ID=player.ID)
    entities = [player]

    libtcod.console_set_custom_font('arial10x10.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)

    libtcod.console_init_root(screen_width, screen_height, 'Game Attempt 1', False)

    con = libtcod.console_new(screen_width, screen_height) #main console to display game
    panel = libtcod.console_new(screen_width, panel_height) #UI info at bottom of screen

    game_map = GameMap(map_width, map_height)
    game_map.make_map(map_width, map_height, player, entities, ID, priority_queue)

    fov_recompute = True

    fov_map = initialize_fov(game_map)

    message_log = MessageLog(message_x, message_width, message_height)

    key = libtcod.Key()
    mouse = libtcod.Mouse()

    while not libtcod.console_is_window_closed():
        libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS | libtcod.EVENT_MOUSE, key, mouse)

        if fov_recompute:
            recompute_fov(fov_map, player.x, player.y, fov_radius, fov_light_walls, fov_algorithm)

        render_all(con, panel, entities, player, game_map, fov_map, fov_recompute, message_log, screen_width,
                   screen_height, bar_width, panel_height, panel_y, mouse, colors)

        fov_recompute = False

        libtcod.console_flush()

        clear_all(con, entities)

        action = handle_keys(key)

        move = action.get('move')
        exit = action.get('exit')
        fullscreen = action.get('fullscreen')

        player_turn_results = []
        enemy = None #if it's not the player's turn, it's this enemy's turn

        if not priority_queue.empty() and not game_state == GameStates.PLAYERS_TURN:
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

        if exit:
            return True

        if fullscreen:
            libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())

        for player_turn_result in player_turn_results:
            message = player_turn_result.get('message')
            dead_entity = player_turn_result.get('dead')

            if message:
                message_log.add_message(message)

            if dead_entity:
                if dead_entity == player:
                    message, game_state = kill_player(dead_entity)
                else:
                    message = kill_monster(dead_entity)
                message_log.add_message(message)

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