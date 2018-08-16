import libtcodpy as libtcod

from enum import Enum
from game_states import GameStates
from menus import character_screen, inventory_menu, level_up_menu


class RenderOrder(Enum):
    CORPSE = 1
    ITEM = 2
    ACTOR = 3

def get_names_under_mouse(mouse, entities, fov_map, camera_x, camera_y):
    (x, y) = (mouse.cx + camera_x, mouse.cy + camera_y)

    names = [entity.name for entity in entities
             if entity.x == x and entity.y == y and libtcod.map_is_in_fov(fov_map, entity.x, entity.y)]
    names = ', '.join(names)

    return names.capitalize()

def render_bar(panel, x, y, total_width, name, value, maximum, bar_color, back_color):
    bar_width = int(float(value) / maximum * total_width)

    libtcod.console_set_default_background(panel, back_color)
    libtcod.console_rect(panel, x, y, total_width, 1, False, libtcod.BKGND_SCREEN)

    libtcod.console_set_default_background(panel, bar_color)
    if bar_width > 0:
        libtcod.console_rect(panel, x, y, bar_width, 1, False, libtcod.BKGND_SCREEN)

    libtcod.console_set_default_foreground(panel, libtcod.white)
    libtcod.console_print_ex(panel, int(x + total_width / 2), y, libtcod.BKGND_NONE, libtcod.CENTER,
                             '{0}: {1}/{2}'.format(name, value, maximum))

def render_all(con, panel, entities, player, game_map, fov_map, fov_recompute, message_log, screen_width, screen_height,
               bar_width, panel_height, panel_y, mouse, colors, game_state, camera_x, camera_y, camera_width, camera_height):
   
    # Draw all the tiles in the game map
    if fov_recompute:
        for y in range(camera_y, camera_y + camera_height):
            for x in range(camera_x, camera_x + camera_width):
                tile_type = game_map.tiles[x][y].tile_type
                visible = libtcod.map_is_in_fov(fov_map, x, y)
                # Decide on color names.
                light_color_name = 'light_' + tile_type
                dark_color_name = 'dark_' + tile_type
                # Convert the map coords to console coords
                console_x = x - camera_x
                console_y = y - camera_y

                # If the player can see it, make it explored and use the light color.
                if visible:
                    game_map.tiles[x][y].explored = True

                    if tile_type == 'nothing':
                        libtcod.console_put_char_ex(con, console_x, console_y, '?', libtcod.blue, libtcod.dark_blue)
                    else:
                        libtcod.console_set_char_background(con, console_x, console_y, colors.get(light_color_name), libtcod.BKGND_SET)
                
                # If I can't see it, but it was explored already, use the dark color.
                elif game_map.tiles[x][y].explored:
                    
                    if tile_type == 'nothing':
                        libtcod.console_put_char_ex(con, console_x, console_y, '?', libtcod.dark_blue, libtcod.black)
                    else:
                        libtcod.console_set_char_background(con, console_x, console_y, colors.get(dark_color_name), libtcod.BKGND_SET)
                # I can neither see it, nor has it been explored. Color it black.
                elif not visible and not game_map.tiles[x][y].explored:
                    if tile_type == 'nothing':
                        libtcod.console_put_char_ex(con, console_x, console_y, '?', libtcod.red, libtcod.dark_red)
                    else:
                        libtcod.console_put_char(con, console_x, console_y, ' ', libtcod.BKGND_NONE)
                        libtcod.console_set_char_background(con, console_x, console_y, libtcod.black, libtcod.BKGND_SET)
                
    entities_in_render_order = sorted(entities, key=lambda x: x.render_order.value)

    # Draw all entities in the list
    for entity in entities_in_render_order:
        if libtcod.map_is_in_fov(fov_map, entity.x, entity.y):
            libtcod.console_set_default_foreground(con, entity.color)
            libtcod.console_put_char(con, entity.x - camera_x, entity.y - camera_y, entity.char, libtcod.BKGND_NONE)

    libtcod.console_blit(con, 0, 0, screen_width, screen_height, 0, 0, 0)

    libtcod.console_set_default_background(panel, libtcod.black)
    libtcod.console_clear(panel)

    # Print the game messages, one line at a time
    y = 1
    for message in message_log.messages:
        libtcod.console_set_default_foreground(panel, message.color)
        libtcod.console_print_ex(panel, message_log.x, y, libtcod.BKGND_NONE, libtcod.LEFT, message.text)
        y += 1

    render_bar(panel, 1, 1, bar_width, 'HP', player.fighter.hp, player.fighter.max_hp,
               libtcod.light_red, libtcod.darker_red)

    libtcod.console_set_default_foreground(panel, libtcod.light_gray)
    libtcod.console_print_ex(panel, 1, 0, libtcod.BKGND_NONE, libtcod.LEFT,
                             get_names_under_mouse(mouse, entities, fov_map, camera_x, camera_y))

    libtcod.console_blit(panel, 0, 0, screen_width, panel_height, 0, 0, panel_y)

    # Show the Inventory screen
    if game_state in (GameStates.SHOW_INVENTORY, GameStates.DROP_INVENTORY):
        if game_state == GameStates.SHOW_INVENTORY:
            inventory_title = 'Press the key next to an item to use it, or Esc to cancel.\n'
        else:
            inventory_title = 'Press the key next to an item to drop it, or Esc to cancel.\n'

        inventory_menu(con, inventory_title, player.inventory, 50, screen_width, screen_height)
    
    # Show the Level Up screen
    elif game_state == GameStates.LEVEL_UP:
        level_up_menu(con, 'Level up! Choose a stat to raise:', player, 40, screen_width, screen_height)

    # Show the Character screen
    elif game_state == GameStates.CHARACTER_SCREEN:
        character_screen(player, 30, 10, screen_width, screen_height)

def clear_all(con, entities, camera_x, camera_y):
    for entity in entities:
        clear_entity(con, entity, camera_x, camera_y)

def clear_entity(con, entity, camera_x, camera_y):
    # erase the character that represents this object
    libtcod.console_put_char(con, entity.x - camera_x, entity.y - camera_y, ' ', libtcod.BKGND_NONE)