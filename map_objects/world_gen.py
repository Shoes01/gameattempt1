from opensimplex import OpenSimplex

class World:
    """
    The World information is stored here. GameMap then translates it into tiles and entities.
    Some noise layers will be used to determine biomes.
    Some noise layers will determine special tile placement, such as trees.
    Some noise layers will determine entity placement?

    TODO: The World should also include some biomes that are not noise generated, such as towns or adventure-sites. These towns should be connected by roads
    """
    def __init__(self, width, height, seeds):
        self.width = width
        self.height = height
        self.seeds = seeds                      # There are 6 usable seeds.
        self.layers = self.gen_noise_layers()   # This will contain 3 lists. For layers[n][x][y], n is the layer number, x and y are the (x, y) coordinates.

    def gen_noise_layers(self):
        """
        Generate noise layers from the seeds.
        """
        # Initialize the layers.
        self.layers = [[[y for y in range(self.height)] for x in range(self.width)] for n in range(len(self.seeds))]

        for n in range(len(self.seeds)):
            gen = OpenSimplex(seed=self.seeds[n]) # Plug the nth seed into the generator.

            for y in range(self.height):
                for x in range(self.width):
                    nx = x/self.width - 0.5     # TODO: Not sure what this is...
                    ny = y/self.height - 0.5    # TODO: Not sure what this is...

                    self.layers[n][x][y] = gen.noise2d(nx, ny) / 2 + 0.5
        
        return self.layers
    
    def get_biome_at_xy(self, x, y):
        """
        Given the noise level of an (x, y) coordinate of a noise layer, the biome is returned.
        Biome layer 0 will represent the Fire-Water axis.
        Biome layer 1 will represent the Earth-Wind axis.

        Combine many biome layers to decide the final biome.

        TODO: Fill out biomes more.
        """
        fire_water_axis = self.layers[0][x][y]
        earth_wind_axis = self.layers[1][x][y]

        if fire_water_axis < 0.33:
            if earth_wind_axis < 0.33: return "fire_earth"
            elif earth_wind_axis < 0.66: return "fire"
            else: return "fire_wind"
        
        elif fire_water_axis < 0.66:
            if earth_wind_axis < 0.33: return "earth"
            elif earth_wind_axis < 0.66: return "normal"
            else: return "wind"

        else:
            if earth_wind_axis < 0.33: return "water_earth"
            elif earth_wind_axis < 0.66: return "water"
            else: return "water_wind"

        return 'nothing' # For when things get more complicated...