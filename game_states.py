from enum import Enum


class GameStates(Enum):
    PLAYERS_TURN = 1
    ENEMY_TURN = 2
    PLAYER_DEAD = 3
    NEUTRAL_TURN = 4
    SHOW_INVENTORY = 5
    DROP_INVENTORY = 6
    TARGETING = 7