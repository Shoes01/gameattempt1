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
        # TODO: Add char and color to the cursor class

    def move(self, dx, dy):
        # TODO: Add relevant code to ensure the cursor doesn't leave the camera
        self.x += dx
        self.y += dy
