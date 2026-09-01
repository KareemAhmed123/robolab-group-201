def printCurrentStep():
    print("Current expansion:",current+1)
    toBePrinted = set()
    for key, value in explored.items():
        toBePrinted.add((key+1, value[0], value[1]+1))
    print("Explored:  ",toBePrinted)

    toBePrinted = set()
    for key, value in neighbourhoodKnots.items():
        toBePrinted.add((key+1, value[0], value[1]+1))
    print("Neighbours:",toBePrinted)
    print()
    
map1 = [
    [0, 3, float('inf'), 5, float('inf'), float('inf'), float('inf')], #0
    [float('inf'), 0, 5, float('inf'), 4, float('inf'), float('inf')],
    [float('inf'), float('inf'), 0, float('inf'), 2, 3, float('inf')],
    [float('inf'), float('inf'), 1, 0, float('inf'), float('inf'), float('inf')],
    [float('inf'), float('inf'), float('inf'), float('inf'), 0, float('inf'), 5],
    [float('inf'), float('inf'), float('inf'), 2, float('inf'), float('inf'), 2],
    [float('inf'), float('inf'), float('inf'), float('inf'), float('inf'), float('inf'), 0]
]
map2 = [
    [0, 3, 4, 11, float('inf'), float('inf')],
    [float('inf'), 0, 3, float('inf'), 5, float('inf')],
    [float('inf'), 1, 0, 7, float('inf'), 1],
    [float('inf'), float('inf'), float('inf'), 0, 1, float('inf')],
    [float('inf'), float('inf'), float('inf'), 1, 0, float('inf')],
    [float('inf'), float('inf'), float('inf'), 3, float('inf'), 0]
]
map3 = [
    [0, 1, float('inf'), float('inf'), float('inf'), float('inf'), float('inf'), float('inf')],
    [float('inf'), 0, float('inf'), float('inf'), 2, 11, float('inf'), float('inf')],
    [7, float('inf'), 0, 2, float('inf'), float('inf'), 6, float('inf')],
    [4, float('inf'), float('inf'), 0, 7, float('inf'), 1, float('inf')],
    [float('inf'), 2, float('inf'), float('inf'), 0, float('inf'), float('inf'), 3],
    [float('inf'), float('inf'), float('inf'), float('inf'), float('inf'), 0, float('inf'), float('inf')],
    [float('inf'), float('inf'), float('inf'), float('inf'), float('inf'), float('inf'), 0, 13],
    [float('inf'), float('inf'), float('inf'), float('inf'), float('inf'), 4, float('inf'), 0]
]

map = map1

# has to be n x n

eingabe = 0


while eingabe >= 0:
    print()
    print("MAIN MENU")
    print("1  = show hole map")
    print("2  = set up a new map")
    print("3  = execute shortest path")
    print("4  = execute Dijkstra")
    print("-1 = quit")
    eingabe = int(input(""))
    print()

    if eingabe == 1:
        for row in range(len(map)):
            for column in range(len(map)):
                if map[row][column] == float('inf'):
                    print('\u221E', end='\t')
                else:
                    print(map[row][column], end='\t')
            print()
    
    if eingabe == 2:
        map = []
        print("The map has to contain as much rows as columns.")
        n = int(input("#rows = #columns = "))
        for row in range(n):
            print("We are about to record row ", row, ". Please enter all values seperated by ENTER. -1 means ", '\u221E', ".", sep="")
            row_array = []
            for column in range(n):
                value = int(input())
                if value == -1:
                    row_array.append(float('inf'))
                else:
                    row_array.append(value)
            map.append(row_array)


    if eingabe == 3:
        for step in range(len(map)): # Zeile step und Spalte step
            for row in range(len(map)):
                for column in range(len(map)):
                    if map[step][column] + map[row][step] < map[row][column]:
                        print("row", row, "column", column, "was updated from", map[row][column], "\tto", map[step][column] + map[row][step])
                        map[row][column] = map[step][column] + map[row][step]
        print("Shortest path was executed successfully")
    
    if eingabe == 4:
        print("Please enter from which knot you want to start. ATTENTION: Numeration starts with 1.")
        start = int(input())-1
        print()
        predecessor = -2 # -2 means the starting knot
        current = start
        neighbourhoodKnots = dict()
        explored = dict()
        explored[current] = (0, -2) # -2 means starting point

        for column in range(len(map)):
            if map[current][column] != float('inf') and map[current][column] != 0:
                neighbourhoodKnots[column] = (map[start][column], current)
        printCurrentStep()

        while 1:
            if not neighbourhoodKnots:
                break
            predecessor = current
            current = next(iter(neighbourhoodKnots)) # random next element
            explored[current] = neighbourhoodKnots[current] # add to explored
            del neighbourhoodKnots[current] # delete from neighbourhood
            costToReachCurrentKnot = explored[current][0]
            for column in range(len(map)):
                if map[current][column] != float('inf') and map[current][column] != 0: # see where you can go from this new knot
                    if column in neighbourhoodKnots:
                        if (costToReachCurrentKnot + map[current][column] < neighbourhoodKnots[column][0]): # found shorter path
                            neighbourhoodKnots[column] = (costToReachCurrentKnot + map[current][column], current)
                    #elif column == start:
                    #    ()
                    else:
                        if column in explored:
                            if (costToReachCurrentKnot + map[current][column] < explored[column][0]): # found shorter path
                                explored[column] = (costToReachCurrentKnot + map[current][column], current)
                        else:
                            neighbourhoodKnots[column] = (costToReachCurrentKnot + map[current][column], current)
            
            printCurrentStep()

            if not neighbourhoodKnots:
                break
            
        print("Destination\tlength\t\tvia")
        for key, value in explored.items():
            destination = predecessor = key
            length = value[0]
            via = [value[1]]
            while -2 not in via:
                predecessor = explored[predecessor][1]
                via.append(explored[predecessor][1])
            via.pop() # remove -2
            via.reverse()
            via.append(destination)
            destination += 1 # make it better readable since counting starts with 1
            for i in range(len(via)):
                via[i] += 1
            print(destination,"\t\t",length,"\t\t",via,sep="")