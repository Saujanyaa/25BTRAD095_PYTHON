from datetime import datetime, date

Time = datetime.now().strftime("%H:%M:%S")
Date = datetime.now().strftime("%d%m%Y")
Today = date.today()
Inv_count = 1

Invoice = f"INV-{Date}-{Inv_count:03d}"

items = {101:"Pen",102:"Pencil",103:"Eraser",104:"Ruler",105:"Marker",106:"Stapler",107:"Whitener",108:"Glue",109:"Scissors",110:"Cello Tape"}
price = {101:20, 102:10, 103:3, 104:5, 105:20, 106:30, 107:30, 108:20, 109:40, 110:25}

print("PRODUCTS LIST")
for i in items:
    print(f"{i:<5}:   {items[i]}")

st = 0.0
l=[]

print()
while True:
    print("1.ADD ITEMS\n2.REMOVE ITEM\n3.GENERATE BILL")
    a = int(input("What would you like to do? : "))
    print()

    if a==1:
        x = 1
        print("Enter '0' to stop adding items")
        while x:
            x = int(input("Enter product ID : "))
            if x==0:
                break
            if x not in items:
                print("Please enter a valid product ID") 
            else:
                q = int(input("Enter quantity : "))
                if x in [i[0] for i in l]:
                    for index, i in enumerate(l):
                        if x == i[0]:
                            old_q = i[2]
                            new_q = old_q + q
                            l[index] = (x, items[x], new_q, price[x])
                            st += price[x]*q
                            break
                else:
                    p = price[x]
                    l.append((x,items[x],q,p))
                    st += price[x]*q
        print("Items added!")
        print()
        
    if a==2:
        rp = 0
        r = int(input("Enter product ID to be removed : "))
        for index, i  in enumerate(l):
            if i[0] == r:
                del l[index]
                st -= i[2]*i[3]
                rp = 1
        if rp == 0:
            print("The product doesn't exist in the added items list")
        else:
            print("Product removed")
        print()

    if a==3:
        gst = 0.18
        GST = st*gst
        gt = GST + st

        if gt >= 100:
            D = gt*0.05
            GT = gt - D
        else:
            D = 0.0
            GT = gt

        print("="*50)
        print(" "*22,"BILL"," "*22)
        print("="*50)
        print(f"{"Date : " + str(Today):<25} {"Time : " + str(Time):>25}")
        print(f"{"Invoice number : " + Invoice:^50}")

        print("-"*50)
        print(f"{"Sl. No.":<8}{"Item Name":<12}{"Qty":<5}{"Unit Price":<13}{"Total":<10}")
        print("-"*50)

        for index, i in enumerate(l, start=1):
            print(f"{index:^8d}{i[1]:<12}{i[2]:<5d}{i[3]:<13.2f}{i[2]*i[3]:<10.2f}")

        print("-"*50)
        print(f"{"Subtotal":>29}   : {st:>10.2f}")
        print(f"{"GST(18%)":>29}   : {GST:>10.2f}")
        print(f"{"Discount":>29}   : {D:>10.2f}")
        print(f"{"Grand Total":>29}   : {GT:>10.2f}")
        print("-"*50)

        Inv_count += 1

        break

