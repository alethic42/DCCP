# systems/pathfinding.py

from collections import deque

from settings import (
    GRID_COLS,
    GRID_ROWS,
    EMPTY,
    PATH,
    START,
    CASTLE,
    TOWER,
    OBSTACLE,
)


class PathFinder:
    def __init__(self, grid):
        """
        grid는 2차원 리스트 형태를 가정한다.
        예:
        grid[row][col]
        """
        self.grid = grid
        self.rows = GRID_ROWS
        self.cols = GRID_COLS

    def in_bounds(self, col, row):
        return 0 <= col < self.cols and 0 <= row < self.rows

    def is_walkable(self, col, row):
        if not self.in_bounds(col, row):
            return False

        cell = self.grid[row][col]

        return cell in (EMPTY, START, CASTLE)

    def get_neighbors(self, col, row):
        directions = [
            (1, 0),
            (-1, 0),
            (0, 1),
            (0, -1),
        ]

        neighbors = []

        for dc, dr in directions:
            next_col = col + dc
            next_row = row + dr

            if self.is_walkable(next_col, next_row):
                neighbors.append((next_col, next_row))

        return neighbors

    def find_path(self, start, goal):
        """
        BFS로 start에서 goal까지의 최단 경로를 찾는다.

        start, goal 형식:
        (col, row)

        반환값:
        [(col, row), (col, row), ...]
        경로가 없으면 빈 리스트 []
        """
        queue = deque()
        queue.append(start)

        came_from = {
            start: None
        }

        while queue:
            current = queue.popleft()

            if current == goal:
                break

            for neighbor in self.get_neighbors(*current):
                if neighbor not in came_from:
                    came_from[neighbor] = current
                    queue.append(neighbor)

        if goal not in came_from:
            return []

        return self.reconstruct_path(came_from, start, goal)

    def reconstruct_path(self, came_from, start, goal):
        path = []
        current = goal

        while current is not None:
            path.append(current)
            current = came_from[current]

        path.reverse()

        if path[0] != start:
            return []

        return path

    def can_place_tower(self, col, row, start, goal):
        """
        해당 칸에 타워를 놓아도 길이 막히지 않는지 검사한다.
        """
        if not self.in_bounds(col, row):
            return False

        if self.grid[row][col] != EMPTY:
            return False

        original = self.grid[row][col]
        self.grid[row][col] = TOWER

        path = self.find_path(start, goal)

        self.grid[row][col] = original

        return len(path) > 0

    def update_grid(self, new_grid):
        """
        외부에서 맵이 바뀌었을 때 PathFinder 내부 grid 참조를 갱신한다.
        """
        self.grid = new_grid