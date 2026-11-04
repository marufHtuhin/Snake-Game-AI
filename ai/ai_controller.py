from collections import deque
from .astar import astar
from snake import DIRECTIONS, OPPOSITE


class AIController:
    """A* food seeking, validated by simulating the snake following the path.

    Strategy (in order):
      1. A* to food; take it only if, after eating, the snake can still reach
         its own tail (so it is never trapped in a closed pocket).
      2. Otherwise follow A* to the tail to stall safely until food is reachable.
      3. Otherwise take the legal move leaving the largest open area.
    """

    def __init__(self, cols, rows):
        self.cols = cols
        self.rows = rows
        self.last_status = "Searching for food"
        self.stall = 0
        self._food = None
        self.path = []  # planned route (used for on-screen visualization)

    def _valid(self, c):
        return 0 <= c[0] < self.cols and 0 <= c[1] < self.rows

    def _area(self, start, blocked):
        blocked = set(blocked)
        seen, q = {start}, deque([start])
        while q:
            x, y = q.popleft()
            for dx, dy in DIRECTIONS.values():
                n = (x + dx, y + dy)
                if self._valid(n) and n not in blocked and n not in seen:
                    seen.add(n)
                    q.append(n)
        return len(seen)

    def _safe_after_eating(self, path, body):
        """Simulate following `path` to food, then check the tail stays reachable."""
        L = len(body)
        virtual = list(reversed(path)) + body[: max(0, L + 1 - len(path))]
        virtual = virtual[: L + 1]
        head, tail = virtual[0], virtual[-1]
        return astar(head, tail, set(virtual[1:-1]), self.cols, self.rows) is not None

    def choose_direction(self, snake, food):
        body = list(snake.body)
        head = snake.head
        self.path = []

        # 1) A* to food, validated by simulation
        path = astar(head, food, set(body[:-1]), self.cols, self.rows)
        # After a long stall, accept a looser safety check (enough open space)
        loose = path and self.stall > 40 and self._area(path[0], body[:-1]) >= len(body) + 5
        if food != self._food:
            self._food, self.stall = food, 0
        if path and (self._safe_after_eating(path, body) or loose):
            self.path = path
            self.last_status = f"A* -> food ({len(path)} steps)"
            return self._dir(head, path[0])

        # 2) Chase the tail (stalling) via A*
        tail_path = astar(head, body[-1], set(body[1:-1]), self.cols, self.rows)
        if tail_path and len(tail_path) > 1:
            self.stall += 1
            self.path = tail_path
            self.last_status = "Stalling: following tail"
            return self._dir(head, tail_path[0])

        # 3) Fallback: largest reachable area
        options = []
        for name, (dx, dy) in DIRECTIONS.items():
            if name == OPPOSITE[snake.direction]:
                continue
            nxt = (head[0] + dx, head[1] + dy)
            eating = nxt == food
            tail_free = body if eating else body[:-1]
            if not self._valid(nxt) or nxt in tail_free:
                continue
            options.append((self._area(nxt, [nxt] + tail_free[:-1]), name))
        if options:
            self.last_status = "Safe fallback"
            return max(options)[1]
        self.last_status = "No safe move"
        return snake.direction

    @staticmethod
    def _dir(a, b):
        v = (b[0] - a[0], b[1] - a[1])
        return next(n for n, d in DIRECTIONS.items() if d == v)
