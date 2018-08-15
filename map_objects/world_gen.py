from opensimplex import OpenSimplex

class World:
    """
    The whole world will be generated from a seed using noise.
    Noise layers will be used to determine biomes. A layer could be a combination of many noise frequencies.
        1) A temperature layer will determine cold - hot. 
        2) A moisture layer will determine sparse - lush.
        This creates 9 biomes.
        
        The temperature layer will determine the ground tile of the biome. 
        The moisture layer will determine the path blocking entities and the path/sight blocking entities.
        Together, they will determine the inhabitants and the rare structures.



                                Floor types             Small path blockers             Large path/sight blockers           Inhabitants             Rare structure
        Cold/Sparse:            Ice, rock,              Boulder                         
                                packed snow

        Cold/Regular:           

        Cold/Lush:

        Normal/Sparse:

        Normal/Regular:         Grass, dirt             Shrubs, small trees             Large trees                                                 Village

        Normal/Lush:

        Hot/Sparse:

        Hot/Regular:            Sand, dirt

        Hot/Lush:
    """
    def __init__(self, width, height, seeds):
        self.width = width
        self.height = height
        self.seeds = seeds                                 # There are 6 usable seeds.
        self.layers = self.gen_noise_layers()              # This will contain 3 lists. For layers[n][x][y], n is the layer number, x and y are the (x, y) coordinates.

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
    
    def biome_tile_type_decider(self, layer_number, x, y):
        """
        Biome layer 0 will represent vegetation.
        Given the noise level of an (x, y) coordinate of a noise layer, the biome is returned.

        Combine many biome layers to decide the final biome. 
        For example, vegetation + danger would give "scary forests" or "benign fields".

        For testing, there is only one biome layer with a single biome.
        """
        noise_level = self.layers[layer_number][x][y]

        if layer_number == 0: # Vegetation noise layer.
            if noise_level < 0.2:
                return 'dirt'
            elif noise_level < 0.6:
                return 'grass'
            elif noise_level < 0.8:
                return 'tall_grass'
            else:
                return 'shrub'

        return 'nothing'