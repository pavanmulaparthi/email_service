class IdempotencyStore:
    def __init__(self):
        self.keys = set()

    def exists(self, key):
        return key in self.keys

    def save(self, key):
        self.keys.add(key)