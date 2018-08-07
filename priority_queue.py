import heapq

class PriorityQueue:
    def __init__(self):
        self.ticker = 0
        self.queue = [] #made of (ticker + action points, ID)
    
    def tick(self):
        self.ticker = self.ticker + 1
        return self.ticker

    def untick(self):
        self.ticker = self.ticker - 1        

    def empty(self):
        return len(self.queue) == 0

    def peek(self):
        return self.queue[0][0]

    def put(self, action_points, ID):
        self.ticker += 1
        heapq.heappush(self.queue, (self.ticker + action_points, ID))

    def get_ID(self):
        return heapq.heappop(self.queue)[1]

    def match(self):
        if self.ticker == self.queue[0]:
            return True
        else:
            return False

    def size(self):
        return len(self.queue)
