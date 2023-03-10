from src.agent import Agent
from src.maze import Maze
from queue import PriorityQueue

def calculate_manhattan_distance(cell1, cell2):
    x1, y1 = cell1
    x2, y2 = cell2

    return abs(x1 - x2) + abs(y1 - y2)

    
def a_star(maze, start=None):
    if start is None:
        start = (maze.rows, maze.cols)
    minimum_cost_cell = PriorityQueue()
    minimum_cost_cell.put(
        (
            calculate_manhattan_distance(start, maze._goal),
            calculate_manhattan_distance(start, maze._goal),
            start,
        )
    )
    a_path = {}
    g_score = {row: float("inf") for row in maze.grid}
    g_score[start] = 0
    f_score = {row: float("inf") for row in maze.grid}
    f_score[start] = calculate_manhattan_distance(start, maze._goal)
    search_path = [start]
    while not minimum_cost_cell.empty():
        current_cell = minimum_cost_cell.get()[2]
        search_path.append(current_cell)
        if current_cell == maze._goal:
            break
        for d in "ESNW":
            if maze.maze_map[current_cell][d] == True:
                if d == "E":
                    child_cell = (current_cell[0], current_cell[1] + 1)
                elif d == "W":
                    child_cell = (current_cell[0], current_cell[1] - 1)
                elif d == "N":
                    child_cell = (current_cell[0] - 1, current_cell[1])
                elif d == "S":
                    child_cell = (current_cell[0] + 1, current_cell[1])

                temp_g_score = g_score[current_cell] + 1
                temp_f_score = temp_g_score + calculate_manhattan_distance(
                    child_cell, maze._goal
                )

                if temp_f_score < f_score[child_cell]:
                    a_path[child_cell] = current_cell
                    g_score[child_cell] = temp_g_score
                    f_score[child_cell] = temp_g_score + calculate_manhattan_distance(
                        child_cell, maze._goal
                    )
                    minimum_cost_cell.put(
                        (
                            f_score[child_cell],
                            calculate_manhattan_distance(child_cell, maze._goal),
                            child_cell,
                        )
                    )

    forward_path = {}
    cell = maze._goal
    while cell != start:
        forward_path[a_path[cell]] = cell
        cell = a_path[cell]
    return forward_path
   

if __name__ == "__main__":

    height_of_maze = int(input("Enter the height of the maze: "))
    width_of_maze = int(input("Enter the width of the maze: "))

    x_start = int(input("Enter the x coordinate of the starting point: "))
    y_start = int(input("Enter the y coordinate of the starting point: "))

    x_end = int(input("Enter the x coordinate of the ending point: "))
    y_end = int(input("Enter the y coordinate of the ending point: "))

    wall_density = 2
    wall_density = int(input("Enter the wall density for the maze: "))
  
    my_maze = Maze(height_of_maze, width_of_maze, cell_density=wall_density)

    my_maze.create_maze(x=x_end, y=y_end, theme="light")
    my_agent = Agent(my_maze, footprints=True, x=x_start, y=y_start, goal=(x_end,y_end), filled=True,shape='arrow', color="red")


    # calculate path from A* algorithm
    a_star_path = a_star(my_maze, (x_start, y_start)) 
    my_maze.trace_path({my_agent: a_star_path}, delay=100)
    my_maze.run()