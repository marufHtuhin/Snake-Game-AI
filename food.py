import random

class Food:
    def __init__(self, cols, rows):
        self.cols = cols
        self.rows = rows
        self.position = None

    def respawn(self, occupied):
        available = [
            (x, y)
            for x in range(self.cols)
            for y in range(self.rows)
            if (x, y) not in occupied
        ]
        self.position = random.choice(available) if available else None
        return self.position
