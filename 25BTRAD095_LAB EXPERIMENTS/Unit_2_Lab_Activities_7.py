n = int(input("Enter a number : "))
n -= 2
a = 0
b = 1
print(a,",",b, end = " , ")
while n:
    c = a+b
    if n == 1:
        print(c)
    else:
        print(c, end=" , ")
    a = b
    b = c
    n -= 1 