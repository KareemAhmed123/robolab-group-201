map = [
    [0, float('inf'), 3, float('inf'), float('inf'), float('inf'), float('inf')],
    [8, 0, float('inf'), 2, float('inf'), float('inf'), float('inf')],
    [float('inf'), float('inf'), 0, float('inf'), float('inf'), float('inf'), float('inf')],
    [4, float('inf'), 8, 0, float('inf'), 3, 6],
    [float('inf'), 4, float('inf'), 7, 0, float('inf'), 15],
    [float('inf'), float('inf'), 3, float('inf'), float('inf'), 0, 2],
    [float('inf'), float('inf'), float('inf'), float('inf'), float('inf'), float('inf'), 0],
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