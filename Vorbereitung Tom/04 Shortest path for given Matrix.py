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
    print("2  = execute")
    print("-1 = quit")
    eingabe = int(input(""))
    print()

    if eingabe == 1:
        for i in range(len(map)):
            for j in range(len(map)):
                if map[i][j] == -1:
                    print('\u221E', end='\t')
                else:
                    print(map[i][j], end='\t')
            print()
    
    if eingabe == 2:
        for step in range(len(map)): # Zeile step und Spalte step
            for i in range(len(map)):
                if i != step:
                    for j in range(len(map)):
                        if j != step:
                            if map[step][j] != -1 and map[i][step] != -1:
                                if map[step][j] + map[i][step] < map[i][j] or map[i][j] == -1:
                                    print("row", i, "column", j, "is updated from", map[i][j], "\tto", map[step][j] + map[i][step])
                                    map[i][j] = map[step][j] + map[i][step]
        print("Shortest path was executed successfully")