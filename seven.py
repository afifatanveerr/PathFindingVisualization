import matplotlib.pyplot as plt
import numpy as np
import time
import heapq
from collections import deque
import tkinter as tk
from tkinter import simpledialog

ROWS = 10
COLS = 10

EMPTY = 0
WALL = -1
START = 1
TARGET = 2
FRONTIER = 3
EXPLORED = 4
PATH = 5

DELAY = 0.15
MOVES = [
    (-1, 0),
    (0, 1),
    (1, 0),
    (1, 1),
    (0, -1),
    (-1, -1)
]

def create_grid():
    grid = np.zeros((ROWS, COLS))
    for i in range(1, 7):
        grid[i][5] = WALL
    start = (4, 7)
    target = (6, 1)
    grid[start] = START
    grid[target] = TARGET
    return grid, start, target

def draw(grid, title="Search", step=0):
    plt.clf()
    colors = {
        EMPTY: 'white',
        WALL: 'black',
        START: 'limegreen',
        TARGET: 'gold',
        FRONTIER: 'cyan',
        EXPLORED: 'orange',
        PATH: 'magenta'
    }
    for i in range(ROWS):
        for j in range(COLS):
            val = grid[i][j]
            plt.gca().add_patch(
                plt.Rectangle((j, i), 1, 1, color=colors[val], ec='gray')
            )
            if val == WALL:
                plt.text(j + 0.5, i + 0.5, "-1", ha='center', va='center', color='white')
            elif val == START:
                plt.text(j + 0.5, i + 0.5, "S", ha='center', va='center', color='black')
            elif val == TARGET:
                plt.text(j + 0.5, i + 0.5, "T", ha='center', va='center', color='black')
            else:
                plt.text(j + 0.5, i + 0.5, "0", ha='center', va='center', color='black')

    plt.xlim(0, COLS)
    plt.ylim(ROWS, 0)
    plt.xticks(np.arange(0, COLS, 1))
    plt.yticks(np.arange(0, ROWS, 1))
    plt.grid(True, which='both', color='lightgray', linestyle='-', linewidth=0.5)
    plt.title(f"{title} | Step: {step}")

    legend_elements = [
        plt.Rectangle((0, 0), 1, 1, color=colors[EMPTY], label='Empty'),
        plt.Rectangle((0, 0), 1, 1, color=colors[WALL], label='Wall'),
        plt.Rectangle((0, 0), 1, 1, color=colors[START], label='Start'),
        plt.Rectangle((0, 0), 1, 1, color=colors[TARGET], label='Target'),
        plt.Rectangle((0, 0), 1, 1, color=colors[FRONTIER], label='Frontier'),
        plt.Rectangle((0, 0), 1, 1, color=colors[EXPLORED], label='Explored'),
        plt.Rectangle((0, 0), 1, 1, color=colors[PATH], label='Path')
    ]
    plt.legend(handles=legend_elements, loc='upper center', bbox_to_anchor=(0.5, -0.1), ncol=4)
    plt.pause(DELAY)

def get_neighbors(grid, node):
    result = []
    for move in MOVES:
        r = node[0] + move[0]
        c = node[1] + move[1]
        if 0 <= r < ROWS and 0 <= c < COLS:
            if grid[r][c] != WALL:
                result.append((r, c))
    return result

def reconstruct_path(grid, parent, start, target):
    node = target
    while node in parent:
        node = parent[node]
        if node != start:
            grid[node] = PATH
        draw(grid, "Final Path")

def bfs(grid, start, target):
    queue = deque([start])
    visited = set([start])
    parent = {}
    step = 0
    while queue:
        current = queue.popleft()
        if current == target:
            reconstruct_path(grid, parent, start, target)
            return
        if current != start:
            grid[current] = EXPLORED
        for neighbor in get_neighbors(grid, current):
            if neighbor not in visited:
                visited.add(neighbor)
                parent[neighbor] = current
                queue.append(neighbor)
                if grid[neighbor] == EMPTY:
                    grid[neighbor] = FRONTIER
        step += 1
        draw(grid, "BFS", step)

def dfs(grid, start, target):
    stack = [start]
    visited = set()
    parent = {}
    step = 0
    while stack:
        current = stack.pop()
        if current == target:
            reconstruct_path(grid, parent, start, target)
            return
        if current not in visited:
            visited.add(current)
            if current != start:
                grid[current] = EXPLORED
            for neighbor in reversed(get_neighbors(grid, current)):
                if neighbor not in visited:
                    parent[neighbor] = current
                    stack.append(neighbor)
                    if grid[neighbor] == EMPTY:
                        grid[neighbor] = FRONTIER
        step += 1
        draw(grid, "DFS", step)

def ucs(grid, start, target):
    pq = [(0, start)]
    parent = {}
    cost = {start: 0}
    step = 0
    while pq:
        current_cost, current = heapq.heappop(pq)
        if current == target:
            reconstruct_path(grid, parent, start, target)
            return
        if current != start:
            grid[current] = EXPLORED
        for neighbor in get_neighbors(grid, current):
            new_cost = current_cost + 1
            if neighbor not in cost or new_cost < cost[neighbor]:
                cost[neighbor] = new_cost
                parent[neighbor] = current
                heapq.heappush(pq, (new_cost, neighbor))
                if grid[neighbor] == EMPTY:
                    grid[neighbor] = FRONTIER
        step += 1
        draw(grid, "UCS", step)

def dls(grid, start, target, limit):
    stack = [(start, 0)]
    parent = {}
    visited = set()
    step = 0
    while stack:
        current, depth = stack.pop()
        if current == target:
            reconstruct_path(grid, parent, start, target)
            print("Target has been found")
            return True
        if depth <= limit and current not in visited:
            visited.add(current)
            if current != start:
                grid[current] = EXPLORED
            for neighbor in reversed(get_neighbors(grid, current)):
                if neighbor not in visited:
                    parent[neighbor] = current
                    stack.append((neighbor, depth + 1))
                    if grid[neighbor] == EMPTY:
                        grid[neighbor] = FRONTIER
        step += 1
        draw(grid, f"DLS Limit={limit}", step)
    print("Target not found within depth limit")
    return False

def iddfs(grid, start, target):
    max_depth = ROWS * COLS
    for limit in range(max_depth):
        temp_grid, start, target = create_grid()
        found = dls(temp_grid, start, target, limit)
        if found:
            return

def bidirectional(grid, start, target):
    q_start = deque([start])
    q_target = deque([target])
    parent_start = {}
    parent_target = {}
    visited_start = {start}
    visited_target = {target}
    meet = None
    step = 0
    while q_start and q_target:
        current_start = q_start.popleft()
        if current_start != start:
            grid[current_start] = EXPLORED
        for neighbor in get_neighbors(grid, current_start):
            if neighbor not in visited_start:
                visited_start.add(neighbor)
                parent_start[neighbor] = current_start
                q_start.append(neighbor)
                if grid[neighbor] == EMPTY:
                    grid[neighbor] = FRONTIER
                if neighbor in visited_target:
                    meet = neighbor
                    break
        if meet:
            break
        current_target = q_target.popleft()
        for neighbor in get_neighbors(grid, current_target):
            if neighbor not in visited_target:
                visited_target.add(neighbor)
                parent_target[neighbor] = current_target
                q_target.append(neighbor)
                if neighbor in visited_start:
                    meet = neighbor
                    break
        step += 1
        draw(grid, "Bidirectional", step)
        if meet:
            break
    if meet:
        node = meet
        while node in parent_start:
            node = parent_start[node]
            if node != start:
                grid[node] = PATH
            draw(grid, "Bidirectional Path", step)
        node = meet
        while node in parent_target:
            node = parent_target[node]
            if node != target:
                grid[node] = PATH
            draw(grid, "Bidirectional Path", step)

def select_algorithm():
    root = tk.Tk()
    root.withdraw()
    algorithms = ["BFS", "DFS", "UCS", "DLS", "IDDFS", "Bidirectional"]
    choice = simpledialog.askinteger("Algorithm", "Select Algorithm:\n1. BFS\n2. DFS\n3. UCS\n4. DLS\n5. IDDFS\n6. Bidirectional")
    return choice

def main():
    while True:
        choice = select_algorithm()
        if not choice:
            break
        plt.figure(figsize=(8, 8))
        grid, start, target = create_grid()
        draw(grid, "Original Grid")
        time.sleep(1)
        if choice == 1:
            bfs(grid, start, target)
        elif choice == 2:
            dfs(grid, start, target)
        elif choice == 3:
            ucs(grid, start, target)
        elif choice == 4:
            limit = simpledialog.askinteger("DLS", "Enter depth limit:")
            if limit is None:
                continue
            found = dls(grid, start, target, limit)
            if not found:
                print("Try higher depth")
        elif choice == 5:
            iddfs(grid, start, target)
        elif choice == 6:
            bidirectional(grid, start, target)
        plt.show()

if __name__ == "__main__":
    main()
