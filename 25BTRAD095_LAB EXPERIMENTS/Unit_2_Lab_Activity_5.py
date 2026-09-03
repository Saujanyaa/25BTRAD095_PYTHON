import random

n = int(input("Guess a number between 50 and 100 : "))
x = random.randint(50,100)

print("The correct number is", x)
if x==n:
    print("You guessed it right!")
else:
    print("Wrong guess!")