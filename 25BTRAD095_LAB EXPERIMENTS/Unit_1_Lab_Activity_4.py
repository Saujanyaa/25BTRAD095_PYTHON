#SIMPLE CALCULATOR
a = float(input("Enter 1st number : "))
b = float(input("Enter 2nd number : "))

x = "y"
while x=="y":
    print()
    print("1.ADD\n2.SUBTRACT\n3.MULTIPLY\n4.DIVIDE")
    c = int(input("Which operation would you like to perform? : "))

    if c==1:
        print(f"{a} + {b} = {a+b}")
    if c==2:
        print(f"{a} - {b} = {a-b}")
    if c==3:    
        print(f"{a} * {b} = {a*b}")
    if c==4:
        print(f"{a} / {b} = {a/b}")

    x = input("Would you like to perform another operation? (y/n) : ")



#AREA CALCULATION
a="y"
while a=="y":
    print()
    print("1.SQUARE\n2.RECTANGLE\n3.CIRCLE")
    c = int(input("Which shape would you like to calculate the area of? : "))

    if c==1:
        s = float(input("Enter the side of the square : "))
        print(f"Area of the square = {s**2}")
    if c==2:
        l = float(input("Enter the length of the rectangle : "))
        b = float(input("Enter the breadth of the rectangle : "))
        print(f"Area of the rectangle = {l*b}")
    if c==3:
        r = float(input("Enter the radius of the circle : "))
        print(f"Area of the circle = {3.14*r**2}")

    print()
    a = input("Would you like to calculate the area of another shape? (y/n) : ").lower()

