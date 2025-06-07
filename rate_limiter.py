import time

class RateLimiter:
    def __init__(self, max_requests, interval):
        self.max_requests = max_requests
        self.interval = interval
        self.request_times = []

    def allow_request(self):
        current_time = time.time()
        self.request_times = [t for t in self.request_times if current_time - t < self.interval]
        if len(self.request_times) >= self.max_requests:
            return False
        self.request_times.append(current_time)
        return True