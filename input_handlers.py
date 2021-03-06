import tcod as libtcod

from game_states import GameStates


def handle_keys(key, game_state):
    """
    Check the Game State, and then return the appropriate action given the key.
    """
    if game_state == GameStates.PLAYERS_TURN:
        return handle_player_turn_keys(key)
    elif game_state == GameStates.PLAYER_DEAD:
        return handle_player_dead_keys(key)
    elif game_state == GameStates.TARGETING:
        return handle_targeting_keys(key)
    elif game_state in (GameStates.SHOW_INVENTORY, GameStates.DROP_INVENTORY):
        return handle_inventory_keys(key)
    elif game_state == GameStates.LEVEL_UP:
        return handle_level_up_menu(key)
    elif game_state == GameStates.CHARACTER_SCREEN:
        return handle_character_screen(key)
    elif game_state == GameStates.MATERIA_SCREEN:
        return handle_materia_extration_menu(key)
    elif game_state == GameStates.LOOK:
        return handle_look(key)

    return {}

def handle_mouse(mouse):
    (x, y) = (mouse.cx, mouse.cy)

    if mouse.lbutton_pressed:
        return {'left_click': (x, y)}
    elif mouse.rbutton_pressed:
        return {'right_click': (x, y)}

    return {}

def generic_movement(key):
    key_char = chr(key.c)

    if key.vk == libtcod.KEY_UP or key_char == 'k' or key.vk == libtcod.KEY_KP8:
        return {'move': (0, -1)}
    elif key.vk == libtcod.KEY_DOWN or key_char == 'j' or key.vk == libtcod.KEY_KP2:
        return {'move': (0, 1)}
    elif key.vk == libtcod.KEY_LEFT or key_char == 'h' or key.vk == libtcod.KEY_KP4:
        return {'move': (-1, 0)}
    elif key.vk == libtcod.KEY_RIGHT or key_char == 'l' or key.vk == libtcod.KEY_KP6:
        return {'move': (1, 0)}
    elif key_char == 'y' or key.vk == libtcod.KEY_KP7:
        return {'move': (-1, -1)}
    elif key_char == 'u' or key.vk == libtcod.KEY_KP9:
        return {'move': (1, -1)}
    elif key_char == 'b' or key.vk == libtcod.KEY_KP1:
        return {'move': (-1, 1)}
    elif key_char == 'n' or key.vk == libtcod.KEY_KP3:
        return {'move': (1, 1)}
    elif key_char == '.' or key.vk == libtcod.KEY_KP5:
        return {'wait': True}
    
    return {}

def handle_player_turn_keys(key):
    key_char = chr(key.c)

    result = {}

    result = generic_movement(key)

    if key_char == 'g':
        result =  {'pickup': True}

    elif key_char == 'i':
        result =  {'show_inventory': True}

    elif key_char == 'd':
        result =  {'drop_inventory': True}

    elif key_char == 'c':
        result =  {'show_character_screen': True}

    elif key_char == 'm':
        result =  {'show_extract_materia_menu': True}

    elif key_char == 'x':
        result =  {'look': True}

    if key.vk == libtcod.KEY_ENTER and key.lalt:
        # Alt+Enter: toggle full screen
        result =  {'fullscreen': True}

    elif key.vk == libtcod.KEY_ESCAPE:
        # Exit the game
        result =  {'exit': True}

    # No key was pressed
    return result

def handle_player_dead_keys(key):
    key_char = chr(key.c)

    if key_char == 'i':
        return {'show_inventory': True}

    if key.vk == libtcod.KEY_ENTER and key.lalt:
        # Alt+Enter: toggle full screen
        return {'fullscreen': True}
    elif key.vk == libtcod.KEY_ESCAPE:
        # Exit the menu
        return {'exit': True}

    # No key was pressed
    return {}

def handle_targeting_keys(key):
    result = {}

    result = generic_movement(key)

    if key.vk == libtcod.KEY_ENTER or key.vk == libtcod.KEY_KPENTER:
        result = {'select': True}

    if key.vk == libtcod.KEY_ESCAPE:
        result = {'exit': True}
    
    return result

def handle_inventory_keys(key):
    index = key.c - ord('a')

    if index >= 0:
        return {'inventory_index': index}

    if key.vk == libtcod.KEY_ENTER and key.lalt:
        # Alt+Enter: toggle full screen
        return {'fullscreen': True}
    elif key.vk == libtcod.KEY_ESCAPE:
        # Exit the menu
        return {'exit': True}

    return {}

def handle_main_menu(key):
    key_char = chr(key.c)

    if key_char == 'a':
        return {'new_game': True}
    elif key_char == 'b':
        return {'load_game': True}
    elif key_char == 'c' or  key.vk == libtcod.KEY_ESCAPE:
        return {'exit': True}

    return {}

def handle_level_up_menu(key):
    key_char = chr(key.c)

    if key_char == 'a':
        return {'level_up': 'hp'}
    elif key_char == 'b':
        return {'level_up': 'str'}
    elif key_char == 'c':
        return {'level_up': 'def'}

    return {}

def handle_character_screen(key):
    if key.vk == libtcod.KEY_ESCAPE:
        return {'exit': True}

    return {}

def handle_materia_extration_menu(key):
    if key.vk == libtcod.KEY_ESCAPE:
        return {'exit': True}
    
    index = key.c - ord('a')
    if index >= 0:
        return {'extraction_index': index}
    
    return {}

def handle_look(key):
    result = {}

    result = generic_movement(key)
    
    if key.vk == libtcod.KEY_ESCAPE:
        result = {'exit': True}

    return result