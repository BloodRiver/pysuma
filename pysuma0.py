# admin

admin = "sajeed"
password = "123@123"

# price, stock and initialization

price = {
    "apple": 10,
    "banana": 5,
    "papaya": 15,
    "strawberry": 20,
    "watermelon": 30
}

stock = {
    "apple": 12,
    "banana": 6,
    "papaya": 0,
    "strawberry": 15,
    "watermelon": 20
}

# purchase

items_bought = {}
purchase = str(0)
number = 0

# refund

refund_items = {}
refund_i = str(0)
refund_n = 0

# calculations

total = 0
refund = 0

# check for admin

# admin commands

cmds = ["/commands", "/cmds", "/update", "/remove", "/rem", "/logout", "/items"]

cmd_func = {
    "/commands or /cmds": "Displays the commands",
    "/update": "Adds items to the existing stock. (Also updates items in the existing stock",
    "/remove or /rem": "Removes items from the existing stock",
    "/items": "Displays the list of items in the existing stock including price and stock.",
    "/logout": "Log out from admin control."
}

name = str(input("Please input your name (input -1 to exit): "))
name = name.lower()

while len(str(name)) == 0:
    name = str(input("Empty input. Please input your name (input -1 to exit): "))

while name == admin:
    pass_input = str(input("Please input your password. Type /cancel to cancel admin login: "))

    while not (pass_input == password or pass_input == "/cancel"):
        pass_input = str(input("Incorrect password. Please input your password or input /cancel to cancel admin login: "))

    if pass_input == password:
        new_name = admin[0].upper() + admin[1:int(len(admin) + 1)]
        cmd = str(input("Welcome Admin " + new_name + ", type /commands or /cmds to view commands: "))

        while "/" not in cmd:
            print(cmd)
            cmd = str(input("Please input a command. Type /commands or /cmds to view commands: "))

        while cmd != "/logout":
            while cmd not in cmds:
                cmd = str(input("That is not a command. Please input correct command: "))

            if cmd == "/commands" or cmd == "/cmds":
                for each in cmd_func:
                    print("%s: %s" % (each, cmd_func[each]))

                cmd = str(input("Please input a command. Type /commands or /cmds to view commands: "))

            if cmd == "/items":
                print("")
                print("Items: ")
                print("")

                for each in price:
                    print("%s: %s tk" % (each, price[each]))

                print("")
                print("Stock:")

                for each in stock:
                    print("%s: %s" % (each, stock[each]))
                cmd = str(input("Please input a command. Type /commands or /cmds to view commands: "))

            if cmd == "/remove" or cmd == "/rem":
                rem_item = input("Please enter the name of the item that you wish to remove from the stock: ")

                while len(str(rem_item)) == 0:
                    rem_item = input("Empty input. Please enter the name of the item that you wish to remove from the stock: ")
                    rem_item = rem_item.lower()

                while rem_item not in stock:
                    rem_item = input("That item is not in the stock. Please enter the name of the item that you wish to remove from the stock: ")
                    rem_item = rem_item.lower()

                    while len(str(rem_item)) == 0:
                        rem_item = input("Empty input. Please enter the name of the item that you wish to remove from the stock: ")
                        rem_item = rem_item.lower()

                del price[rem_item]
                del stock[rem_item]

                cmd = str(input("Please input a command. Type /commands or /cmds to view commands: "))

            if cmd == "/update":
                new_item = input("Please enter the name of the new item: ")
                while len(str(new_item)) == 0:
                    new_item = input("Empty input. Please enter the name of the new item: ")

                new_number = input("Please enter the number of " + new_item + "s you wish to add to the stock: ")

                while len(str(new_number)) == 0:
                    new_number = input("Empty input. Please enter the number of " + new_item + "s you wish to add to the stock: ")

                while not new_number.isdigit():
                    new_number = input("Incorrect input. Please enter the number of " + new_item + "s you wish to add to the stock: ")

                    while len(str(new_number)) == 0:
                        new_number = input("Empty input. Please enter the number of " + new_item + "s you wish to add to the stock: ")

                new_number = int(new_number)

                while new_number < 0:
                    new_number = input("Incorrect input. Please enter the number of " + new_item + "s you wish to add to the stock: ")

                    while len(str(new_number)) == 0:
                        new_number = input("Empty input. Please enter the number of " + new_item + "s you wish to add to the stock: ")

                    while not new_number.isdigit():
                        new_number = input("Incorrect input. Please enter the number of " + new_item + "s you wish to add to the stock: ")

                        while len(str(new_number)) == 0:
                            new_number = input("Empty input. Please enter the number of " + new_item + "s you wish to add to the stock: ")

                    new_number = int(new_number)

                new_price = input("Please enter the price of the item: ")

                while len(str(new_price)) == 0:
                    new_price = input("Empty input. Please enter the price of the item: ")

                while not new_price.isdigit():
                    new_number = input("Incorrect input. Please enter the price of the item: ")

                    while len(str(new_number)) == 0:
                        new_number = input("Empty input. Please enter the price of the item: ")

                new_price = float(new_price)

                while new_price < 0:
                    new_price = input("Incorrect input. Please enter the price of the item: ")

                    while len(str(new_price)) == 0:
                        new_price = input("Empty input. Please enter the price of the item: ")

                    while not new_price.isdigit():
                        new_price = input("Incorrect input. Please enter the price of the item: ")

                        while len(str(new_price)) == 0:
                            new_price = input("Empty input. Please enter the price of the item: ")

                    new_price = float(new_price)

                if new_item in price:
                    price[new_item] = new_price
                else:
                    price.update({str(new_item): new_price})

                if new_item in stock:
                    stock[new_item] += new_number
                else:
                    stock.update({str(new_item): new_number})

                cmd = str(input("Please input a command. Type /commands or /cmds to view commands: "))

    name = str(input("Please input your name: "))


# showing the items, prices and stock
if name != "-1":
    print("")
    print("Welcome to Python supermarket, " + name + ". What would you like to buy?")
    print("")
    print("Items:")

    for each in price:
        print("%s: %s tk" % (each, price[each]))

    print("")
    print("Stock:")

    for each in stock:
        print("%s: %s" % (each, stock[each]))

    # taking inputs for purchase

    while purchase != "finish":
        purchase = str(input("Please input the item which you wish to buy (input 'finish' to proceed): "))
        purchase = purchase.lower()

        # validation check for empty input

        while len(purchase) == 0:
            purchase = str(input("Empty input. Please input the item which you wish to buy (input 'finish' to proceed): "))
            purchase = purchase.lower()

        # validation check to see whether item is in stock or not

        if purchase != "finish" and (purchase not in stock):

            while (purchase not in stock) and purchase != 'finish':

                if purchase != "finish":
                    purchase = str(input("We do not have that item. Please input the item which you wish to buy (input 'finish' to proceed): "))

        # check to see whether input item is in stock or not

        if purchase != "finish":
            if stock[purchase] == 0:
                while stock[purchase] == 0:
                    purchase = str(input("We do not have that item in our stock. Please input the item which you wish to buy (input 'finish to proceed): "))

        # adding items into the shopping bag

        if purchase not in items_bought and purchase != "finish":
            items_bought.update({purchase: 0})

        # taking inputs of number of items

        if purchase != "finish":
            number = input("Please input the number of items that you wish to buy: ")

            # validation check for empty input

            while len(str(number)) == 0:
                number = input("Empty input. Please input the number of items that you wish to buy: ")

            # validation check for integer

            while not number.isdigit():
                number = input("Incorrect input. Please input the number of items that you wish to buy: ")

                # validation check for empty input

                while len(str(number)) == 0:
                    number = input("Empty input. Please input the number of items that you wish to buy: ")

            number = int(number)

            # validation check to see whether input is a positive integer or not

            while number < 0:
                number = input("Incorrect input. Please input the number of items that you wish to buy: ")

                # validation check for empty input

                while len(str(number)) == 0:
                    number = input("Empty input. Please input the number of items that you wish to buy: ")

                # validation check for integer

                while not number.isdigit():
                    number = input("Incorrect input. Please input the number of items that you wish to buy: ")

                    # validation check for empty input
                    while len(str(number)) == 0:
                        number = input("Empty input. Please input the number of items that you wish to buy: ")

            # validation check to see whether input value exceeds stock value

            while number > stock[purchase]:
                number = input("Input value exceeds stock value. Please input the number of items that you wish to buy: ")

                # validation check for empty input

                while len(str(number)) == 0:
                    number = input("Empty input. Please input the number of items that you wish to buy: ")

                # validation check for integer

                while not number.isdigit():
                    number = input("Incorrect input. Please input the number of items that you wish to buy: ")

                    # validation check for empty input

                    while len(str(number)) == 0:
                        number = input("Empty input. Please input the number of items that you wish to buy: ")

                number = int(number)

                # validation check to see whether input is a positive integer or not

                while number < 0:
                    number = input("Incorrect input. Please input the number of items that you wish to buy: ")

                    # validation check for empty input

                    while len(str(number)) == 0:

                        number = input("Empty input. Please input the number of items that you wish to buy: ")

                    # validation check for integer

                    while not number.isdigit():
                        number = input("Incorrect input. Please input the number of items that you wish to buy: ")

                        # validation check for empty input
                        while len(str(number)) == 0:
                            number = input("Empty input. Please input the number of items that you wish to buy: ")
                    number = int(number)

            items_bought[purchase] += number
            stock[purchase] -= number

    # taking inputs for refund

    while refund_i != "finish":
        refund_i = str(input("Please input the name of the faulty items that you wish to return(input 'finish' to proceed): "))
        refund_i = refund_i.lower()

        # validation check for empty input

        while len(refund_i) == 0:
            refund_i = str(input("Empty input. Please input the name of the faulty items that you wish to return(input 'finish' to proceed): "))
            refund_i = refund_i.lower()

        # presence check to see whether item is in shopping bag or not

        if refund_i != "finish":
            if refund_i not in items_bought:
                while (refund_i not in items_bought) and refund_i != 'finish':
                    while len(refund_i) == 0:
                        refunt_i = str(input("Empty input. Please input the name of the item which you wish to return(input 'finish' to proceed): "))

                    refund_i = str(input("You have not bought this item. Please input the name of the faulty items that you wish to return(input 'finish' to proceed): "))
                    refund_i = refund_i.lower()

        # adding items to the refund list

        if refund_i != "finish":
            if refund_i not in refund_items:
                refund_items.update({refund_i: 0})

            # taking inputs for number of items to return

            refund_n = input("Please input the number of items you wish to return: ")

            # validation check for empty input

            while len(str(refund_n)) == 0:
                refund_n = input("Empty input. Please input the number of items you wish to return: ")

            # validation check for integer

            while not refund_n.isdigit():
                refund_n = input("Incorrect input. Please input the number of items you wish to return: ")

                # validation check for empty input

                while len(str(refund_n)) == 0:
                    refund_n = input("Empty input. Please input the number of items you wish to return: ")
            refund_n = int(refund_n)

            # validation check to see whether input is positive integer or not

            while refund_n < 0:
                refund_n = input("Incorrect input. Please input the number of items you wish to return: ")

                # validation check for empty input

                while len(str(refund_n)) == 0:
                    refund_n = input("Empty input. Please input the number of items you wish to return: ")

                # validation check for integer

                while not refund_n.isdigit():
                    refund_n = input("Incorrect input. Please input the number of items you wish to return: ")

                    # validation check for empty input

                    while len(str(refund_n)) == 0:
                        refund_n = input("Empty input. Please input the number of items you wish to return: ")

            refund_items[refund_i] += refund_n


    # final calculations

    # total bill

    for each in items_bought:
        total += price[each] * items_bought[each]

    # total refund

    for each in refund_items:
        refund += price[each] * refund_items[each]

    till = total - refund

    # final output

    print("")
    print("")
    print("Items bought: ")
    print("")

    for each in items_bought:
        print("%s: %s" % (each, items_bought[each]))

    print("")
    print("Total bill: " + str(total) + " tk")
    print("")
    print("Refund: ")
    print("")

    for each in refund_items:
        print("%s: %s" % (each, refund_items[each]))

    print("")
    print("Total amount refunded: " + str(refund) + " tk")
    print("")
    print("Money remaining in the till: " + str(till) + " tk")
    print("")
else:
    print("Program ended. Thank you for using my software!")
print("Press enter to continue...")
input()
