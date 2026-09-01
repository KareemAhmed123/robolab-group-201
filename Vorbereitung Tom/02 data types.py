var2 = True
var3 = 10.023
var4 = 10+3j

str = "Hello World"
print(str[0], str[2:5], str[2:], str * 2, str + "Test")
#                 t to 5    3 and after   append

list = ['abcd', 789, 2.23]
print(list[1])

tuple = ('abcd', 789, 2.23)
# tuple 1 + tuple 2 works

for i in range(5): # 0 <= i <= 4
    print(i)

# <=>

for i in range(0,5,1):
    print(i)


# bytes data types

b = b'Hello'
print(b) # b'Hello'

# sets

set = {123, "Test", 456}
print(set)

# dictionary

capitals = {"USA":"New York", "Germany":"Berlin"}
print(capitals)
print(capitals.keys())
print(capitals.values())

print(not "USA" in capitals.keys()) # False
for country in capitals.keys():
    print(country)
# for k, v in capitals.items()


a = "1"
b = int(a)
b += 1
print(b)

# binary to int

a = int("110011", 2) # Basis 2, geht auch mit 8 oder 16

# unicode

var = "\u00BE"