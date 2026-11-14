
import random

while True:
    print("\n--- DICE SIMULATOR ---")

    n = int(input("Enter number of dice to roll: "))

    if n <= 0:
        print("Enter a valid number of dice!")
        continue

    for i in range(n):
        result = random.randint(1, 6)
        print("Dice", i + 1, ":", result)

    choice = input("Roll again? (yes/no): ")

    if choice.lower() != "yes":
        print("Thank you!")
        break
