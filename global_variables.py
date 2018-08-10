class GlobalVariables:
    def __init__(self):
        self.ID = 0
    
    def get_new_ID(self):
        self.ID += 1
        return self.ID