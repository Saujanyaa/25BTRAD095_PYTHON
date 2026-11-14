
import csv

try:
    with open(r"C:\Users\sauja\employees.csv", "r", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)

        print("--- PAYROLL SUMMARY ---")

        for emp in reader:
            print("\nReading record:", emp)

            try:
                basic = float(emp["Basic_Salary"])

                hra = basic * 0.20
                da = basic * 0.10
                gross = basic + hra + da

                pf = basic * 0.12
                tax = gross * 0.05

                deductions = pf + tax
                net = gross - deductions

                print("Employee ID:", emp["ID"])
                print("Name:", emp["Name"])
                print("Basic Salary:", basic)
                print("Gross Salary:", gross)
                print("Deductions:", deductions)
                print("Net Salary:", net)

            except (ValueError, KeyError, TypeError):
                print("Invalid employee record:", emp)

except FileNotFoundError:
    print("Employee file not found!")
