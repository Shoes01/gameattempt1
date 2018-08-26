class Cursor:
    """
    When the game is in the LOOK state, a yellow X apears and is moveable.
    The game displays what is below the cursor.

    TODO: All relevant cursor code should pass through here, but may not be written here.

    Maybe this isn't necessary?

    """
    __init__(self, x, y):
        self.x = x
        self.y = y

    def move(self, dx, dy):
        # TODO: Add relevant code to ensure the cursor doesn't leave the camera
        self.x += dx
        self.y += dy
