class Item:
    def __init__(self, use_function=None, targeting=False, targeting_message=None, caught_entity=None, can_contain=False, **kwargs):
        self.use_function = use_function            # What the item does (see item_functions.py)
        self.targeting = targeting                  # If the item has to target something before being used.
        self.targeting_message = targeting_message  # The message displayed to the player when targeting.
        self.function_kwargs = kwargs               # The keywords informing the function of this item. Indefinite length.
        self.caught_entity = caught_entity          # Which entity is inside the item.
        self.can_contain = can_contain              # If the item can hold things.