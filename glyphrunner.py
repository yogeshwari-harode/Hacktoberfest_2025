#!/usr/bin/env python3
"""
GlyphRunner: Neon Maze
Single-file terminal game (turn-based, ASCII).
Save as glyphrunner.py and run with: python glyphrunner.py

Controls:
  W / w - move up
  S / s - move down
  A / a - move left
  D / d - move right
  Q - quit

Legend:
  @ : player
  # : wall
  . : floor
  * : glyph (collect for points)
  E : enemy (touch = damage)
  P : power-up (heals or shield)
  X : exit to next level
"""

import random
import os
import sys
import time
from copy import deepcopy

# --- Config ---
WIDTH = 21   # must be odd for nicer maze
HEIGHT = 11  # must be odd
NUM_GLYPHS = 6
NUM_ENEMIES = 2
NUM_POWERUPS = 1
MAX_LEVEL = 8
MAX_HEALTH = 5

# --- Utilities ---
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def clamp(n, a, b):
    return max(a, min(b, n))

# --- Maze generation (simple randomized Prim-like) ---
def generate_maze(w, h):
    # w,h should be odd
    maze = [['#' for _ in range(w)] for _ in range(h)]
    start = (1, 1)
    maze[start[1]][start[0]] = '.'
    walls = []
    def add_walls(x, y):
        for dx, dy in [(2,0),(-2,0),(0,2),(0,-2)]:
            nx, ny = x+dx, y+dy
            if 0 < nx < w-1 and 0 < ny < h-1 and maze[ny][nx] == '#':
                walls.append((nx, ny, x, y))
    add_walls(*start)
    while walls:
        idx = random.randrange(len(walls))
        wx, wy, px, py = walls.pop(idx)
        if maze[wy][wx] == '#':
            # find the cell opposite to wall relative to parent
            ox, oy = wx + (wx - px), wy + (wy - py)
            if 0 < ox < w-1 and 0 < oy < h-1 and maze[oy][ox] == '#':
                maze[wy][wx] = '.'
                maze[oy][ox] = '.'
                add_walls(ox, oy)
    # carve a few extra holes for variety
    for _ in range((w*h)//30):
        x = random.randrange(1, w-1, 2)
        y = random.randrange(1, h-1, 2)
        maze[y][x] = '.'
    return maze

# --- Entities ---
class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.health = MAX_HEALTH
        self.score = 0
        self.shield_turns = 0

class Enemy:
    def __init__(self, x, y):
        self.x = x
        self.y = y

# --- Game logic ---
def find_empty_cells(maze):
    empties = []
    for y,row in enumerate(maze):
        for x,ch in enumerate(row):
            if ch == '.':
                empties.append((x,y))
    return empties

def place_items(maze, player, level):
    empties = find_empty_cells(maze)
    random.shuffle(empties)
    # place glyphs
    glyphs = set()
    for _ in range(NUM_GLYPHS + level//2):
        if not empties: break
        glyphs.add(empties.pop())
    # place powerups
    powerups = set()
    for _ in range(NUM_POWERUPS + (level//3)):
        if not empties: break
        powerups.add(empties.pop())
    # place exit
    exit_cell = None
    if empties:
        exit_cell = empties.pop()
    # place enemies
    enemies = []
    for _ in range(NUM_ENEMIES + level//2):
        if not empties: break
        ex, ey = empties.pop()
        enemies.append(Enemy(ex, ey))
    # place player at a remaining open cell (or override)
    if empties:
        px, py = empties.pop()
        player.x, player.y = px, py
    else:
        # fallback: find any '.' location
        for y,row in enumerate(maze):
            for x,ch in enumerate(row):
                if ch == '.':
                    player.x, player.y = x, y
                    break
            else:
                continue
            break
    return glyphs, powerups, exit_cell, enemies

def render(maze, player, glyphs, powerups, exit_cell, enemies, level):
    grid = deepcopy(maze)
    # place items
    for (x,y) in glyphs:
        grid[y][x] = '*'
    for (x,y) in powerups:
        grid[y][x] = 'P'
    if exit_cell:
        ex,ey = exit_cell
        grid[ey][ex] = 'X'
    for e in enemies:
        grid[e.y][e.x] = 'E'
    # player on top
    grid[player.y][player.x] = '@'
    # print
    clear_screen()
    print(f"GlyphRunner: Neon Maze — Level {level}")
    print(f"Health: {player.health} {'(Shielded)' if player.shield_turns>0 else ''}  Score: {player.score}")
    print('-'*(len(grid[0])+2))
    for row in grid:
        print('|' + ''.join(row) + '|')
    print('-'*(len(grid[0])+2))
    print("Controls: W/A/S/D to move, Q to quit. Collect '*' glyphs, reach 'X' to advance.")
    print("Touching enemies 'E' deals 1 damage unless shielded. Power-ups 'P' may heal or shield.")

def neighbors(x,y):
    return [(x+1,y),(x-1,y),(x,y+1),(x,y-1)]

def enemy_move_towards(enemy, player, maze):
    # choose best neighbor to move: prefer closer to player but must be floor '.' or on glyph/power/exit
    cand = []
    for nx,ny in neighbors(enemy.x, enemy.y):
        if 0 <= nx < len(maze[0]) and 0 <= ny < len(maze):
            if maze[ny][nx] == '.':
                dist = abs(nx - player.x) + abs(ny - player.y)
                cand.append((dist,nx,ny))
    if not cand:
        return  # can't move
    cand.sort()
    # slight randomness to avoid perfect chasing
    if random.random() < 0.7:
        _, nx, ny = cand[0]
    else:
        _, nx, ny = random.choice(cand)
    enemy.x, enemy.y = nx, ny

def run_game():
    level = 1
    player = Player(1,1)
    while True:
        # generate level maze
        w = clamp(WIDTH + (level-1)*2, 15, 41)
        h = clamp(HEIGHT + (level-1), 9, 31)
        # make odd
        if w % 2 == 0: w += 1
        if h % 2 == 0: h += 1
        maze = generate_maze(w, h)
        glyphs, powerups, exit_cell, enemies = place_items(maze, player, level)
        # gameplay loop for this level
        turn = 0
        while True:
            render(maze, player, glyphs, powerups, exit_cell, enemies, level)
            # check win/lose
            if player.health <= 0:
                print("\nYou collapsed... Game Over.")
                print(f"Final Score: {player.score}  Reached Level: {level}")
                return
            # input
            move = input("Move (W/A/S/D or Q): ").strip().lower()[:1]
            if move == 'q':
                print("Quitting. Thanks for playing!")
                return
            dx = dy = 0
            if move == 'w': dy = -1
            elif move == 's': dy = 1
            elif move == 'a': dx = -1
            elif move == 'd': dx = 1
            else:
                # invalid input: treat as 'wait'
                pass
            nx, ny = player.x + dx, player.y + dy
            # bounds & walls
            if 0 <= nx < len(maze[0]) and 0 <= ny < len(maze) and maze[ny][nx] == '.':
                player.x, player.y = nx, ny
            # interactions after moving
            # glyph
            if (player.x, player.y) in glyphs:
                player.score += 10 + level*2
                glyphs.remove((player.x, player.y))
                print("You collected a glyph! + points.")
                time.sleep(0.2)
            # powerup
            if (player.x, player.y) in powerups:
                # random effect: heal or shield
                if random.random() < 0.5:
                    old = player.health
                    player.health = min(MAX_HEALTH + level//3, player.health + 2)
                    print(f"Power-up: Healed from {old} to {player.health}.")
                else:
                    player.shield_turns = 4 + level//2
                    print("Power-up: Shield activated for a few turns.")
                powerups.remove((player.x, player.y))
                time.sleep(0.3)
            # exit
            if exit_cell and (player.x, player.y) == exit_cell:
                # check if enough glyphs collected to advance (optional rule)
                if level < MAX_LEVEL and player.score < level * 15:
                    print("You can leave, but collecting more glyphs gives better score. Leaving anyway...")
                print("You found the exit! Advancing to next level...")
                time.sleep(0.6)
                level += 1
                break
            # enemies move
            for e in enemies:
                # enemies move more frequently at higher levels (simulate speed)
                moves_this_turn = 1 + (level//3)
                for _ in range(moves_this_turn):
                    if random.random() < 0.6:
                        enemy_move_towards(e, player, maze)
                    else:
                        # random move
                        dirs = neighbors(e.x, e.y)
                        random.shuffle(dirs)
                        for nx,ny in dirs:
                            if 0 <= nx < len(maze[0]) and 0 <= ny < len(maze) and maze[ny][nx] == '.':
                                e.x, e.y = nx, ny
                                break
            # check collisions with enemies
            for e in enemies:
                if e.x == player.x and e.y == player.y:
                    if player.shield_turns > 0:
                        print("An enemy hit your shield! No damage.")
                        player.shield_turns -= 1
                    else:
                        player.health -= 1
                        print("Ouch! An enemy hit you. -1 health.")
                        time.sleep(0.4)
                    # push enemy back a tile if possible
                    for nx,ny in neighbors(e.x, e.y):
                        if 0 <= nx < len(maze[0]) and 0 <= ny < len(maze) and maze[ny][nx] == '.':
                            e.x, e.y = nx, ny
                            break
            if player.shield_turns > 0:
                player.shield_turns -= 1
            turn += 1
            # small message at intervals
            if turn % 10 == 0:
                print(f"(Turn {turn}) Keep going! Glyphs left: {len(glyphs)}")
                time.sleep(0.2)
        # level loop ends; continue to next level
        if level > MAX_LEVEL:
            print("Congratulations — you've mastered the Neon Maze!")
            print(f"Final Score: {player.score}")
            return

if __name__ == '__main__':
    try:
        run_game()
    except KeyboardInterrupt:
        print("\nInterrupted. Goodbye!")
