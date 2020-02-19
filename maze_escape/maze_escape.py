#!/usr/bin/python

'''
    @author Managarmr
    @version 1.0
    @code IA for maze escape
    @date 06/02/2020 
'''

# import
import argparse
import random

# get parameters
def argparser():
    '''
        parameters function
    '''
    parser = argparse.ArgumentParser(description='file to create maze')
    parser.add_argument('file',help='maze structure')
    parser.add_argument('--verbose',help='verbose mode',action='store_true')
    parser.add_argument('--display',help='a simple display mode',action='store_true')
    return parser.parse_args()

# define maze
class Maze:
    def __init__(self,file):
        '''
            init maze class
            @file: txt file describing maze        
        '''
        self.file = file
        self.maze,self.size = self.__initMaze__()

    def __initMaze__(self):
        '''
            get maze structure
            @return int array, size of maze
        '''
        maze = []
        width = 0
        file = open(self.file,'r')
        for line in file:
            width += 1
            for element in line:
                # add wall
                if (element == "X"):
                    maze.append(1)
                # add escape
                elif (element == "s"):
                    maze.append(2)
                # add bot
                elif (element == "r"):
                    maze.append(3)
                elif (element == "\n"):
                    pass
                # free
                else:
                    maze.append(0)
        return maze,(width,len(line))

    def getSize(self):
        '''
            get size of maze
            @return a tuple of int
        '''
        return self.size

    def getMaze(self):
        '''
            get maze structure
            @return int array
        '''
        return self.maze

    def getStart(self):
        '''
            get start position of bot
            @return an int
        '''
        return self.maze.index(3)

    def print(self):
        '''
            print maze structure
        '''
        print(self.size)
        for w in range(self.size[0]):
            line = []
            for h in range(self.size[1]):
                line.append(self.maze[w*self.size[1]+h])
            print(line)

# bot exploring the maze
class Bot:
    def __init__(self,maze,display):
        '''
            create a bot
            @maze: maze struct
            @display: display mode
        '''
        self.countMove = 0
        self.maze = maze
        self.action = ['up','down','left','right']
        self.learningRate = 0.8
        self.discountFactor = 0.8
        self.display = display
        self.state = maze.getStart() # at the beginning, the bot is in start position
        self.qMatrix = [[0 for i in range(len(self.action))] for j in range(self.maze.getSize()[1]*self.maze.getSize()[0])]

    def bellman(self,state,action,maze):
        '''
            update q table with bellman action
            @state: the actual state of the bot
            @action: the selected action
            @maze: maze structure
        '''
        actionRealized = self.action[action]

        # check the action realized
        if (actionRealized == 'up'):
            newState = state - self.maze.size[1]
        elif (actionRealized == 'down'):
            newState = state + self.maze.size[1]
        elif (actionRealized == 'left'):
            newState = state - 1
        else:
            newState = state + 1 

        # give a reward for the action
        rewardNewState = 0
        if (maze[newState] == 1): # the new state is a wall
            rewardNewState = -1
        elif (maze[newState] == 2): # the new state is the exit
            rewardNewState = 1

        # update q table with bellman equation
        self.qMatrix[state][action] += self.learningRate * (rewardNewState + self.discountFactor * max(self.qMatrix[newState]) - self.qMatrix[state][action])

        if (rewardNewState == -1):
            return state
        return newState

    def explore(self,maxGames):
        '''
            bot exploring the maze
            @maxGames: stop the exploration
        '''
        maze = self.maze.getMaze()
        epsilon = 1
        gameCount = 0
        state = self.state

        while (gameCount < maxGames):
            r = random.random()

            # select a random action
            if (r <= epsilon):
                action = random.randrange(0,4)
            # select the best action based on q table
            else:
                action = self.qMatrix[state].index(max(self.qMatrix[state]))
            newState = self.bellman(state,action,maze)

            # moving bot
            if not(newState == state):
                maze[state] = 0
                maze[newState] = 3 if not (maze[newState] == 2) else 2
            state = newState

            # find the exit
            if (maze[state] == 2):
                epsilon *= 0.95
                gameCount += 1
                state = self.state
                maze[state] = 3
                print("=============>",gameCount)

    def bestWay(self):
        '''
            after exploring, select the best way with q table
        '''
        maze = self.maze.getMaze()
        state = self.state
        solution = []

        if (self.display):
            for w in range(self.maze.size[0]):
                line = []
                for h in range(self.maze.size[1]):
                    line.append(maze[w*self.maze.size[1]+h])
                print(line)
            print("===============")

        while not(maze[state] == 2):
            action = self.qMatrix[state].index(max(self.qMatrix[state]))

            actionRealized = self.action[action]
            maze[state] = 0
            solution.append((state,actionRealized))

            if (actionRealized == 'up'):
                state -= self.maze.size[1]
            elif (actionRealized == 'down'):
                state += self.maze.size[1]
            elif (actionRealized == 'left'):
                state -= 1
            else:
                state += 1

            maze[state] = 3 if not (maze[state] == 2) else 2

            if (self.display):
                for w in range(self.maze.size[0]):
                    line = []
                    for h in range(self.maze.size[1]):
                        line.append(maze[w*self.maze.size[1]+h])
                    print(line)
                print("===============")

        print(solution)

# main
def main():
    arg = argparser()
    mazeFile = arg.file
    verbose = arg.verbose
    display = arg.display

    maze = Maze(mazeFile)

    if (display):
        maze.print()

    bot = Bot(maze,display)

    bot.explore(10)

    if (verbose):
        print(bot.qMatrix)

    bot.bestWay()

if __name__ == "__main__":
    main()