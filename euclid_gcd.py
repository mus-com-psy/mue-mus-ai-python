def mystery(a, b):
    a = abs(a)
    b = abs(b)
    while b != 0:
        while a > b:
            a = a - b
        b = b - a
    return a

ans = mystery(96, 42)
print(ans)
