
products = {}

while True:
    print("\n--- SALES DATA ANALYZER ---")
    print("1. Add Product")
    print("2. Update Sales")
    print("3. Display Sales")
    print("4. Calculate Total Sales")
    print("5. Highest Selling Product")
    print("6. Exit")

    choice = input("Enter your choice: ")

    if choice == "1":
        name = input("Enter product name: ")
        quantity = int(input("Enter quantity sold: "))
        price = float(input("Enter price per unit: "))

        if name in products:
            print("Product already exists!")
        elif quantity < 0 or price < 0:
            print("Invalid quantity or price!")
        else:
            products[name] = {
                "quantity": quantity,
                "price": price
            }
            print("Product added successfully!")

    elif choice == "2":
        name = input("Enter product name: ")

        if name in products:
            quantity = int(input("Enter new quantity sold: "))

            if quantity >= 0:
                products[name]["quantity"] = quantity
                print("Sales updated successfully!")
            else:
                print("Invalid quantity!")

        else:
            print("Product not found!")

    elif choice == "3":
        print("\n--- PRODUCT SALES ---")

        for name, details in products.items():
            revenue = details["quantity"] * details["price"]

            print("Product:", name)
            print("Quantity:", details["quantity"])
            print("Price:", details["price"])
            print("Revenue:", revenue)

    elif choice == "4":
        total = 0

        for details in products.values():
            total += details["quantity"] * details["price"]

        print("Total Sales Revenue:", total)

    elif choice == "5":
        if len(products) == 0:
            print("No products available!")
        else:
            highest = max(
                products,
                key=lambda name: products[name]["quantity"]
            )

            print("Highest Selling Product:", highest)
            print("Quantity Sold:", products[highest]["quantity"])

    elif choice == "6":
        print("Exiting Sales Data Analyzer.")
        break

    else:
        print("Invalid choice!")
