map = [
    [0, -1, 3, -1, -1, -1, -1],
    [8, 0, -1, 2, -1, -1, -1],
    [-1, -1, 0, -1, -1, -1, -1],
    [4, -1, 8, 0, -1, 3, 6],
    [-1, 4, -1, 7, 0, -1, 15],
    [-1, -1, 3, -1, -1, 0, 2],
    [-1, -1, -1, -1, -1, -1, 0],
]
# has to be n x n

eingabe = 0


while eingabe >= 0:
    print()
    print("MAIN MENU")
    print("1  = show hole map")
    print("2  = set up a new map")
    print("3  = execute")
    print("-1 = quit")
    eingabe = int(input(""))
    print()

    if eingabe == 1:
        for row in range(len(map)):
            for column in range(len(map)):
                if map[row][column] == -1:
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
                row_array.append(value)
            map.append(row_array)


    if eingabe == 3:
        for step in range(len(map)): # Zeile step und Spalte step
            for row in range(len(map)):
                if row != step:
                    for column in range(len(map)):
                        if column != step:
                            if map[step][column] != -1 and map[row][step] != -1:
                                if map[step][column] + map[row][step] < map[row][column] or map[row][column] == -1:
                                    print("row", row, "column", column, "was updated from", map[row][column], "\tto", map[step][column] + map[row][step])
                                    map[row][column] = map[step][column] + map[row][step]
        print("Shortest path was executed successfully")