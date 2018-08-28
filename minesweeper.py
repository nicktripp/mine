# Python 3
import sys
import random
import numpy as np

## Setup game parameters
# Flags
BOMB = -1
EMPTY = 0
UNVISIT = -2
FLAG = -3
QUEST = -4
BOMB_HIGHLIGHT = -5
P_FORMAT = {BOMB: "*", EMPTY: ".", UNVISIT: " ", FLAG: "!", QUEST: "?", BOMB_HIGHLIGHT: "\u2605"}

def main():
    if sys.version_info[0] < 3:
        raise Exception("Must be using Python 3")

    program_name = sys.argv[0]
    args = sys.argv[1:]
    argc = len(args)

    if (argc != 2):
        sys.exit("Usage: " + program_name + " <grid size> <bomb count>")

    grid_size = int(args[0])
    bomb_count = int(args[1])

    if (bomb_count > grid_size**2):
        # Too many bombs
        print("Bomb count must be less than (grid size)^2!", file=sys.stderr)
        sys.exit("Usage: " + program_name + " <grid size> <bomb count>")

    # Generating bombs
    bomb_seq = [BOMB]*bomb_count
    bomb_seq += [EMPTY]*(grid_size**2 - bomb_count)
    random.shuffle(bomb_seq)

    # Reform board
    grid = np.reshape(bomb_seq, (grid_size,grid_size))

    # Update numbers
    neighbors = [(x,y) for x in [-1,0,1] for y in [-1,0,1] if not (x == 0 and y == 0)]
    for y in range(grid_size):
        for x in range(grid_size):
            if(grid[x,y] == BOMB):
                # Update non-bomb neighbors
                for (i,j) in neighbors:
                    if x+i >= 0 and x+i < grid_size and y+j >= 0 and y+j < grid_size and grid[x+i,y+j] != BOMB:
                        grid[x+i,y+j] += 1

    # ------
    # Visual Test
    # print("Bomb Count: {}\nGrid Size: {}".format(bomb_count,grid_size))
    # print_board(grid)
    # ------

    # Setup player markdown
    revealed = np.full((grid_size, grid_size), False)
    markdown = np.full((grid_size, grid_size), UNVISIT)
    flag_count = 0

    ## Main game loop
    lost = False
    lostBomb = (-1,-1)
    won = False
    while(not (lost or won)):
        # Check if won
        squares_checked = np.count_nonzero(revealed)
        if squares_checked == grid_size**2 - bomb_count:
            won = True
            continue

        # Print status
        print_unrevealed_board(grid, revealed, markdown)
        print("Total Bombs: {}\nBombs Marked: {}\n".format(bomb_count, flag_count))

        # Get input
        cmd = input("> ")
        cmd_args = cmd.split()
        cmd_argc = len(cmd_args)

        # print("Recieved {} cmd args. First arg: |{}|".format(cmd_argc, cmd_args[0].upper()))
        print()

        if (cmd_argc <= 0):
            print_cmd_help()
            continue

        # Mark
        if(cmd_args[0].upper() == "M" or cmd_args[0].upper() == "MARK"):
            if not (cmd_argc == 3 or cmd_argc == 4):
                print_cmd_help("MARK: incorrect arg count")
                continue

            try:
                x = int(cmd_args[1])
                y = int(cmd_args[2])
            except ValueError:
                print_cmd_help("MARK: x and y must be ints")
                continue
            if(x < 0 or y < 0 or x >= grid_size or y >= grid_size):
                print_cmd_help("MARK: x and y out of bounds")
                continue
            elif(revealed[x,y]):
                print("(x,y) already revealed, so nothing was marked.\n")
                continue

            if (cmd_argc == 3):
                if markdown[x,y] == FLAG:
                    flag_count -= 1
                markdown[x,y] = UNVISIT
            elif (cmd_argc == 4):
                if (cmd_args[3] not in "?!"):
                    print_cmd_help("MARK: markdown must be ? or !")
                    continue
                mark = cmd_args[3]
                if mark == "?":
                    markdown[x,y] = QUEST
                elif mark == "!":
                    markdown[x,y] = FLAG
                    flag_count += 1

        # Press
        elif(cmd_args[0].upper() == "P" or cmd_args[0].upper() == "PRESS"):
            if (cmd_argc != 3):
                print_cmd_help("PRESS: incorrect arg count")
                continue

            try:
                x = int(cmd_args[1])
                y = int(cmd_args[2])
            except ValueError:
                print_cmd_help("PRESS: x and y must be ints")
                continue
            if(x < 0 or y < 0 or x >= grid_size or y >= grid_size):
                print_cmd_help("MARK: x and y out of bounds")
                continue

            # Check if lost
            if(grid[x,y] == BOMB):
                lost = True
                lostBomb = (x,y)
                continue

            # Check if Empty
            elif(grid[x,y] == EMPTY):
                # Flood fill all adjacent empty squares
                stack = [(x,y)]
                while (len(stack) > 0):
                    curr = stack.pop()
                    (currX, currY) = curr
                    if(currX < 0 or currY < 0 or currX >= grid_size or currY >= grid_size):
                        continue
                    elif revealed[curr] == False:
                        revealed[curr] = True
                        if grid[curr] == EMPTY:
                            stack += [(currX+i,currY+j) for (i,j) in neighbors]

            revealed[x,y] = True

        # Rest
        elif(cmd_args[0].upper() == "REST"):
            if (cmd_argc != 1):
                print_cmd_help("REST: incorrect arg count")
                continue

            for y in range(grid_size):
                for x in range(grid_size):
                    if markdown[x,y] != FLAG:
                        # Check if lost
                        if(grid[x,y] == BOMB):
                            lost = True
                            lostBomb = (x,y)

                        revealed[x,y] = True

        # CMD Error
        else:
            print_cmd_help()
            continue

    # Finish up
    if (lost):
        grid[lostBomb] = BOMB_HIGHLIGHT
        print_board(grid)
        print("\n*** YOU LOST ***\n")
    else:
        print_board(grid)
        print("\n*** YOU WON! ***\n")

def print_cmd_help(err_msg=""):
    print(err_msg)
    print("Usage:")
    print(" mark <x> <y> [?|!]\t# Marks square (x,y). No markdown clears markdown")
    print(" press <x> <y>\t\t# Presses square (x,y) permanently")
    print(" rest\t\t\t# Presses all squares not flagged")
    print()

def print_board(board):
    size = len(board)
    print("\n    ", end="")
    for i in range(size):
        print("{:^3} ".format(i), end="")

    print("\n   ."+"---|"*(size-1)+"---.")

    for y in range(size):
        print("{:^3}|".format(y), end="")
        for x in range(size):
            print("{:^3}|".format(P_FORMAT[board[x,y]] if board[x,y] <= 0 else board[x,y]), end="")
        print("")
        if y < (size - 1):
            print("   |" + "---|" * size)

    print("   `"+"---|"*(size-1)+"---`")

def print_unrevealed_board(board, revealed, markdown):
    part_board = np.where(revealed, board, markdown)
    print_board(part_board)

main()
