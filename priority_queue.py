import heapq

class PriorityQueue:
    def __init__(self):
        self.ticker = 0
        self.queue = []
    
    def tick(self):
        self.ticker = self.ticker + 1
        return self.ticker

    def empty(self):
        return len(self.queue) == 0

    def peek(self):
        return self.queue[0]

    def put(self, action_points, ID):
        heapq.heappush(self.queue, (self.ticker + action_points, ID))

    def get_ID(self):
        return heapq.heappop(self.queue)[1]
