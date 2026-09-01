def fn1():
    x = 3
    fn2(x)
    return x

def fn2(x):
    x += 4

print(fn1())