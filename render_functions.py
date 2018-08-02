import libtcodpy as libtcod


def render_all(con, entities, game_map, fov_map, fov_recompute, screen_width, screen_height, colors):
    # Draw all the tiles in the game map
    if fov_recompute:
        for y in range(game_map.height):
            for x in range(game_map.width):
                tile_type = game_map.tiles[x][y].tile_type
                visible = libtcod.map_is_in_fov(fov_map, x, y)
                
                if visible:
                    if tile_type == 'dirt':
                        libtcod.console_set_char_background(con, x, y, colors.get('light_dirt'), libtcod.BKGND_SET)
                    else: #Assume everything else is grass
                        libtcod.console_set_char_background(con, x, y, colors.get('light_grass'), libtcod.BKGND_SET)
                    game_map.tiles[x][y].explored = True
                elif game_map.tiles[x][y].explored:
                    if tile_type == 'dirt':
                        libtcod.console_set_char_background(con, x, y, colors.get('dark_dirt'), libtcod.BKGND_SET)
                    else: #Assume everything else is grass
                        libtcod.console_set_char_background(con, x, y, colors.get('dark_grass'), libtcod.BKGND_SET)
                
    # Draw all entities in the list
    for entity in entities:
        draw_entity(con, entity, fov_map)

    libtcod.console_blit(con, 0, 0, screen_width, screen_height, 0, 0, 0)


def clear_all(con, entities):
    for entity in entities:
        clear_entity(con, entity)

def draw_entity(con, entity, fov_map):
    if libtcod.map_is_in_fov(fov_map, entity.x, entity.y):
        libtcod.console_set_default_foreground(con, entity.color)
        libtcod.console_put_char(con, entity.x, entity.y, entity.char, libtcod.BKGND_NONE)


def clear_entity(con, entity):
    # erase the character that represents this object
    libtcod.console_put_char(con, entity.x, entity.y, ' ', libtcod.BKGND_NONE)