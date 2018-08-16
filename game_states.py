from enum import Enum


class GameStates(Enum):
    PLAYERS_TURN = 1
    ENEMY_TURN = 2      # Actually just not-player's turn.
    PLAYER_DEAD = 3
    SHOW_INVENTORY = 4
    DROP_INVENTORY = 5
    TARGETING = 6
    LEVEL_UP = 7
    CHARACTER_SCREEN = 8