
class Book:
    def __init__(self, title, author):
        self.title = title
        self.author = author
        self.available = True

    def issue(self):
        if self.available:
            self.available = False
            print("Book issued successfully!")
        else:
            print("Book is not available!")

    def return_book(self):
        if not self.available:
            self.available = True
            print("Book returned successfully!")
        else:
            print("Book was not issued!")

    def display(self):
        print("Title:", self.title)
        print("Author:", self.author)

        if self.available:
            print("Status: Available")
        else:
            print("Status: Issued")


book = Book("Python Programming", "Guido van Rossum")

while True:
    print("\n--- LIBRARY MANAGEMENT SYSTEM ---")
    print("1. Display Book")
    print("2. Issue Book")
    print("3. Return Book")
    print("4. Exit")

    choice = input("Enter your choice: ")

    if choice == "1":
        book.display()

    elif choice == "2":
        book.issue()

    elif choice == "3":
        book.return_book()

    elif choice == "4":
        print("Exiting Library System.")
        break

    else:
        print("Invalid choice!")
