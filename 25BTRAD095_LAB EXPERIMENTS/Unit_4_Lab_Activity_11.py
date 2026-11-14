
try:
    file = open(r"C:\Users\sauja\OneDrive\Documents\application.log.txt", "r")

    error = 0
    warning = 0
    info = 0

    for line in file:
        if "ERROR" in line:
            error += 1
        elif "WARNING" in line:
            warning += 1
        elif "INFO" in line:
            info += 1

    file.close()

    print("Log File Summary")
    print("ERROR:", error)
    print("WARNING:", warning)
    print("INFO:", info)

except FileNotFoundError:
    print("Log file not found!")

except PermissionError:
    print("Permission denied!")
