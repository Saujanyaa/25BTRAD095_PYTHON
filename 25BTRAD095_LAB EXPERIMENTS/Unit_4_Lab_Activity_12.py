
FILE = "students.txt"

while True:
    print("\n--- STUDENT DATA MANAGER ---")
    print("1. Add Student")
    print("2. Search Student")
    print("3. Update Student")
    print("4. Display Students")
    print("5. Exit")

    choice = input("Enter your choice: ")

    if choice == "1":
        name = input("Enter name: ")
        roll = input("Enter roll number: ")
        marks = input("Enter marks: ")

        with open(FILE, "a") as f:
            f.write(name + "," + roll + "," + marks + "\n")

        print("Student added successfully!")

    elif choice == "2":
        roll = input("Enter roll number to search: ")
        found = False

        try:
            with open(FILE, "r") as f:
                for line in f:
                    name, r, marks = line.strip().split(",")

                    if r == roll:
                        print("Name:", name)
                        print("Roll Number:", r)
                        print("Marks:", marks)
                        found = True
                        break

            if not found:
                print("Student not found!")

        except FileNotFoundError:
            print("No student records found!")

    elif choice == "3":
        roll = input("Enter roll number to update: ")
        found = False
        records = []

        try:
            with open(FILE, "r") as f:
                for line in f:
                    name, r, marks = line.strip().split(",")

                    if r == roll:
                        marks = input("Enter new marks: ")
                        found = True

                    records.append(name + "," + r + "," + marks + "\n")

            if found:
                with open(FILE, "w") as f:
                    f.writelines(records)
                print("Student record updated!")
            else:
                print("Student not found!")

        except FileNotFoundError:
            print("No student records found!")

    elif choice == "4":
        try:
            with open(FILE, "r") as f:
                print("\nStudent Records:")
                for line in f:
                    print(line.strip())

        except FileNotFoundError:
            print("No student records found!")

    elif choice == "5":
        print("Exiting Student Data Manager.")
        break

    else:
        print("Invalid choice!")
