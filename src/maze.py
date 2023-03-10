import random
import datetime
import csv
import os
import time
from tkinter import *
from collections import deque
from PIL import ImageGrab
from src.theme import COLOR
from src.agent import Agent


class Maze:
    '''
    This is the main class to create Maze.
    '''

    def __init__(self, rows=10, cols=10, cell_density=2):
        '''
        rows--> No. of rows of the Maze
        cols--> No. of columns of the Maze
        Need to pass just the two arguments. The rest will be assigned automatically
        maze_map--> Will be set to a Dicationary. Keys will be cells and
                    values will be another dictionary with keys=['E','W','N','S'] for
                    East West North South and values will be 0 or 1. 0 means that 
                    direction(EWNS) is blocked. 1 means that direction is open.
        grid--> A list of all cells
        path--> Shortest path from start(bottom right) to goal(by default top left)
                It will be a dictionary
        _win,_cell_width,_canvas -->    _win and )canvas are for Tkinter window and canvas
                                        _cell_width is cell width calculated automatically
        _agents-->  A list of aganets on the Maze
        markedCells-->  Will be used to mark some particular cell during
                        path trace by the Agent.
        _
        '''
        self.rows = rows
        self.cols = cols
        self.maze_map = {}
        self.grid = []
        self.path = {}
        self._cell_width = 200
        self._win = None
        self._canvas = None
        self._agents = []
        self.mark_cells = []
        self.cell_density = cell_density

    @property
    def grid(self):
        return self._grid

    @grid.setter
    def grid(self, n):
        self._grid = []
        y = 0
        for n in range(self.cols):
            x = 1
            y = 1+y
            for m in range(self.rows):
                self.grid.append((x, y))
                self.maze_map[x, y] = {'E': 0, 'W': 0, 'N': 0, 'S': 0}
                x = x + 1

    def _open_east_wall(self, x, y):
        '''
        To remove the East Wall of the cell
        '''
        self.maze_map[x, y]['E'] = 1
        if y+1 <= self.cols:
            self.maze_map[x, y+1]['W'] = 1

    def _open_west_wall(self, x, y):
        self.maze_map[x, y]['W'] = 1
        if y-1 > 0:
            self.maze_map[x, y-1]['E'] = 1

    def _open_north_wall(self, x, y):
        self.maze_map[x, y]['N'] = 1
        if x-1 > 0:
            self.maze_map[x-1, y]['S'] = 1

    def _open_south_wall(self, x, y):
        self.maze_map[x, y]['S'] = 1
        if x+1 <= self.rows:
            self.maze_map[x+1, y]['N'] = 1

    def create_maze(self, x=1, y=1, pattern=None, loop_percent=0, save_maze=False, load_maze=None, theme: COLOR = COLOR.dark):
        '''
        Function to create a random maze
        
        args: 
            x: x coordinate of the end point
            y: y coordinate of the end point 
            pattern: Either horizontal or vertical, the maze structure will be according to the pattern like more vertical or horizontal
            loop_percent: number of paths/loops from start to the end
            save_maze: save the generated maze as a csv file for reference
            load_maze: provide the csv file to generate a desired maze
            theme: theme
        '''
        _stack = []
        _closed = []
        self.theme = theme
        self._goal = (x, y)
        if (isinstance(theme, str)):
            if (theme in COLOR.__members__):
                self.theme = COLOR[theme]
            else:
                raise ValueError(f'{theme} is not a valid theme COLOR!')

        def blocked_neighbours(cell):
            n = []
            for d in self.maze_map[cell].keys():
                if self.maze_map[cell][d] == 0:
                    if d == 'E' and (cell[0], cell[1]+1) in self.grid:
                        n.append((cell[0], cell[1]+1))
                    elif d == 'W' and (cell[0], cell[1]-1) in self.grid:
                        n.append((cell[0], cell[1]-1))
                    elif d == 'N' and (cell[0]-1, cell[1]) in self.grid:
                        n.append((cell[0]-1, cell[1]))
                    elif d == 'S' and (cell[0]+1, cell[1]) in self.grid:
                        n.append((cell[0]+1, cell[1]))
            return n

        def remove_wall_in_between(cell1, cell2):
            '''
            To remove wall in between two cells
            '''
            if cell1[0] == cell2[0]:
                if cell1[1] == cell2[1]+1:
                    self.maze_map[cell1]['W'] = 1
                    self.maze_map[cell2]['E'] = 1
                else:
                    self.maze_map[cell1]['E'] = 1
                    self.maze_map[cell2]['W'] = 1
            else:
                if cell1[0] == cell2[0]+1:
                    self.maze_map[cell1]['N'] = 1
                    self.maze_map[cell2]['S'] = 1
                else:
                    self.maze_map[cell1]['S'] = 1
                    self.maze_map[cell2]['N'] = 1

        def is_cyclic(cell1, cell2):
            '''
            To avoid too much blank(clear) path.
            '''
            ans = False
            if cell1[0] == cell2[0]:
                if cell1[1] > cell2[1]:
                    cell1, cell2 = cell2, cell1
                if self.maze_map[cell1]['S'] == 1 and self.maze_map[cell2]['S'] == 1:
                    if (cell1[0]+1, cell1[1]) in self.grid and self.maze_map[(cell1[0]+1, cell1[1])]['E'] == 1:
                        ans = True
                if self.maze_map[cell1]['N'] == 1 and self.maze_map[cell2]['N'] == 1:
                    if (cell1[0]-1, cell1[1]) in self.grid and self.maze_map[(cell1[0]-1, cell1[1])]['E'] == 1:
                        ans = True
            else:
                if cell1[0] > cell2[0]:
                    cell1, cell2 = cell2, cell1
                if self.maze_map[cell1]['E'] == 1 and self.maze_map[cell2]['E'] == 1:
                    if (cell1[0], cell1[1]+1) in self.grid and self.maze_map[(cell1[0], cell1[1]+1)]['S'] == 1:
                        ans = True
                if self.maze_map[cell1]['W'] == 1 and self.maze_map[cell2]['W'] == 1:
                    if (cell1[0], cell1[1]-1) in self.grid and self.maze_map[(cell1[0], cell1[1]-1)]['S'] == 1:
                        ans = True
            return ans

        def breadth_first_search(cell):
            '''
            Breadth First Search
            To generate the shortest path.
            This will be used only when there are multiple paths (loop_percent>0) or
            Maze is loaded from a CSV file.
            If a perfect Maze is generated and without the load file, this method will
            not be used since the Maze generation will calculate the path.
            '''
            frontier = deque()
            frontier.append(cell)
            path = {}
            visited = {(self.rows, self.cols)}
            print('maze_map: ', self.maze_map)
            while len(frontier) > 0:
                cell = frontier.popleft()
                if self.maze_map[cell]['W'] and (cell[0], cell[1]-1) not in visited:
                    next_cell = (cell[0], cell[1]-1)
                    path[next_cell] = cell
                    frontier.append(next_cell)
                    visited.add(next_cell)
                if self.maze_map[cell]['S'] and (cell[0]+1, cell[1]) not in visited:
                    next_cell = (cell[0]+1, cell[1])
                    path[next_cell] = cell
                    frontier.append(next_cell)
                    visited.add(next_cell)
                if self.maze_map[cell]['E'] and (cell[0], cell[1]+1) not in visited:
                    next_cell = (cell[0], cell[1]+1)
                    path[next_cell] = cell
                    frontier.append(next_cell)
                    visited.add(next_cell)
                if self.maze_map[cell]['N'] and (cell[0]-1, cell[1]) not in visited:
                    next_cell = (cell[0]-1, cell[1])
                    path[next_cell] = cell
                    frontier.append(next_cell)
                    visited.add(next_cell)
            forward_path = {}
            cell = self._goal
            while cell != (self.rows, self.cols):
                try:
                    forward_path[path[cell]] = cell
                    cell = path[cell]
                except:
                    print('Path to goal not found!')
                    return
            return forward_path
        # if Maze is to be generated randomly
        if not load_maze:
            _stack.append((x, y))
            _closed.append((x, y))
            bias_length = 2  # if pattern is 'v' or 'h'
            if (pattern is not None and pattern.lower() == 'h'):
                bias_length = max(self.cols//10, 2)
            if (pattern is not None and pattern.lower() == 'v'):
                bias_length = max(self.rows//10, 2)
            bias = 0

            while len(_stack) > 0:
                cell = []
                bias += 1
                if (x, y + 1) not in _closed and (x, y+1) in self.grid:
                    cell.append("E")
                if (x, y-1) not in _closed and (x, y-1) in self.grid:
                    cell.append("W")
                if (x+1, y) not in _closed and (x+1, y) in self.grid:
                    cell.append("S")
                if (x-1, y) not in _closed and (x-1, y) in self.grid:
                    cell.append("N")
                if len(cell) > 0:
                    if pattern is not None and pattern.lower() == 'h' and bias <= bias_length:
                        if ('E' in cell or 'W' in cell):
                            if 'S' in cell:
                                cell.remove('S')
                            if 'N' in cell:
                                cell.remove('N')
                    elif pattern is not None and pattern.lower() == 'v' and bias <= bias_length:
                        if ('N' in cell or 'S' in cell):
                            if 'E' in cell:
                                cell.remove('E')
                            if 'W' in cell:
                                cell.remove('W')
                    else:
                        bias = 0
                    current_cell = (random.choice(cell))
                    if current_cell == "E":
                        self._open_east_wall(x, y)
                        self.path[x, y+1] = x, y
                        y = y + 1
                        _closed.append((x, y))
                        _stack.append((x, y))

                    elif current_cell == "W":
                        self._open_west_wall(x, y)
                        self.path[x, y-1] = x, y
                        y = y - 1
                        _closed.append((x, y))
                        _stack.append((x, y))

                    elif current_cell == "N":
                        self._open_north_wall(x, y)
                        self.path[(x-1, y)] = x, y
                        x = x - 1
                        _closed.append((x, y))
                        _stack.append((x, y))

                    elif current_cell == "S":
                        self._open_south_wall(x, y)
                        self.path[(x+1, y)] = x, y
                        x = x + 1
                        _closed.append((x, y))
                        _stack.append((x, y))

                else:
                    x, y = _stack.pop()

            # Multiple Path Loops
            if loop_percent != 0:

                x, y = self.rows, self.cols
                pathCells = [(x, y)]
                while x != self.rows or y != self.cols:
                    x, y = self.path[(x, y)]
                    pathCells.append((x, y))
                notPathCells = [i for i in self.grid if i not in pathCells]
                random.shuffle(pathCells)
                random.shuffle(notPathCells)
                pathLength = len(pathCells)
                notPathLength = len(notPathCells)
                count1, count2 = pathLength/3*loop_percent/100, notPathLength/3*loop_percent/100

                # remove blocks from shortest path cells
                count = 0
                i = 0
                while count < count1:  # these many blocks to remove
                    if len(blocked_neighbours(pathCells[i])) > 0:
                        cell = random.choice(blocked_neighbours(pathCells[i]))
                        if not is_cyclic(cell, pathCells[i]):
                            remove_wall_in_between(cell, pathCells[i])
                            count += 1
                        i += 1

                    else:
                        i += 1
                    if i == len(pathCells):
                        break
                # remove blocks from outside shortest path cells
                if len(notPathCells) > 0:
                    count = 0
                    i = 0
                    while count < count2:  # these many blocks to remove
                        if len(blocked_neighbours(notPathCells[i])) > 0:
                            cell = random.choice(
                                blocked_neighbours(notPathCells[i]))
                            if not is_cyclic(cell, notPathCells[i]):
                                remove_wall_in_between(cell, notPathCells[i])
                                count += 1
                            i += 1

                        else:
                            i += 1
                        if i == len(notPathCells):
                            break
                self.path = breadth_first_search((self.rows, self.cols))
        else:
            # Load Maze from CSV file
            with open(load_maze, 'r') as f:
                last = list(f.readlines())[-1]
                c = last.split(',')
                c[0] = int(c[0].lstrip('"('))
                c[1] = int(c[1].rstrip(')"'))
                self.rows = c[0]
                self.cols = c[1]
                self.grid = []

            with open(load_maze, 'r') as f:
                r = csv.reader(f)
                next(r)
                for i in r:
                    c = i[0].split(',')
                    c[0] = int(c[0].lstrip('('))
                    c[1] = int(c[1].rstrip(')'))
                    self.maze_map[tuple(c)] = {'E': int(i[1]), 'W': int(
                        i[2]), 'N': int(i[3]), 'S': int(i[4])}
            self.path = breadth_first_search((self.rows, self.cols))
        self._draw_maze(self.theme)
        Agent(self, *self._goal, shape='square',
              filled=True, color=COLOR.green)
        if save_maze:
            dt_string = datetime.datetime.now().strftime("%Y-%m-%d--%H-%M-%S")
            with open(f'Maze--{dt_string}.csv', 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['  cell  ', 'E', 'W', 'N', 'S'])
                for k, v in self.maze_map.items():
                    entry = [k]
                    for i in v.values():
                        entry.append(i)
                    writer.writerow(entry)
                f.seek(0, os.SEEK_END)
                f.seek(f.tell()-2, os.SEEK_SET)
                f.truncate()

    def _draw_maze(self, theme):
        '''
        Creation of Tkinter window and Maze lines
        '''

        self._lab_width = 26  # Space from the top for Labels
        self._win = Tk()
        self._win.state('zoomed')
        self._win.title('PyMaze - Python Maze solver')

        scr_width = self._win.winfo_screenwidth()
        scr_height = self._win.winfo_screenheight()
        self._win.geometry(f"{scr_width}x{scr_height}+0+0")
        # 0,0 is top left corner
        self._canvas = Canvas(
            width=scr_width, height=scr_height, bg=theme.value[0])
        self._canvas.pack(expand=YES, fill=BOTH)
        # Some calculations for calculating the width of the Maze cell
        k = 3.25
        if self.rows >= 95 and self.cols >= 95:
            k = 0
        elif self.rows >= 80 and self.cols >= 80:
            k = 1
        elif self.rows >= 70 and self.cols >= 70:
            k = 1.5
        elif self.rows >= 50 and self.cols >= 50:
            k = 2
        elif self.rows >= 35 and self.cols >= 35:
            k = 2.5
        elif self.rows >= 22 and self.cols >= 22:
            k = 3
        self._cell_width = round(min(((scr_height-self.rows-k*self._lab_width)/(
            self.rows)), ((scr_width-self.cols-k*self._lab_width)/(self.cols)), 90), 3)

        # Creating Maze lines
        if self._win is not None:
            if self.grid is not None:
                for cell in self.grid:
                    x, y = cell
                    w = self._cell_width
                    x = x*w-w+self._lab_width
                    y = y*w-w+self._lab_width
                    if self.maze_map[cell]['E'] == False:
                        l = self._canvas.create_line(
                            y + w, x, y + w, x + w, width=self.cell_density, fill=theme.value[1], tag='line')
                    if self.maze_map[cell]['W'] == False:
                        l = self._canvas.create_line(
                            y, x, y, x + w, width=self.cell_density, fill=theme.value[1], tag='line')
                    if self.maze_map[cell]['N'] == False:
                        l = self._canvas.create_line(
                            y, x, y + w, x, width=self.cell_density, fill=theme.value[1], tag='line')
                    if self.maze_map[cell]['S'] == False:
                        l = self._canvas.create_line(
                            y, x + w, y + w, x + w, width=self.cell_density, fill=theme.value[1], tag='line')

    def _redraw_cell(self, x, y, theme):
        '''
        To redraw a cell.
        With Full sized square Agent, it can overlap with Maze lines
        So the cell is redrawn so that cell lines are on top
        '''
        w = self._cell_width
        cell = (x, y)
        x = x*w-w+self._lab_width
        y = y*w-w+self._lab_width
        if self.maze_map[cell]['E'] == False:
            self._canvas.create_line(
                y + w, x, y + w, x + w, width=self.cell_density, fill=theme.value[1])
        if self.maze_map[cell]['W'] == False:
            self._canvas.create_line(
                y, x, y, x + w, width=self.cell_density, fill=theme.value[1])
        if self.maze_map[cell]['N'] == False:
            self._canvas.create_line(
                y, x, y + w, x, width=self.cell_density, fill=theme.value[1])
        if self.maze_map[cell]['S'] == False:
            self._canvas.create_line(
                y, x + w, y + w, x + w, width=self.cell_density, fill=theme.value[1])

    def enable_arrow_keys(self, a):
        '''
        To control an Agent a with Arrow Keys
        '''
        self._win.bind('<Left>', a.move_position_left)
        self._win.bind('<Right>', a.move_position_right)
        self._win.bind('<Up>', a.move_position_up)
        self._win.bind('<Down>', a.move_position_down)

    def enable_wasd_keys(self, a):
        '''
        To control an Agent a with keys W,A,S,D
        '''
        self._win.bind('<a>', a.move_position_left)
        self._win.bind('<d>', a.move_position_right)
        self._win.bind('<w>', a.move_position_up)
        self._win.bind('<s>', a.move_position_down)

    _tracePathList = []

    def _tracePathSingle(self, a, p, kill, showMarked, delay):
        '''
        An interal method to help trace_path method for tracing a path by Agent.
        '''

        def killAgent(a):
            '''
            if the Agent should be killed after it reaches the Goal or completes the path
            '''
            for i in range(len(a._body)):
                self._canvas.delete(a._body[i])
            self._canvas.delete(a._head)
        w = self._cell_width
        if ((a.x, a.y) in self.mark_cells and showMarked):
            w = self._cell_width
            x = a.x*w-w+self._lab_width
            y = a.y*w-w+self._lab_width
            self._canvas.create_oval(y + w/2.5+w/20, x + w/2.5+w/20, y + w/2.5 +
                                     w/4-w/20, x + w/2.5 + w/4-w/20, fill='red', outline='red', tag='ov')
            self._canvas.tag_raise('ov')

        if (a.x, a.y) == (a.goal):
            del Maze._tracePathList[0][0][a]
            if Maze._tracePathList[0][0] == {}:
                del Maze._tracePathList[0]
                if len(Maze._tracePathList) > 0:
                    self.trace_path(
                        Maze._tracePathList[0][0], kill=Maze._tracePathList[0][1], delay=Maze._tracePathList[0][2])
            if kill:
                self._win.after(300, killAgent, a)
            return
        # If path is provided as Dictionary
        if (type(p) == dict):
            if (len(p) == 0):
                del Maze._tracePathList[0][0][a]
                return
            if a.shape == 'arrow':
                old = (a.x, a.y)
                new = p[(a.x, a.y)]
                o = a._orient

                if old != new:
                    if old[0] == new[0]:
                        if old[1] > new[1]:
                            mov = 3  # 'W' #3
                        else:
                            mov = 1  # 'E' #1
                    else:
                        if old[0] > new[0]:
                            mov = 0  # 'N' #0

                        else:
                            mov = 2  # 'S' #2
                    if mov-o == 2:
                        a._rotate_clock_wise()

                    if mov-o == -2:
                        a._rotate_clock_wise()
                    if mov-o == 1:
                        a._rotate_clock_wise()
                    if mov-o == -1:
                        a._rotate_counter_clock_wise()
                    if mov-o == 3:
                        a._rotate_counter_clock_wise()
                    if mov-o == -3:
                        a._rotate_clock_wise()
                    if mov == o:
                        a.x, a.y = p[(a.x, a.y)]
                else:
                    del p[(a.x, a.y)]
            else:
                a.x, a.y = p[(a.x, a.y)]
        # If path is provided as String
        if (type(p) == str):
            if (len(p) == 0):
                del Maze._tracePathList[0][0][a]
                if Maze._tracePathList[0][0] == {}:
                    del Maze._tracePathList[0]
                    if len(Maze._tracePathList) > 0:
                        self.trace_path(
                            Maze._tracePathList[0][0], kill=Maze._tracePathList[0][1], delay=Maze._tracePathList[0][2])
                if kill:

                    self._win.after(300, killAgent, a)
                return
            if a.shape == 'arrow':
                old = (a.x, a.y)
                new = p[0]
                o = a._orient
                if new == 'N':
                    mov = 0
                elif new == 'E':
                    mov = 1
                elif new == 'S':
                    mov = 2
                elif new == 'W':
                    mov = 3

                if mov-o == 2:
                    a._rotate_clock_wise()

                if mov-o == -2:
                    a._rotate_clock_wise()
                if mov-o == 1:
                    a._rotate_clock_wise()
                if mov-o == -1:
                    a._rotate_counter_clock_wise()
                if mov-o == 3:
                    a._rotate_counter_clock_wise()
                if mov-o == -3:
                    a._rotate_clock_wise()
            if a.shape == 'square' or mov == o:
                move = p[0]
                if move == 'E':
                    if a.y+1 <= self.cols:
                        a.y += 1
                elif move == 'W':
                    if a.y-1 > 0:
                        a.y -= 1
                elif move == 'N':
                    if a.x-1 > 0:
                        a.x -= 1
                        a.y = a.y
                elif move == 'S':
                    if a.x+1 <= self.rows:
                        a.x += 1
                        a.y = a.y
                elif move == 'C':
                    a._rotate_clock_wise()
                elif move == 'A':
                    a._rotate_counter_clock_wise()
                p = p[1:]
        # If path is provided as List
        if (type(p) == list):
            if (len(p) == 0):
                del Maze._tracePathList[0][0][a]
                if Maze._tracePathList[0][0] == {}:
                    del Maze._tracePathList[0]
                    if len(Maze._tracePathList) > 0:
                        self.trace_path(
                            Maze._tracePathList[0][0], kill=Maze._tracePathList[0][1], delay=Maze._tracePathList[0][2])
                if kill:
                    self._win.after(300, killAgent, a)
                return
            if a.shape == 'arrow':
                old = (a.x, a.y)
                new = p[0]
                o = a._orient

                if old != new:
                    if old[0] == new[0]:
                        if old[1] > new[1]:
                            mov = 3  # 'W' #3
                        else:
                            mov = 1  # 'E' #1
                    else:
                        if old[0] > new[0]:
                            mov = 0  # 'N' #0

                        else:
                            mov = 2  # 'S' #2
                    if mov-o == 2:
                        a._rotate_clock_wise()

                    elif mov-o == -2:
                        a._rotate_clock_wise()
                    elif mov-o == 1:
                        a._rotate_clock_wise()
                    elif mov-o == -1:
                        a._rotate_counter_clock_wise()
                    elif mov-o == 3:
                        a._rotate_counter_clock_wise()
                    elif mov-o == -3:
                        a._rotate_clock_wise()
                    elif mov == o:
                        a.x, a.y = p[0]
                        del p[0]
                else:
                    del p[0]
            else:
                a.x, a.y = p[0]
                del p[0]

        self._win.after(delay, self._tracePathSingle,
                        a, p, kill, showMarked, delay)

    def trace_path(self, d, kill=False, delay=100, showMarked=False):
        '''
        A method to trace path by Agent
        You can provide more than one Agent/path details
        '''
        self._tracePathList.append((d, kill, delay))
        if Maze._tracePathList[0][0] == d:
            for a, p in d.items():
                if a.goal != (a.x, a.y) and len(p) != 0:
                    self._tracePathSingle(a, p, kill, showMarked, delay)

    def save_gif(self, screenshots, filename):
        screenshots[0].save(
            filename,
            format='GIF',
            append_images=screenshots[1:],
            save_all=True,
            duration=100,
            loop=0
        )

    def capture_screenshots(self, num_frames, screenshots):
        # Capture the screen as an image
        time.sleep(1)

        # check if the window has a size
        if self._win.winfo_width() == 0 or self._win.winfo_height() == 0:
            return

        # create a bounding box from the window coordinates
        x, y = self._win.winfo_x(), self._win.winfo_y()
        width, height = self._win.winfo_width(), self._win.winfo_height()

        bbox = (int(x), int(y), int(x) + int(width), int(y) + int(height))
        image = ImageGrab.grab(bbox)

        # Add the image to the list of screenshots
        screenshots.append(image)

        # Stop capturing screenshots if we've reached the desired number
        if len(screenshots) == num_frames:
            self.save_gif(screenshots, 'animation.gif')
            return

        # Schedule the next screenshot capture in 100 milliseconds
        self._win.after(100, self.capture_screenshots, num_frames, screenshots)

    def run(self):
        '''
        Finally to run the Tkinter Main Loop
        '''

        # for generating the gif of the solution
        # self._win.after(100, self.capture_screenshots, 25, [])

        self._win.mainloop()
