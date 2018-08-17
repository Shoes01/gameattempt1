import heapq

class PriorityQueue:
    """
    The Priorirty Queue keeps track of turn order. Some entities are faster than others,
    and so they get more turns.

    The game starts on the player's turn.
    If the PQ is not empty, and it is enemy turn, it gets the next entity in line.
        * It does not check on the player's turn, because the player doesn't act immediately.
    """

    def __init__(self):
        self.ticker = 0
        self.queue = [] #made of (ticker + action points, ID)
        heapq.heapify(self.queue) # TODO this is untested

    def empty(self):
        return len(self.queue) == 0

    #peek to see the ID of the topmost item (to see if it is alive)
    def peek(self):
        return self.queue[0][1]

    def put(self, action_points, ID):        
        heapq.heappush(self.queue, (self.ticker + action_points, ID))
        self.ticker = self.queue[0][0]

    def put_next(self, ID):
        # This action does not advance the ticker
        if self.empty():
            heapq.heappush(self.queue, (self.ticker + 1, ID))
        else:
            heapq.heappush(self.queue, (self.queue[0][0] + 1, ID))
        self.ticker = self.queue[0][0]

    def get_ID(self):        
        return heapq.heappop(self.queue)[1]

    def size(self):
        return len(self.queue)