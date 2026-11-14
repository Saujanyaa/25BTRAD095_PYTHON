
students = {}

n = int(input("Enter number of students: "))

for i in range(n):
    name = input("\nEnter student name: ")
    marks = float(input("Enter marks: "))

    if marks >= 90:
        grade = "A"
    elif marks >= 80:
        grade = "B"
    elif marks >= 70:
        grade = "C"
    elif marks >= 60:
        grade = "D"
    else:
        grade = "F"

    students[name] = {
        "marks": marks,
        "grade": grade
    }

print("\n--- STUDENT RESULTS ---")

for name, details in students.items():
    print("Name:", name)
    print("Marks:", details["marks"])
    print("Grade:", details["grade"])
    print()
