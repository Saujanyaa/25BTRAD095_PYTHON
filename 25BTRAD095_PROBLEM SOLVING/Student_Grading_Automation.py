d = {}
tm = ()
tg = ()
l = []
s = ()

n = int(input("Enter the number of students : "))
for i in range(n):
    print(f"\nEnter the details of Student {i+1}")
    rollno = int(input("Roll No. : "))
    name = input("Name of the Student : ")
    print("\nEnter the marks for the following subjects : ")
    os = float(input("Operating System : "))
    coa = float(input("Computer Organization and Architecture : "))
    dmgt = float(input("Discrete Mathematics and Graph Theory : "))
    pp = float(input("Python Programming : "))
    dt = float(input("Design Thinking : "))
    
    avg = (os+coa+dmgt+pp+dt)/5
    if avg >= 95:
        g = "O"
    elif avg >= 90:
        g = "A+"
    elif avg >= 85:
        g = "A"
    elif avg >= 80:
        g = "B+"
    elif avg >= 75:
        g = "B"
    elif avg >= 70:
        g = "C+"
    elif avg >= 65:
        g = "C"
    else:
        g = "D"  

    s = (rollno,name)
    tm = (os, coa, dmgt, pp, dt)
    tg = (g)
    l = [tm,tg]
    d[s] = l

print()
print("Grades : ")
for i in d:
    print(i, ":", d[i])
    
      


        
