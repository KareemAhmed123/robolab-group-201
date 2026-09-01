"""
reserved memory locations, each with an address, case-sensitive

<class 'str'>
<class 'int'>
<class 'float'>

Variablen mit dem gleichen Wert werden als unterschiedliche Objekte angesehen
"""

month="May"
print(id(month)) # print address
print(type(month))
del month

x = str(10)
print("x =", x) # x = 10

a,b,c = 10,20,30
print(a,b,c) # 10 20 30

a=b=c=5
def sum(x,y,z):
    sum = x+y+z
    return sum

print(sum(a,b,c))
print(a is b) # Objekte haben gleiche Speicheradresse, True