from IPython.core.magic import on_off
from pickle import TRUE
from enum import Enum
import random
import numpy as np

class DoorState(Enum):
    CLOSED = 0
    OPEN = 1

class Cell:

    def __init__(self, x, y):
        self.xCor = x
        self.yCor = y
        self.status = DoorState.CLOSED
        self.onfire = False
        self.fireProbability = 0.0

    def __str__(self):
        return f'X:{self.xCor} Y:{self.yCor} status:{self.status}\n'

    def __repr__(self):
        return f'X:{self.xCor} Y:{self.yCor} status:{self.status}\n'

    def printState(self, botLocation, buttonLocation):
      if botLocation is not None and botLocation.xCor == self.xCor and botLocation.yCor == self.yCor:
        print ('■', end= '')
      elif buttonLocation is not None and buttonLocation.xCor == self.xCor and buttonLocation.yCor == self.yCor:
        print ('@', end= '')
      elif self.onfire:
        print('‡', end = '')
      else:
        if self.status == DoorState.CLOSED:
          print ('∅', end='')
        else:
          print ('O', end='')

D = 30  #size of Array
Q = 0.75  #flammability of the ship
def printArray(arr, botLocation, buttonLocation):
    for i in range(D):
        for j in range(D):
            arr[i][j].printState(botLocation, buttonLocation)
        print ('')

def checkifOneOpen(arr, x, y):
    i = 0
    if (x > 0 and arr[x-1][y].status == DoorState.OPEN):
        i += 1
    if (x < D-1 and arr[x+1][y].status == DoorState.OPEN):
        i += 1
    if (y > 0 and arr[x][y-1].status == DoorState.OPEN):
        i += 1
    if (y < D-1 and arr[x][y+1].status == DoorState.OPEN):
        i += 1
    if (i != 1):
        return False
    else:
        return True

# I don't think this is the best way to do things but I think it needs a slightly larger rewrite to fix.
# Would it not make sense to store location as part of Bot object?

def placeBot(arr):
    checkArr = np.zeros((D, D), dtype = int)
    found=False
    while (found == False):
        nextX = random.randint(0,D-1)
        nextY = random.randint(0,D-1)
        if (checkArr[nextX][nextY] == 0):
            if arr[nextX][nextY].status == DoorState.OPEN:
                selected=arr[nextX][nextY]
                found=True
            else:
                checkArr[nextX][nextY] = 1
                if np.any(checkArr == 0) != True:
                    break
    return selected

def openNextCell(arr):
    checkArr = np.zeros((D, D), dtype = int)
    found = False
    while (found == False):
        nextX = random.randint(0,D-1)
        nextY = random.randint(0,D-1)
        checkArr[nextX][nextY] = 1
        if (arr[nextX][nextY].status == DoorState.CLOSED and checkifOneOpen(arr, nextX, nextY) == True):
            #print(f'Opening at {nextX}, {nextY}')
            arr[nextX][nextY].status = DoorState.OPEN
            found = True
        if np.any(checkArr == 0) != True:
            break
    return found

def move_bot(botLocation, direction):
    x, y = botLocation.xCor, botLocation.yCor
    if direction == 'up' and y > 0 and matrix[y-1][x].status == DoorState.OPEN and not matrix[y-1][x].onfire:
        botLocation = matrix[y-1][x]
    elif direction == 'down' and y < D-1 and matrix[y+1][x].status == DoorState.OPEN and not matrix[y+1][x].onfire:
        botLocation = matrix[y+1][x]
    elif direction == 'left' and x > 0 and matrix[y][x-1].status == DoorState.OPEN and not matrix[y][x-1].onfire:
        botLocation = matrix[y][x-1]
    elif direction == 'right' and x < D-1 and matrix[y][x+1].status == DoorState.OPEN and not matrix[y][x+1].onfire:
        botLocation = matrix[y][x+1]
    return botLocation

# This is for map generation?

# for x values, 0 is the top line, 3 is the bottom line - for y values, 0 is the value all the way on the left, 3 is the value all the way on the right
def checkDeadEnd(arr, x, y):
  i = 0
  if (x > 0 and arr[x-1][y].status == DoorState.OPEN):
        i += 1
  if (x < D-1 and arr[x+1][y].status == DoorState.OPEN):
        i += 1
  if (y > 0 and arr[x][y-1].status == DoorState.OPEN):
        i += 1
  if (y < D-1 and arr[x][y+1].status == DoorState.OPEN):
        i += 1
  if (arr[x][y].status) == DoorState.OPEN and i == 1:
    return True;
  else:
    return False;

def startFire(arr, botLocation):
    checkArr = np.zeros((D, D), dtype = int)
    found=False
    while (found == False):
        nextX = random.randint(0,D-1)
        nextY = random.randint(0,D-1)
        if (checkArr[nextX][nextY] == 0):
            if arr[nextX][nextY].status == DoorState.OPEN and botLocation.xCor != nextX and botLocation.yCor != nextY:
                selected=arr[nextX][nextY]
                found=True
            else:
                checkArr[nextX][nextY] = 1
                if np.any(checkArr == 0) != True:
                    break
    return selected

def getProbabilityFire(arr):
  highestProbabilityCell = None
  for x in range (D - 1):
    for y in range (D - 1):
      burningCount = 0
      cell = arr[x][y]
      #print(f'Cell probability is: {str(cell)}')
      if cell.onfire == True or cell.status == DoorState.CLOSED:
        continue
      if (x > 0 and arr[x-1][y].onfire == True):
        burningCount += 1
      if (x < D-1 and arr[x+1][y].onfire == True):
        burningCount += 1
      if (y > 0 and arr[x][y-1].onfire == True):
        burningCount += 1
      if (y < D-1 and arr[x][y+1].onfire == True):
        burningCount += 1
      if burningCount == 0:
        cell.fireProbability = 0
      else:
        cell.fireProbability = 1 - (pow((1 - Q), burningCount))
      #print(f'Cell probability is: {cell.fireProbability} for {str(cell)}')
      if highestProbabilityCell is None:
        highestProbabilityCell = cell
      elif highestProbabilityCell.fireProbability < cell.fireProbability:
        highestProbabilityCell = cell
  return highestProbabilityCell

def placeButton(arr, botLocation):
    checkArr = np.zeros((D, D), dtype = int)
    found=False
    while (found == False):
        nextX = random.randint(0,D-1)
        nextY = random.randint(0,D-1)
        if (checkArr[nextX][nextY] == 0):
            if arr[nextX][nextY].status == DoorState.OPEN and botLocation.xCor != nextX and botLocation.yCor != nextY and arr[nextX][nextY].onfire == False:
                selected=arr[nextX][nextY]
                found=True
            else:
                checkArr[nextX][nextY] = 1
                if np.any(checkArr == 0) != True:
                    break
    return selected

matrix = [[Cell(i,j) for i in range(D)] for j in range(D)]

# print result
printArray(matrix, None, None)

startX = random.randint(0,D-1)
startY = random.randint(0,D-1)


print(f'Starting at {startX}, {startY}')
matrix[startX][startY].status = DoorState.OPEN
printArray(matrix, None, None)
print('')

# Ok this part is written after all of the stuff below that paragraph but this is the bot strat logic.

# Compartmentalized BFS

def find_shortest_path(matrix, source, destination):
    queue = [(source, [source])]
    visited = set([source])

    while queue:
        (vertex, path) = queue.pop(0)
        x, y = vertex.xCor, vertex.yCor
        for direction in ['up', 'down', 'left', 'right']:
            if direction == 'up' and y > 0:
                next_cell = matrix[y-1][x]
            elif direction == 'down' and y < D-1:
                next_cell = matrix[y+1][x]
            elif direction == 'left' and x > 0:
                next_cell = matrix[y][x-1]
            elif direction == 'right' and x < D-1:
                next_cell = matrix[y][x+1]
            else:
                continue

            if next_cell == destination:
                return path + [next_cell]
            elif next_cell.status == DoorState.OPEN and next_cell not in visited:
                visited.add(next_cell)
                queue.append((next_cell, path + [next_cell]))
    return None

# Static BFS, will run once, fill array and then instruct Bot to keep same path for rest of timestep

def strategy_1(matrix, botLocation, buttonLocation):
    if not strategy_1.path:
        strategy_1.path = find_shortest_path(matrix, botLocation, buttonLocation)
    return strategy_1.path.pop(0) if strategy_1.path else None
strategy_1.path = []

# Modified BFS used for Strategy 2, don't know if I can compartmentalize this in a smarter way to use 1st one or not.
# Actually I might be able to just use this one for the first as well, since there is yet to be fire at the beginning.

def find_shortest_path_avoid_fire(matrix, source, destination):
    queue = [(source, [source])]
    visited = set([source])

    while queue:
        (vertex, path) = queue.pop(0)
        x, y = vertex.xCor, vertex.yCor
        for direction in ['up', 'down', 'left', 'right']:
            if direction == 'up' and y > 0:
                next_cell = matrix[y-1][x]
            elif direction == 'down' and y < D-1:
                next_cell = matrix[y+1][x]
            elif direction == 'left' and x > 0:
                next_cell = matrix[y][x-1]
            elif direction == 'right' and x < D-1:
                next_cell = matrix[y][x+1]
            else:
                continue

            if next_cell == destination:
                return path + [next_cell]
            elif next_cell.status == DoorState.OPEN and not next_cell.onfire and next_cell not in visited:
                visited.add(next_cell)
                queue.append((next_cell, path + [next_cell]))
    return None

# Strategy 2, BFS accounting for fire, will rerun at every time step

def strategy_2(matrix, botLocation, buttonLocation):
    # Recompute the path in every timestep, avoiding cells that are on fire
    path = find_shortest_path_avoid_fire(matrix, botLocation, buttonLocation)
    return path[1] if path else None

def execute_bot_strategy(matrix, botLocation, buttonLocation, strategy):
    if strategy == 1:
        return strategy_1(matrix, botLocation, buttonLocation)
    elif strategy == 2:
        return strategy_2(matrix, botLocation, buttonLocation)
    elif strategy == 3:
        return strategy_3(matrix, botLocation, buttonLocation)
    elif strategy == 4:
        return strategy_3(matrix, botLocation, buttonLocation)

# Again, can probably shorten, but going hyper-verbose for now, will compress later.

def is_adjacent_to_fire(matrix, cell):
    x, y = cell.xCor, cell.yCor
    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        nx, ny = x + dx, y + dy
        if 0 <= nx < D and 0 <= ny < D and matrix[ny][nx].onfire:
            return True
    return False

def find_shortest_path_avoid_fire_and_adjacent(matrix, source, destination):
    queue = [(source, [source])]
    visited = set([source])

    while queue:
        (vertex, path) = queue.pop(0)
        x, y = vertex.xCor, vertex.yCor
        for direction in ['up', 'down', 'left', 'right']:
            if direction == 'up' and y > 0:
                next_cell = matrix[y-1][x]
            elif direction == 'down' and y < D-1:
                next_cell = matrix[y+1][x]
            elif direction == 'left' and x > 0:
                next_cell = matrix[y][x-1]
            elif direction == 'right' and x < D-1:
                next_cell = matrix[y][x+1]
            else:
                continue

            if next_cell == destination:
                return path + [next_cell]
            elif next_cell.status == DoorState.OPEN and not next_cell.onfire and not is_adjacent_to_fire(matrix, next_cell) and next_cell not in visited:
                visited.add(next_cell)
                queue.append((next_cell, path + [next_cell]))
    return None

# Strategy 3

def strategy_3(matrix, botLocation, buttonLocation):
    path = find_shortest_path_avoid_fire_and_adjacent(matrix, botLocation, buttonLocation)
    if not path:
        path = find_shortest_path_avoid_fire(matrix, botLocation, buttonLocation)
    return path[1] if path else None

def getPossibleFireCells(arr, threshold=0.1):
    possible_fire_cells = []
    for x in range(D):
        for y in range(D):
            burningCount = 0
            cell = arr[x][y]
            if cell.onfire == True or cell.status == DoorState.CLOSED:
                continue
            if (x > 0 and arr[x-1][y].onfire == True):
                burningCount += 1
            if (x < D-1 and arr[x+1][y].onfire == True):
                burningCount += 1
            if (y > 0 and arr[x][y-1].onfire == True):
                burningCount += 1
            if (y < D-1 and arr[x][y+1].onfire == True):
                burningCount += 1
            if burningCount == 0:
                cell.fireProbability = 0
            else:
                cell.fireProbability = 1 - (pow((1 - Q), burningCount))
            
            if cell.fireProbability >= threshold:
                possible_fire_cells.append(cell)
    return possible_fire_cells

def monte_carlo_simulation(matrix, bot_location, button_location, n_simulations=100):
    best_path = None
    lowest_risk = float('inf')
    
    for _ in range(n_simulations):
        # Clone current state to simulate future without affecting current state
        simulated_matrix = [row.copy() for row in matrix]
        
        # Identify cells that may catch fire
        fire_cells = getPossibleFireCells(simulated_matrix)
        
        # Randomly set some of them on fire
        for cell in fire_cells:
            if random.random() < cell.fireProbability:
                cell.onfire = True
        
        # Evaluate bot path under this fire scenario
        path = find_shortest_path_avoid_fire(simulated_matrix, bot_location, button_location)
        
        if path is not None:
            path_risk = evaluate_path_risk(path)
        
            # Update best path if this one is better
            if path_risk < lowest_risk:
                best_path, lowest_risk = path, path_risk
    
    return best_path

def evaluate_path_risk(path):
    return sum(cell.fireProbability for cell in path)

def find_nearest_fire(matrix, bot_location):
    queue = [(bot_location, [bot_location])]
    visited = set([bot_location])

    while queue:
        (vertex, path) = queue.pop(0)
        x, y = vertex.xCor, vertex.yCor
        for direction in ['up', 'down', 'left', 'right']:
            if direction == 'up' and y > 0:
                next_cell = matrix[y-1][x]
            elif direction == 'down' and y < D-1:
                next_cell = matrix[y+1][x]
            elif direction == 'left' and x > 0:
                next_cell = matrix[y][x-1]
            elif direction == 'right' and x < D-1:
                next_cell = matrix[y][x+1]
            else:
                continue

            if next_cell.onfire:
                return path + [next_cell]
            elif next_cell.status == DoorState.OPEN and next_cell not in visited:
                visited.add(next_cell)
                queue.append((next_cell, path + [next_cell]))
    return None

# Strategy 4
def strategy_4(matrix, bot_location, button_location):
    best_path = monte_carlo_simulation(matrix, bot_location, button_location)
    if best_path is None:
        print("No viable path to the button found. Reverting to BFS")
        best_path = find_nearest_fire(matrix, bot_location)
    return best_path[1] if best_path else None

def reset_fire(matrix):
    for row in matrix:
        for cell in row:
            cell.onfire = False

while openNextCell(matrix):
    print('next iteration')
    printArray(matrix, None, None)
    print('')

deadCellCt = 0
deadCells = []
for i in range(D):
  for j in range(D):
    if checkDeadEnd(matrix, i, j) == True:
      #print(f'Cell {i},{j} is a dead end')
      deadCells.append(matrix[i][j])
      deadCellCt += 1

if deadCellCt > 0 :
  if deadCellCt % 1 == 1:
    deadCellCt = int(deadCellCt/2 + 1)
  else:
    if deadCellCt % 1 == 0:
      deadCellCt = int(deadCellCt/2)

print (f'Flipping {deadCellCt} Cells')
for i in range(deadCellCt):
    found = False
    #check up
    cell = deadCells[i]
    checkArr = [0,0,0,0]
    while (found == False):
        #get a random number 0 through 4
        # 0 is left 1 is right 2 is up 3 is down
        j = random.randint(0, 3)
        if (j == 0 and cell.xCor > 0 and matrix[cell.yCor][cell.xCor-1].status == DoorState.CLOSED):
            matrix[cell.yCor][cell.xCor-1].status = DoorState.OPEN
            print(f'opening {cell.yCor}, {cell.xCor - 1}')
            found = True
        if (found == False and j == 1 and cell.xCor < D-1 and matrix[cell.yCor][cell.xCor+1].status == DoorState.CLOSED):
            matrix[cell.yCor][cell.xCor+1].status = DoorState.OPEN
            print(f'opening {cell.yCor}, {cell.xCor + 1}')
            found = True
        if (found==False and j == 2 and cell.yCor > 0 and matrix[cell.yCor-1][cell.xCor].status == DoorState.CLOSED):
            matrix[cell.yCor-1][cell.xCor].status = DoorState.OPEN
            print(f'opening {cell.yCor - 1}, {cell.xCor}')
            found = True
        if (found==False and j == 3 and cell.yCor < D-1 and matrix[cell.yCor+1][cell.xCor].status == DoorState.CLOSED):
            matrix[cell.yCor+1][cell.xCor].status = DoorState.OPEN
            print(f'opening {cell.yCor+1}, {cell.xCor}')
            found = True
        checkArr[j] = 1
        if checkArr[0] == 1 and checkArr[1] == 1 and checkArr[2] == 1 and checkArr[3] == 1 :
            break

printArray(matrix, None, None)
savedMatrix = matrix


# botLocation = botNextCell(matrix, cell)
# newFire = getProbabilityFire(matrix)
# print(f'Fire spreading to {str(newFire)}')
# if(botLocation.onfire == True):
#   print(f'dead, never to be seen again :p')
#   quit()
# if(botLocation.xCor == buttonLocation.xCor and botLocation.yCor == buttonLocation.yCor):
#   print(f'ship successfully saved!')
#   quit()
# newFire.onfire = True
# while newFire is not None:
#   print(f'Fire spreading to {str(newFire)}')
#   newFire.onfire = True
#   botLocation = botNextCell(matrix, botLocation)
#   newFire = getProbabilityFire(matrix)
#   printArray(matrix, cell, buttonLocation)
#   if(botLocation.onfire == True):
#     print(f'dead, never to be seen again :p')
#     quit()
#   if(botLocation.xCor == buttonLocation.xCor and botLocation.yCor == buttonLocation.yCor):
#     print(f'ship successfully saved!')
#     quit()



# For Real
def run_simulation():

  # Reset Matrix
  matrix = savedMatrix

  reset_fire(matrix)

  # Bot Setup
  cell = placeBot(matrix)
  print(f'Bot is Starting at {str(cell)}')
  botLocation = cell
  #printArray(matrix, cell, None)

  # Fire Setup
  fire = startFire(matrix, cell)
  print(f'Fire starting at {str(fire)}')
  fire.onfire = True
  #printArray(matrix, cell, None)

  # Button Setup
  buttonLocation = placeButton(matrix, cell)
  print(f'Button placed at {str(buttonLocation)}')
  #printArray(matrix, cell, buttonLocation)

  # Strategy Choice
  # while True:
  #     try:
  #         strategy_number = int(input("Designate which strategy you want to run (1,2,3,4): "))
  #         if strategy_number in [1, 2, 3, 4]:
  #             break
  #         else:
  #             print("Invalid input. Please enter a number between 1 and 4.")
  #     except ValueError:
  #         print("Invalid input. Please enter a number between 1 and 4.")

  # Time Step Setup
  time_step = 0
  time_out = 1000

  # Action Loop
  while time_step < time_out:
    #print(matrix)

    # End State Checks
    if botLocation is None:
      print("Bot cannot find a valid move. Task failed.")
      return "failure"
    if botLocation.onfire == True:
      print("Bot burned. Task failed.")
      return "failure"
    if botLocation == buttonLocation:
      print("Button pressed. Fire suppressed. Task completed successfully.")
      return "success"

    #Bot Move
    botLocation = execute_bot_strategy(matrix, botLocation, buttonLocation, strategy_number)
    print(f'Bot moving to {str(botLocation)}')

    # Fire Spread
    newFire = getProbabilityFire(matrix)
    print(f'Fire spreading to {str(newFire)}')
    newFire.onfire = True

    time_step += 1

  else:
    print("Timed Out")
    return "time_out"

success_count = 0
failure_count = 0
timeout_count = 0

simulation_count = 500
strategy_number = 3

for _ in range(simulation_count):
    result = run_simulation()
    if result == "success":
        success_count += 1
    elif result == "failure":
        failure_count += 1
    elif result == "timeout":
        timeout_count += 1

print(f"Out of {simulation_count} simulations:")
print(f"{success_count} were successful")
print(f"{failure_count} resulted in failure")
print(f"{timeout_count} timed out")
