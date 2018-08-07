import libtcodpy as libtcod

from components.ai import BasicMonster
from components.fighter import Fighter
from death_functions import kill_monster, kill_player
from entity import Entity, get_blocking_entities_at_location
from fov_functions import initialize_fov, recompute_fov
from game_states import GameStates
from input_handlers import handle_keys
from map_objects.game_map import GameMap
from priority_queue import PriorityQueue
from render_functions import clear_all, render_all, RenderOrder

def main():
    screen_width = 80
    screen_height = 50
    map_width = 80
    map_height = 45
    ID = 1 #0 belong to the player
    
    libtcod.sys_set_fps(20)

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

    con = libtcod.console_new(screen_width, screen_height)

    game_map = GameMap(map_width, map_height)
    game_map.make_map(map_width, map_height, player, entities, ID, priority_queue)

    fov_recompute = True

    fov_map = initialize_fov(game_map)    

    key = libtcod.Key()
    mouse = libtcod.Mouse()

    while not libtcod.console_is_window_closed():
        libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS, key, mouse)

        if not game_state == GameStates.PLAYERS_TURN: #this pretty much pauses the game while it is the player's turn
            priority_queue.tick()

        if fov_recompute:
            recompute_fov(fov_map, player.x, player.y, fov_radius, fov_light_walls, fov_algorithm)

        render_all(con, entities, player, game_map, fov_map, fov_recompute, screen_width, screen_height, colors)

        fov_recompute = False

        libtcod.console_flush()

        clear_all(con, entities)

        action = handle_keys(key)

        move = action.get('move')
        exit = action.get('exit')
        fullscreen = action.get('fullscreen')

        player_turn_results = []
        enemy = None #if it's not the player's turn, it's this enemy's turn

        print(priority_queue.ticker, ') AP: ', priority_queue.queue[0][0], ' ID: ', priority_queue.queue[0][1])

        if not priority_queue.empty() and priority_queue.ticker == priority_queue.peek():
            print('Looping.')
            queue_ID = priority_queue.get_ID()
            for entity in entities:
                if  queue_ID == entity.ID:
                    priority_queue.untick() #in case there are many entites with the same speed
                    if entity.ai == None: #it's the player
                        game_state = GameStates.PLAYERS_TURN
                        break
                    else:
                        enemy = entity
                        game_state = GameStates.ENEMY_TURN
                        break
            else:
                game_state = GameStates.NEUTRAL_TURN

        
        print('GameState: ', game_state)

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
                print(message)

            if dead_entity:
                if dead_entity == player:
                    message, game_state = kill_player(dead_entity)
                else:
                    message = kill_monster(dead_entity)

                print(message)

        if game_state == GameStates.ENEMY_TURN and enemy:
            enemy_turn_results = enemy.ai.take_turn(player, fov_map, game_map, entities)

            for enemy_turn_result in enemy_turn_results:
                message = enemy_turn_result.get('message')
                dead_entity = enemy_turn_result.get('dead')

                if message:
                    print(message)

                if dead_entity:
                    if dead_entity == player:
                        message, game_state = kill_player(dead_entity)
                    else:
                        message = kill_monster(dead_entity)

                    print(message)

                    if game_state == GameStates.PLAYER_DEAD:
                        break

            if game_state == GameStates.PLAYER_DEAD:
                break

            else:
                priority_queue.put(enemy.fighter.speed, enemy.ID)
                game_state = GameStates.NEUTRAL_TURN

if __name__ == '__main__':
    main()