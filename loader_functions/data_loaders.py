import os
import shelve


def save_game(player, entities, game_map, message_log, game_state, priority_queue, global_variables, world):
    save_file = 'savegame'
    save_path = 'savegames'
    with shelve.open(os.path.join(save_path, save_file), 'n') as data_file:
        data_file['player_index'] = entities.index(player)
        data_file['entities'] = entities
        data_file['game_map'] = game_map
        data_file['message_log'] = message_log
        data_file['game_state'] = game_state
        data_file['priority_queue'] = priority_queue
        data_file['global_variables'] = global_variables
        data_file['world'] = world

def load_game():
    save_file = 'savegame'
    save_path = 'savegames'
    if not os.path.isfile(os.path.join(save_path, save_file+'.dat')):
        raise FileNotFoundError

    with shelve.open(os.path.join(save_path, save_file), 'r') as data_file:
        player_index = data_file['player_index']
        entities = data_file['entities']
        game_map = data_file['game_map']
        message_log = data_file['message_log']
        game_state = data_file['game_state']
        priority_queue = data_file['priority_queue']
        global_variables = data_file['global_variables']
        world = data_file['world']

    player = entities[player_index]

    return player, entities, game_map, message_log, game_state, priority_queue, global_variables, world