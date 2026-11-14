
students = {}

while True:
    print("\n--- ATTENDANCE TRACKER ---")
    print("1. Add Student")
    print("2. Update Attendance")
    print("3. Display Attendance")
    print("4. Check Attendance Percentage")
    print("5. Exit")

    choice = input("Enter your choice: ")

    if choice == "1":
        name = input("Enter student name: ")

        if name in students:
            print("Student already exists!")
        else:
            students[name] = []
            print("Student added successfully!")

    elif choice == "2":
        name = input("Enter student name: ")

        if name in students:
            status = input("Enter attendance (P/A): ").upper()

            if status == "P" or status == "A":
                students[name].append(status)
                print("Attendance updated!")
            else:
                print("Invalid attendance status!")

        else:
            print("Student not found!")

    elif choice == "3":
        print("\n--- ATTENDANCE RECORDS ---")

        for name, records in students.items():
            print(name, ":", records)

    elif choice == "4":
        print("\n--- ATTENDANCE PERCENTAGE ---")

        threshold = float(input("Enter attendance threshold: "))

        for name, records in students.items():
            total = len(records)

            if total == 0:
                percentage = 0
            else:
                percentage = (records.count("P") / total) * 100

            print(name, ":", percentage, "%")

            if percentage < threshold:
                print("Below required attendance!")

    elif choice == "5":
        print("Exiting Attendance Tracker.")
        break

    else:
        print("Invalid choice!")
