import heapq

class PriorityQueue:
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

    def get_ID(self):        
        return heapq.heappop(self.queue)[1]

    def size(self):
        return len(self.queue)