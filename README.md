## PyMaze
PyMaze is a Python application that generates a random maze and solves it using the A* algorithm. The application is designed to allow users to input the size of the maze, starting and ending points, and also specify the density of walls.

The A* algorithm implementation is optimized for performance and the application has the ability to extend with other algorithms as well. To visualize the solution path, tkinter, a Python library, is used. The solution path can be saved as a GIF animation.

## How to use
To use the application simply run the main.py file and it will ask for values for the parameters like, height of the maze, width of the maze, x and y coordinates for the starting and ending points, wall density for the walls. Provide these information and it will create a random maze and solve it visually using tkinter.

## Solution Approach
- A random maze is created using recursive backtracking algorithm based on user inputs
- Then based on the starting and ending coordinates, `A*(a-star)` algorithm is used to find the optimal path from start to end points
- Then an agent is created and place in the maze to walk on the maze
- The path generated from `A*(a-star)` algorithm is then traced back using the agent to show the solution visually.
- Solution gif is also generated in the end

## Code Structure
- `src/theme.py` - Contains an enum of themes that are used by `maze` and `agent` files.
- `src/agent.py` - Contains code for creating an agent that traverses through the maze 
- `src/maze.py` - Contains code for creating a random maze, saving a maze, loading a maze and much more which related to maze. This code is then used by the main driver of the application.
- `main.py` - the driver of the application, imports all the information from the src package and contains the `A*(a-star)` algorithm and it is expected to run the main.py file providing all the paramters of the puzzle.


## Screenshots
![1](https://user-images.githubusercontent.com/29038590/224319908-c05b9f86-2862-4c65-9e34-07cfd14891ae.png)
![2](https://user-images.githubusercontent.com/29038590/224319927-d35be0f6-dc58-49de-b7e5-b6a0f5259b98.png)
![3](https://user-images.githubusercontent.com/29038590/224319940-10b793d6-67f6-4657-8985-089e2664a412.png)
