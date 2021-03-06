import tcod as libtcod

from entity import get_blocking_entities_at_location
from game_messages import Message


def heal(*args, **kwargs):
    entity = args[0]
    amount = kwargs.get('amount')

    results = []

    if entity.fighter.hp == entity.fighter.max_hp:
        results.append({'consumed': False, 'message': Message('You are already at full health', libtcod.yellow)})
    else:
        entity.fighter.heal(amount)
        results.append({'consumed': True, 'message': Message('Your wounds start to feel better!', libtcod.green)})

    return results

def catch(*args, **kwargs):
    """
    This item is thrown at a target entity. If the target entity is eligible, the target entity caught.
    """
    thrower_entity = args[0]
    
    power = kwargs.get('power')             # The power of the pokeball.
    item_entity = kwargs.get('item_entity') # The entity information of the thrown item.
    entities = kwargs.get('entities')       # The list of entities.
    fov_map = kwargs.get('fov_map')         # The fov_map, to confirm the target is legal.
    target_x = kwargs.get('target_x')       # The x target.
    target_y = kwargs.get('target_y')       # The y target.

    results = []

    # Ensure that the target is within sight.
    if not libtcod.map_is_in_fov(fov_map, target_x, target_y):
        results.append({'thrown': None, 'message': Message('You cannot target a tile outside your field of view.', libtcod.yellow)})
        return results
    
    if not item_entity.item.caught_entity:
        # Pokeball is empty. Catch something!
        for entity in entities:
            if entity.x == target_x and entity.y == target_y and entity.ai: # The entity is at the target, and it has an AI.

                if entity.fighter.hp > power: # The pokeball is not strong enough.
                    results.append({'thrown': item_entity,
                                        'target_xy': (target_x, target_y),
                                        'message': Message('The {0} has too much health!'.format(entity.name.capitalize()), libtcod.red),
                                        'catch': None})
                    break

                elif entity.fighter.hp <= power: # The pokeball catches the entity!
                    results.append({'thrown': item_entity,
                                        'target_xy': (target_x, target_y),
                                        'message': Message('{0} has captured the {1}!'.format(thrower_entity.name.capitalize(), entity.name.capitalize()), libtcod.green),
                                        'catch': entity})
                    item_entity.item.caught_entity = entity
                    item_entity.item.swap_messages()
                    item_entity.item.use_function = release # The pokeball can no longer catch things. It can only release things now.
                    break

        else:
            results.append({'thrown': item_entity, 
                                'target_xy': (target_x, target_y), 
                                'message': Message('{0} throws the ball. It lands on the ground.'.format(thrower_entity.name.capitalize()), libtcod.white),
                                'catch': None})

    return results

def release(*args, **kwargs):
    """
    This item is thrown at a target tile. If the tile is eligible, the contained entity is released.
    """
    thrower_entity = args[0]
    
    item_entity = kwargs.get('item_entity') # The entity information of the thrown item.
    entities = kwargs.get('entities')       # The list of entities.
    fov_map = kwargs.get('fov_map')         # The fov_map, to confirm the target is legal.
    target_x = kwargs.get('target_x')       # The x target.
    target_y = kwargs.get('target_y')       # The y target.

    results = []

    # Ensure that the target is within sight.
    if not libtcod.map_is_in_fov(fov_map, target_x, target_y):
        results.append({'thrown': None, 'message': Message('You cannot target a tile outside your field of view.', libtcod.yellow)})
        return results

    if item_entity.item.caught_entity:        
        if get_blocking_entities_at_location(entities, target_x, target_y): # Can't release the pokemon at a blocked tile.
            results.append({'thrown': None, 
                                'message': Message('You cannot release {0} at this location.'.format(item_entity.item.caught_entity.name.capitalize()), libtcod.yellow)})
        else: # You can throw here, yay!
            results.append({'thrown': item_entity, 
                                'target_xy': (target_x, target_y), 
                                'message': Message('{0} releases his {1}!'.format(thrower_entity.name.capitalize(), item_entity.item.caught_entity.name.capitalize()), libtcod.green),
                                'release': item_entity.item.caught_entity})
            item_entity.item.caught_entity = None # The pokeball has nothing in it anymore!
            item_entity.item.swap_messages()
            item_entity.item.use_function = catch # The pokeball can now catch things.

    return results

def materia(*args, **kwargs):
    """
    Placeholder function.
    """
    owner_entity = args[0]

    materia_type = kwargs.get('type')
    materia_level = kwargs.get('level')
    
    results = []

    results.append({'message': Message('{0} looks at their {1} Materia. It is level {2}.'.format(owner_entity.name.capitalize(), materia_type.capitalize(), str(materia_level)), libtcod.yellow)})

    return results