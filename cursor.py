import tcod as libtcod

class Cursor:
    """
    When the game is in the LOOK state, a yellow X apears and is moveable.
    The game displays what is below the cursor.

    TODO: All relevant cursor code should pass through here, but may not be written here.

    Maybe this isn't necessary?

    """
    def __init__(self):
        # Doesn't matter what the x,y start as, because the cursor always spawns on the player.
        self.x = -1
        self.y = -1
        self.char = 'X'
        self.color = libtcod.yellow

    def move(self, dx, dy, camera_width, camera_height, camera_x, camera_y):
        # TODO: Add relevant code to ensure the cursor doesn't leave the camera
        self.x += dx
        self.y += dy

        if self.x > camera_width + camera_x - 1: self.x = camera_width + camera_x - 1
        if self.y > camera_height + camera_y - 1: self.y = camera_height + camera_y - 1
        if self.x < 0 + camera_x: self.x = 0 + camera_x
        if self.y < 0 + camera_y: self.y = 0 + camera_y
