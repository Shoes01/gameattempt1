class Camera:
    """
    A place to store all the camera information.
    """
    def __init__(self, w, h, player_x, player_y, game_map_width, game_map_height):
        self.w = w                              # Camera width.
        self.h = h                              # Camera height.

        self.x = player_x - int(self.w / 2) - 1 # Leftmost camera x coordinate.
        self.y = player_y - int(self.h / 2) - 1 # Toptmost camera y coordinate.
        self.x2 = self.x + self.w               # Rightmost camera x coordinate.
        self.y2 = self.y + self.h               # Bottommost camera y coordinate.
        self.max_x = game_map_width - self.w    # Maximum x coordinate the camera can have.
        self.max_y = game_map_height - self.h   # Maximum y coordinate the camera can have.
        self.min_x = 0                          # Minimum x coordinate the camera can have.
        self.min_y = 0                          # Minimum y coordinate the camera can have.

        self.keep_inside()



    def move_to(self, x, y):
        # Move the camera to a specific coordinate.
        self.x = x
        self.y = y
        self.keep_inside()
    
    def move(self, dx, dy):
        # Move the camera by dx and dy. TODO: Only if the player is in the center already.
        self.x += dx
        self.y += dy
        self.keep_inside()

    def keep_inside(self):
        # Ensure the camera does not see outside the game map.
        if self.x < self.min_x: self.x = self.min_x
        if self.y < self.min_y: self.y = self.min_y
        if self.x > self.max_x: self.x = self.max_x
        if self.y > self.max_y: self.y = self.max_y

        # Chance the x2, y2 to reflect new x, y.    
        self.x2 = self.x + self.w
        self.y2 = self.y + self.h
    
    def absolute_center(self):
        # Return the center coordinate of the camera.
        x = self.x + int(self.w / 2) + 1
        y = self.y + int(self.h / 2) + 1

        return x, y

