import heapq

DIRECTIONS = [(0, -1), (0, 1), (-1, 0), (1, 0)]

def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def astar(start, goal, blocked, cols, rows):
    """Return a list of cells from start (excluded) to goal, or None."""
    blocked = set(blocked)
    blocked.discard(start)
    blocked.discard(goal)

    frontier = [(heuristic(start, goal), 0, start)]
    came_from = {}
    cost = {start: 0}
    counter = 0

    while frontier:
        _, current_cost, current = heapq.heappop(frontier)
        if current == goal:
            path = []
            while current != start:
                path.append(current)
                current = came_from[current]
            path.reverse()
            return path

        if current_cost != cost.get(current):
            continue

        for dx, dy in DIRECTIONS:
            nxt = (current[0] + dx, current[1] + dy)
            if not (0 <= nxt[0] < cols and 0 <= nxt[1] < rows):
                continue
            if nxt in blocked:
                continue
            new_cost = current_cost + 1
            if new_cost < cost.get(nxt, float("inf")):
                cost[nxt] = new_cost
                came_from[nxt] = current
                counter += 1
                heapq.heappush(
                    frontier,
                    (new_cost + heuristic(nxt, goal), new_cost, nxt)
                )
    return None
