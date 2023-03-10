from tkinter import *
from src.theme import COLOR


class Agent:
    '''
    The agents can be placed on the Maze.
    They can represent the virtual object just to indcate the cell selected in Maze.
    Or they can be the physical agents (like robots)
    They can have two shapes (square or arrow)
    '''

    def __init__(self, parent_maze, x=None, y=None, shape='square', goal=None, filled=False, footprints=False, color: COLOR = COLOR.blue):
        '''
        parentmaze-->  The Maze on which Agent is placed.
        x,y-->  Position of the Agent i.e. cell inside which Agent will be placed
                Default value is the lower right corner of the Maze
        shape-->    square or arrow (as string)
        goal-->     Default value is the goal of the Maze
        filled-->   For square shape, filled=False is a smaller square
                    While filled =True is a biiger square filled in complete Cell
                    This option doesn't matter for arrow shape.
        footprints-->   When the aganet will move to some other cell, its footprints
                        on the previous cell can be placed by making this True
        color-->    Color of the Agent.
        _orient-->  You don't need to pass this
                    It is used with arrow shape Agent to shows it turning
        position--> You don't need to pass this
                    This is the cell (x,y)
        _head-->    You don't need to pass this
                    It is actually the Agent.
        _body-->    You don't need to pass this
                    Tracks the body of the Agent (the previous positions of it)
        '''
        self._parent_maze = parent_maze
        self.color = color
        if (isinstance(color, str)):
            if (color in COLOR.__members__):
                self.color = COLOR[color]
            else:
                raise ValueError(f'{color} is not a valid COLOR!')
        self.filled = filled
        self.shape = shape
        self._orient = 0
        if x is None:
            x = parent_maze.rows
        if y is None:
            y = parent_maze.cols
        self.x = x
        self.y = y
        self.footprints = footprints
        self._parent_maze._agents.append(self)
        if goal == None:
            self.goal = self._parent_maze._goal
        else:
            self.goal = goal
        print("this is goal cor: ", self.goal)
        self._body = []
        self.position = (self.x, self.y)

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, new_x):
        self._x = new_x

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, new_y):
        self._y = new_y
        w = self._parent_maze._cell_width
        x = self.x*w-w+self._parent_maze._lab_width
        y = self.y*w-w+self._parent_maze._lab_width
        if self.shape == 'square':
            if self.filled:
                self._coord = (y, x, y + w, x + w)
            else:
                self._coord = (y + w/2.5, x + w/2.5, y +
                               w/2.5 + w/4, x + w/2.5 + w/4)
        else:
            self._coord = (y + w/2, x + 3*w/9, y + w/2, x + 3*w/9+w/4)

        if (hasattr(self, '_head')):
            if self.footprints is False:
                self._parent_maze._canvas.delete(self._head)
            else:
                if self.shape == 'square':
                    self._parent_maze._canvas.itemconfig(
                        self._head, fill=self.color.value[1], outline="")
                    self._parent_maze._canvas.tag_raise(self._head)
                    try:
                        self._parent_maze._canvas.tag_lower(self._head, 'ov')
                    except:
                        pass
                    if self.filled:
                        lll = self._parent_maze._canvas.coords(self._head)
                        oldcell = (round(((lll[1]-26)/self._parent_maze._cell_width)+1), round(
                            ((lll[0]-26)/self._parent_maze._cell_width)+1))
                        self._parent_maze._redraw_cell(
                            *oldcell, self._parent_maze.theme)
                else:
                    self._parent_maze._canvas.itemconfig(
                        self._head, fill=self.color.value[1])  # ,outline='gray70')
                    self._parent_maze._canvas.tag_raise(self._head)
                    try:
                        self._parent_maze._canvas.tag_lower(self._head, 'ov')
                    except:
                        pass
                self._body.append(self._head)
            if not self.filled or self.shape == 'arrow':
                if self.shape == 'square':
                    self._head = self._parent_maze._canvas.create_rectangle(
                        *self._coord, fill=self.color.value[0], outline='')  # stipple='gray75'
                    try:
                        self._parent_maze._canvas.tag_lower(self._head, 'ov')
                    except:
                        pass
                else:
                    self._head = self._parent_maze._canvas.create_line(
                        *self._coord, fill=self.color.value[0], arrow=FIRST, arrowshape=(3/10*w, 4/10*w, 4/10*w))  # ,outline=self.color.name)
                    try:
                        self._parent_maze._canvas.tag_lower(self._head, 'ov')
                    except:
                        pass
                    o = self._orient % 4
                    if o == 1:
                        self._rotate_clock_wise()
                        self._orient -= 1
                    elif o == 3:
                        self._rotate_counter_clock_wise()
                        self._orient += 1
                    elif o == 2:
                        self._rotate_counter_clock_wise()
                        self._rotate_counter_clock_wise()
                        self._orient += 2
            else:
                self._head = self._parent_maze._canvas.create_rectangle(
                    *self._coord, fill=self.color.value[0], outline='')  # stipple='gray75'
                try:
                    self._parent_maze._canvas.tag_lower(self._head, 'ov')
                except:
                    pass
                self._parent_maze._redraw_cell(
                    self.x, self.y, theme=self._parent_maze.theme)
        else:
            self._head = self._parent_maze._canvas.create_rectangle(
                *self._coord, fill=self.color.value[0], outline='')  # stipple='gray75'
            try:
                self._parent_maze._canvas.tag_lower(self._head, 'ov')
            except:
                pass
            self._parent_maze._redraw_cell(
                self.x, self.y, theme=self._parent_maze.theme)

    @property
    def position(self):
        return (self.x, self.y)

    @position.setter
    def position(self, newpos):
        self.x = newpos[0]
        self.y = newpos[1]
        self._position = newpos

    def _rotate_counter_clock_wise(self):
        '''
        To Rotate the Agent in Counter Clock Wise direction
        '''
        def point_new(p, new_origin):
            return (p[0]-new_origin[0], p[1]-new_origin[1])
        w = self._parent_maze._cell_width
        x = self.x*w-w+self._parent_maze._lab_width
        y = self.y*w-w+self._parent_maze._lab_width
        cent = (y+w/2, x+w/2)
        p1 = point_new((self._coord[0], self._coord[1]), cent)
        p2 = point_new((self._coord[2], self._coord[3]), cent)
        p1_cw = (p1[1], -p1[0])
        p2_cw = (p2[1], -p2[0])
        p1 = p1_cw[0]+cent[0], p1_cw[1]+cent[1]
        p2 = p2_cw[0]+cent[0], p2_cw[1]+cent[1]
        self._coord = (*p1, *p2)
        self._parent_maze._canvas.coords(self._head, *self._coord)
        self._orient = (self._orient-1) % 4

    def _rotate_clock_wise(self):
        '''
        To Rotate the Agent in Clock Wise direction
        '''
        def point_new(p, new_origin):
            return (p[0]-new_origin[0], p[1]-new_origin[1])
        w = self._parent_maze._cell_width
        x = self.x*w-w+self._parent_maze._lab_width
        y = self.y*w-w+self._parent_maze._lab_width
        cent = (y+w/2, x+w/2)
        p1 = point_new((self._coord[0], self._coord[1]), cent)
        p2 = point_new((self._coord[2], self._coord[3]), cent)
        p1_cw = (-p1[1], p1[0])
        p2_cw = (-p2[1], p2[0])
        p1 = p1_cw[0]+cent[0], p1_cw[1]+cent[1]
        p2 = p2_cw[0]+cent[0], p2_cw[1]+cent[1]
        self._coord = (*p1, *p2)
        self._parent_maze._canvas.coords(self._head, *self._coord)
        self._orient = (self._orient+1) % 4

    def move_position_right(self, event):
        if self._parent_maze.maze_map[self.x, self.y]['E'] == True:
            self.y = self.y+1

    def move_position_left(self, event):
        if self._parent_maze.maze_map[self.x, self.y]['W'] == True:
            self.y = self.y-1

    def move_position_up(self, event):
        if self._parent_maze.maze_map[self.x, self.y]['N'] == True:
            self.x = self.x-1
            self.y = self.y

    def move_position_down(self, event):
        if self._parent_maze.maze_map[self.x, self.y]['S'] == True:
            self.x = self.x+1
            self.y = self.y