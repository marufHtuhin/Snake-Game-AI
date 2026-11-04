from collections import deque

DIRECTIONS = {
    "UP": (0, -1),
    "DOWN": (0, 1),
    "LEFT": (-1, 0),
    "RIGHT": (1, 0),
}
OPPOSITE = {"UP": "DOWN", "DOWN": "UP", "LEFT": "RIGHT", "RIGHT": "LEFT"}

class Snake:
    def __init__(self, cols, rows):
        cx, cy = cols // 2, rows // 2
        self.body = deque([(cx, cy), (cx - 1, cy), (cx - 2, cy)])
        self.direction = "RIGHT"
        self.grow_pending = 0

    @property
    def head(self):
        return self.body[0]

    def set_direction(self, direction):
        if direction in DIRECTIONS and direction != OPPOSITE[self.direction]:
            self.direction = direction

    def next_head(self, direction=None):
        dx, dy = DIRECTIONS[direction or self.direction]
        return (self.head[0] + dx, self.head[1] + dy)

    def move(self, direction=None):
        if direction:
            self.set_direction(direction)
        new_head = self.next_head()
        self.body.appendleft(new_head)
        if self.grow_pending:
            self.grow_pending -= 1
        else:
            self.body.pop()

    def grow(self):
        self.grow_pending += 1
