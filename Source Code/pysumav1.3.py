import tkinter as tk
import tkinter.messagebox as msg
import tkinter.font as fonts
import os
import datetime as dt
import sqlite3 as sql
import json
from hashlib import sha1
import random


ROOT_TITLE = "Sajeed's Python Super Market v1.3"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
root = tk.Tk()
root.title(ROOT_TITLE)
root.geometry("640x480")
root.resizable(0, 0)
root.config(background='white')
cart_items = {}
cart_prices = {}
shopping_cart = ""

user = {"name": "", "is_admin": 0, "is_masteradmin": 0}
customer_id = None

if "settings.json" in os.listdir("."):
    with open("settings.json") as json_file:
        data = json.load(json_file)
        hasher = data["hasher"]
        database = data["database"]
        masteradmin = data["masteradmin"]
        masteradminpassword = data["masteradminpassword"]
else:
    msg.showerror(ROOT_TITLE, "settings.json is missing")
    raise SystemExit

if "log.txt" not in os.listdir('.'):
    with open("log.txt", "w") as log:
        log.write("")


def create_db():

    if database not in os.listdir('.'):

        try:
            db = sql.connect(database)
        except sql.Error as e:
            print(e)
        finally:
            cursor = db.cursor()
            cursor.execute("CREATE TABLE IF NOT EXISTS `accounts` ('id' integer primary key autoincrement, 'name' text not null, 'password' text not null, 'is_admin' integer default 0, 'is_masteradmin' integer default 0);")
            cursor.execute("CREATE TABLE IF NOT EXISTS `items` ('name' text not null, 'price' real not null, 'stock' integer not null);")
            cursor.execute("CREATE TABLE IF NOT EXISTS `orders` ('customer_id' integer, 'items' text not null, 'number_ordered' text not null);")
            cursor.close()
            db.close()


if "Flux" not in fonts.families():
    msg.showerror(ROOT_TITLE, "Please install 'Flux Regular.otf' (provided in the compressed file)")
    raise SystemExit

if "icon.ico" in os.listdir(".") or "icon.xbm" in os.listdir("."):
    try:
        root.iconbitmap("icon.ico")
    except Exception:
        root.iconbitmap("@" + BASE_DIR + "/icon.xbm")
else:
    msg.showerror(ROOT_TITLE, "Icon file is missing")
    raise SystemExit

if "logo.png" not in os.listdir("."):
    msg.showerror(ROOT_TITLE, "logo.png file is missing")
    raise SystemExit


def WriteInLog(text):
    with open("log.txt", "a") as log:
        now = dt.datetime.now()
        log.write("[{}/{}/{}][{}:{}] {}\n".format(now.day, now.month, now.year, now.hour, now.minute, text))


def db_query(query, query_type):
    global database
    try:
        db = sql.connect(database)
    except sql.Error:
        create_db()
    finally:
        cursor = db.cursor()
        if query_type == "select" or query_type == "s":
            cursor.execute(query)
            results = cursor.fetchall()
            cursor.close()
            db.close()
            return results
        if query_type == "insert" or query_type == "i" or query_type == "delete" or query_type == "d" or query_type == "update" or query_type == "u":
            try:
                cursor.execute(query)
                db.commit()
                cursor.close()
                db.close()
            except sql.Error as e:
                db.rollback()
                print(e)
                return False


def check_pass(pass_in, enc_pass):
    pass_details = enc_pass.split("$")

    # algorithm$iteration$salt$password
    algorithm = pass_details[0]
    if len(pass_details) == 3:
        salt = pass_details[1]
        password = pass_details[2]

    else:
        iteration = int(pass_details[1])
        salt = pass_details[2]
        password = pass_details[3]

    encrypted_password = salt + pass_in
    if algorithm == "sha1":

        for _ in range(iteration):
            encrypted_password = sha1(encrypted_password.encode()).hexdigest()
    if encrypted_password == password:
        return True
    else:
        return False


def fetch_account(username):
    account_details = db_query("SELECT * FROM `accounts` WHERE `name` = '%s'" % (username), "s")
    if account_details:
        account_details = account_details[0]
    else:
        return None

    if len(account_details) == 0:
        return None
    else:
        return {"id": account_details[0], "name": account_details[1], "password": account_details[2], "is_admin": int(account_details[3]), "is_masteradmin": int(account_details[4])}


def create_password(pass_in):
    letters = ['abcedfghijklmnopqrstuvwxyz', 'ABCDEFGHIJKLMNOPQRSTUVWXYZ']

    salt = ''

    for _ in range(4):
        a = random.randint(0, 1)
        b = random.randint(0, len(letters[a]) - 1)
        salt += letters[a][b]

    encrypted_password = salt + pass_in
    iteration = random.randint(100, 200)

    for _ in range(iteration):
        if hasher == "sha1":
            encrypted_password = sha1(encrypted_password.encode()).hexdigest()

    return "{}${}${}${}".format(hasher, iteration, salt, encrypted_password)


if database not in os.listdir("."):
    create_db()

result = db_query("SELECT * FROM `accounts` WHERE `name` = '%s'" % (masteradmin), "s")

if not result:
    db_query("INSERT INTO `accounts` (`id`, `name`, `password`, `is_admin`, `is_masteradmin`) VALUES (NULL, '%s', '%s', 0, 1)" % (masteradmin, create_password(masteradminpassword)), "i")


class MainMenu:
    Name = tk.StringVar()
    Pwd = tk.StringVar()

    def __init__(self):

        # tk.Frame
        self.mainFrame = tk.Frame(root, width=640, height=480)
        self.mainFrame.pack()

        # Background image
        self.mainbgImg = tk.PhotoImage(file="logo.png")
        self.mainBg = tk.Label(self.mainFrame, image=self.mainbgImg)
        self.mainBg.place(x=0, y=0)

        # Name
        self.NameLabel = tk.Label(self.mainFrame, font=("Flux", 16, "bold"), text="Name:", bg="white")
        self.NameLabel.place(x=410, y=110)
        self.NameInput = tk.Entry(self.mainFrame, font=("Flux", 16, "bold"), bg="lightgrey", bd=2, relief=tk.SUNKEN, textvariable=self.Name)
        self.NameInput.bind("<Button-1>", lambda event: self.inputFocus(event, item=self.NameInput))
        self.NameInput.bind("<KeyPress>", lambda event: self.inputFocus(event, item=self.NameInput))
        self.NameInput.bind("<Return>", self.logIn)
        self.NameInput.place(x=410, y=140)

        # Password
        self.PwdLabel = tk.Label(self.mainFrame, font=("Flux", 16, "bold"), text="Password:", bg="white")
        self.PwdLabel.place(x=410, y=170)
        self.PwdInput = tk.Entry(self.mainFrame, show="*", font=("Flux", 16, "bold"), bg="lightgrey", bd=2, relief=tk.SUNKEN, textvariable=self.Pwd)
        self.PwdInput.bind("<Button-1>", lambda event: self.inputFocus(event, item=self.PwdInput))
        self.PwdInput.bind("<KeyPress>", lambda event: self.inputFocus(event, item=self.PwdInput))
        self.PwdInput.bind("<Return>", self.logIn)
        self.PwdInput.place(x=410, y=200)

        # Login button
        self.logBtn = tk.Button(self.mainFrame, font=("Flux", 16, "bold"), text="Log In")
        self.logBtn.bind("<Button-1>", self.logIn)
        self.logBtn.place(x=410, y=240)

        # Register link
        self.regLink = tk.Label(self.mainFrame, font=("Flux", 16, "underline"), text="Don't have an account? Make one!", cursor="hand2", bg="white", anchor=tk.W)
        self.regLink.bind("<Button-1>", self.reg)
        self.regLink.place(x=355, y=280)
        root.protocol("WM_DELETE_WINDOW", root.destroy)

    def logIn(self, event):
        global user, room
        if len(str(self.Name.get())) == 0:
            self.NameInput.config(bg="red")
            msg.showerror(ROOT_TITLE, "Name cannot be empty!")
        if len(str(self.Pwd.get())) == 0:
            self.PwdInput.config(bg="red")
            msg.showerror(ROOT_TITLE, "Please enter your password!")

        if len(str(self.Name.get())) != 0 and len(str(self.Pwd.get())) != 0:
            account = fetch_account(self.Name.get())

            if account is None:
                msg.showerror(ROOT_TITLE, "Account does not exist in database.")
            else:
                if check_pass(str(self.Pwd.get()), account["password"]):
                    user["name"] = self.Name.get()
                    user["is_admin"], user["is_masteradmin"] = account["is_admin"], account["is_masteradmin"]
                    msg.showinfo(ROOT_TITLE, "Welcome %s!" % (user["name"]))
                    self.Name.set("")
                    self.Pwd.set("")

                    for child in root.winfo_children():
                        child.destroy()

                    if account["is_admin"]:
                        room = AdminPanel()
                        WriteInLog("Admin %s has logged in." % (user["name"]))
                    elif account["is_masteradmin"]:
                        room = AdminPanel()
                        WriteInLog("Master admin %s has logged in." % (user["name"]))
                    else:
                        room = CustomerPanel()
                        WriteInLog("Customer %s has logged in." % (user["name"]))
                else:
                    self.PwdInput.config(bg="red")
                    msg.showerror(ROOT_TITLE, "Incorrect Password!")

    def reg(self, event):
        global room
        self.mainFrame.destroy()
        for child in root.winfo_children():
            child.destroy()
        room = Register()

    def inputFocus(self, event, item):
        item.config(bg="lightblue")
        if item != self.NameInput and self.NameInput['bg'] != 'red':
            self.NameInput.config(bg="lightgrey")

        if item != self.PwdInput and self.PwdInput['bg'] != 'red':
            self.PwdInput.config(bg="lightgrey")


class Register:
    reg_Name = tk.StringVar()
    new_Pwd = tk.StringVar()
    conf_Pwd = tk.StringVar()

    def __init__(self):

        # tk.Frame
        self.regFrame = tk.Frame(root, width=640, height=480, bg="white")
        self.regFrame.place(x=0, y=0)

        # Register name
        self.regName = tk.Label(self.regFrame, font=("Flux", 16, "bold"), bg="white", text="Name:")
        self.regName.place(x=200, y=100)
        self.NameEntry = tk.Entry(self.regFrame, font=("Flux", 16, "bold"), bg="lightgrey", bd=2, relief=tk.SUNKEN, textvariable=self.reg_Name)
        self.NameEntry.bind("<Button-1>", lambda event: self.inputFocus(event, self.NameEntry))
        self.NameEntry.bind("<KeyPress>", lambda event: self.inputFocus(event, self.NameEntry))
        self.NameEntry.bind("<Return>", self.regAccount)
        self.NameEntry.place(x=200, y=130)

        # Register password
        self.newPwd = tk.Label(self.regFrame, font=("Flux", 16, "bold"), bg="white", text="New password:")
        self.newPwd.place(x=200, y=160)
        self.NewPwd_Entry = tk.Entry(self.regFrame, font=("Flux", 16, "bold"), bg="lightgrey", bd=2, relief=tk.SUNKEN, textvariable=self.new_Pwd)
        self.NewPwd_Entry.bind("<Button-1>", lambda event: self.inputFocus(event, self.NewPwd_Entry))
        self.NewPwd_Entry.bind("<KeyPress>", lambda event: self.inputFocus(event, self.NewPwd_Entry))
        self.NewPwd_Entry.bind("<Return>", self.regAccount)
        self.NewPwd_Entry.place(x=200, y=190)

        # Confirm Password
        self.confpwd = tk.Label(self.regFrame, font=("Flux", 16, "bold"), bg="white", text="Confirm password:")
        self.confpwd.place(x=200, y=220)
        self.confpwd_entry = tk.Entry(self.regFrame, font=("Flux", 16, "bold"), bg="lightgrey", bd=2, relief=tk.SUNKEN, textvariable=self.conf_Pwd)
        self.confpwd_entry.bind("<Button-1>", lambda event: self.inputFocus(event, self.confpwd_entry))
        self.confpwd_entry.bind("<KeyPress>", lambda event: self.inputFocus(event, self.confpwd_entry))
        self.confpwd_entry.bind("<Return>", self.regAccount)
        self.confpwd_entry.place(x=200, y=250)

        # Register button
        self.regBtn = tk.Button(self.regFrame, font=("Flux", 16, "bold"), text="Register")
        self.regBtn.bind("<Button-1>", self.regAccount)
        self.regBtn.place(x=200, y=280)

        # Back button
        self.backBtn = tk.Button(self.regFrame, font=("Flux", 16, "bold"), text="Back", command=self.back)
        self.backBtn.place(x=350, y=280)

        root.protocol("WM_DELETE_WINDOW", self.back)

    def regAccount(self, event):
        global masterAdmin, room
        if len(str(self.reg_Name.get())) == 0:
            self.NameEntry.config(bg="red")
            msg.showinfo(ROOT_TITLE, "Name cannot be empty")

        if len(str(self.new_Pwd.get())) == 0:
            self.NewPwd_Entry.config(bg="red")
            msg.showinfo(ROOT_TITLE, "You must choose a password!")

        if len(str(self.conf_Pwd.get())) == 0:
            self.confpwd_entry.config(bg="red")
            msg.showinfo(ROOT_TITLE, "Please retype your password!")

        if (len(str(self.reg_Name.get())) != 0 and len(str(self.new_Pwd.get())) != 0 and len(str(self.conf_Pwd.get())) != 0):
            if (self.conf_Pwd.get() == self.new_Pwd.get()):
                if fetch_account(str(self.reg_Name.get())) is None:
                    db_query("INSERT INTO `accounts` ('id', 'name', 'password', 'is_admin', 'is_masteradmin') VALUES (NULL, '%s', '%s', 0, 0);" % (self.reg_Name.get(), create_password(self.new_Pwd.get())), "i")
                    msg.showinfo(ROOT_TITLE, "Registered account with:\nName: {}\nPassword: {}".format(self.reg_Name.get(), self.new_Pwd.get()))

                    WriteInLog("Account {} has been registered and added to database.")

                    self.reg_Name.set("")
                    self.new_Pwd.set("")
                    self.conf_Pwd.set("")
                    self.regFrame.destroy()
                    for child in root.winfo_children():
                        child.destroy()
                    room = MainMenu()
                else:
                    msg.showerror(ROOT_TITLE, "Account already exists.")
            else:
                msg.showinfo(ROOT_TITLE, "Passwords do not match!")
                self.confpwd_entry.config(bg="red")

    def back(self):
        global room
        self.regFrame.destroy()
        for child in root.winfo_children():
            child.destroy()
        room = MainMenu()

    def inputFocus(self, event, item):
        item.config(bg='lightblue')

        if item != self.NameEntry and self.NameEntry['bg'] != ' red':
            self.NameEntry.config(bg='lightgrey')

        if item != self.NewPwd_Entry and self.NewPwd_Entry['bg'] != ' red':
            self.NewPwd_Entry.config(bg='lightgrey')

        if item != self.confpwd_entry and self.confpwd_entry['bg'] != ' red':
            self.confpwd_entry.config(bg='lightgrey')


class AdminPanel:
    def __init__(self):
        global user

        orders = db_query("SELECT * FROM `orders`", "s")

        if orders:
            msg.showinfo(ROOT_TITLE, "There are new orders pending!")

        # Admin tk.Frame and header
        self.adminFrame = tk.Frame(root, width=640, height=480, bg="white")
        self.adminFrame.place(x=0, y=0)
        self.header = tk.Label(root, font=("Flux", 32, "bold"), text="Admin Panel", bg="white")
        self.header.place(x=320, y=36, anchor=tk.CENTER)

        # Account info
        self.nameInfo = tk.Label(root, font=(12), text="Name: " + user["name"], bg="white")
        self.nameInfo.place(y=100)

        # Options
        # View admin database
        if user["is_masteradmin"]:
            self.viewadminDB = tk.Label(self.adminFrame, font=("Flux", 20, "bold"), text="View admin database", bg="white", cursor="hand2")
            self.viewadminDB.bind("<Motion>", lambda event: self.mouse_enter(event, self.viewadminDB))
            self.viewadminDB.bind("<Leave>", lambda event: self.mouse_exit(event, self.viewadminDB))
            self.viewadminDB.bind("<Button-1>", lambda event: self.agoto(event, AdminDatabase))
            self.viewadminDB.place(x=320, y=150, anchor=tk.CENTER, width=640)

        # View accounts database
        self.viewADB = tk.Label(self.adminFrame, font=("Flux", 20, "bold"), text="View account database", bg="white", cursor="hand2")
        self.viewADB.bind("<Motion>", lambda event: self.mouse_enter(event, self.viewADB))
        self.viewADB.bind("<Leave>", lambda event: self.mouse_exit(event, self.viewADB))
        self.viewADB.bind("<Button-1>", lambda event: self.agoto(event, AccountDatabase))
        self.viewADB.place(x=320, y=200, anchor=tk.CENTER, width=640)

        # View stock
        self.viewStock = tk.Label(self.adminFrame, font=("Flux", 20, "bold"), text="View items stock", bg="white", cursor="hand2")
        self.viewStock.bind("<Motion>", lambda event: self.mouse_enter(event, self.viewStock))
        self.viewStock.bind("<Leave>", lambda event: self.mouse_exit(event, self.viewStock))
        self.viewStock.bind("<Button-1>", lambda event: self.agoto(event, AdminStock))
        self.viewStock.place(x=320, y=250, anchor=tk.CENTER, width=640)

        # Transaction screen
        self.transactionScreen = tk.Label(self.adminFrame, font=("Flux", 20, "bold"), text="View Orders", bg="white", cursor="hand2")
        self.transactionScreen.bind("<Motion>", lambda event: self.mouse_enter(event, self.transactionScreen))
        self.transactionScreen.bind("<Leave>", lambda event: self.mouse_exit(event, self.transactionScreen))
        self.transactionScreen.bind("<Button-1>", lambda event: self.agoto(event, TransactionScreen))
        self.transactionScreen.place(x=320, y=300, anchor=tk.CENTER, width=640)
        self.Logout = tk.Label(self.adminFrame, font=("Flux", 20, "bold"), text="Logout", bg="white", cursor="hand2")
        self.Logout.bind("<Motion>", lambda event: self.mouse_enter(event, self.Logout))
        self.Logout.bind("<Leave>", lambda event: self.mouse_exit(event, self.Logout))
        self.Logout.bind("<Button-1>", self.logoutBtn)
        self.Logout.place(x=320, y=350, anchor=tk.CENTER, width=640)

        root.protocol("WM_DELETE_WINDOW", self.logoutWin)

    def mouse_enter(self, event, item):
        item.config(bg="lightblue")

    def mouse_exit(self, event, item):
        item.config(bg="white")

    def logoutBtn(self, event):
        global user, room
        self.adminFrame.destroy()
        for child in root.winfo_children():
            child.destroy()
        if user["is_masteradmin"]:
            WriteInLog("Master admin {} logged out.".format(user["name"]))
        else:
            WriteInLog("Admin {} logged out.".format(user["name"]))
        user["name"], user["is_admin"], user["is_masteradmin"] = "", 0, 0

        room = MainMenu()

    def logoutWin(self):
        global user, room
        self.adminFrame.destroy()
        for child in root.winfo_children():
            child.destroy()
        if user["is_masteradmin"]:
            WriteInLog("Master admin {} logged out.".format(user["name"]))
        else:
            WriteInLog("Admin {} logged out.".format(user["name"]))
        user["name"], user["is_admin"], user["is_masteradmin"] = "", 0, 0
        room = MainMenu()

    def agoto(self, event, newroom):
        global room
        for child in root.winfo_children():
            child.destroy()
        room = newroom()


class AdminDatabase:
    def __init__(self):
        global user

        root.protocol('WM_DELETE_WINDOW', self.back_Btn)
        self.admins = []
        db_admins = db_query("SELECT `name` FROM `accounts` WHERE `is_admin` = 1", "s")

        if not db_admins:
            root.update()
            tk.Label(root, font=("Flux", 16, "bold"), bg="white", text="There are no admins in the database.").place(x=root.winfo_width() / 2, y=root.winfo_height() / 2, anchor=tk.CENTER)
            tk.Button(root, font=("Flux", 14, "bold"), text="Back", command=self.back_Btn).place(x=root.winfo_width() / 2, y=root.winfo_height() / 2 + 30, anchor=tk.CENTER)
        else:
            for admin in db_admins:
                self.admins.append(admin[0])
            self.adminDBcanvas = tk.Canvas(root, bg="white", bd=0)
            self.adminDBcanvas.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
            self.adminList = tk.Frame(self.adminDBcanvas, width=640, bg="white")
            self.adminDBcanvas.create_window((0, 0), window=self.adminList, anchor=tk.NW)
            self.adminScrollbar = tk.Scrollbar(self.adminDBcanvas, orient=tk.VERTICAL, command=self.adminDBcanvas.yview)
            self.adminScrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            self.adminDBcanvas.config(yscrollcommand=self.adminScrollbar.set)
            self.adminDBcanvas.bind("<Configure>", self.adminScroll)

            self.adminDBheader = tk.Label(root, font=("Flux", 32, "bold"), text=("Admin Database"), bg="white")
            self.adminDBheader.pack(side=tk.TOP, anchor=tk.CENTER)

            self.backBtn = tk.Button(root, font=("Flux", 14, "bold"), text="Back", command=self.back_Btn)
            self.backBtn.pack(side=tk.BOTTOM, anchor=tk.SE)

            self.nameInfo = tk.Label(root, font=(12), text="Name: " + user["name"], bg="white")
            self.nameInfo.pack(side=tk.BOTTOM, anchor=tk.W, pady=(64, 0))

            tk.Label(self.adminList, font=("Flux", 18, "bold"), text="Names", bg="white").grid(column=0, row=0)
            tk.Label(self.adminList, font=("Flux", 18, "bold"), text="Remove", bg="white").grid(column=1, row=0, padx=(435, 0))
            self.adminNames = []
            self.adminButtons = []
            for e in range(len(self.admins)):
                self.adminButtons.append(tk.Button(self.adminList, font=("Flux", 14, "bold"), text="Remove Admin", command=lambda e=e: self.RemoveAdmin(e)))

            for each in self.admins:
                self.adminNames.append(tk.Label(self.adminList, font=("Flux", 16, "bold"), text=each, bg="white"))

            for x in range(0, len(self.adminNames)):
                self.adminNames[x].grid(column=0, row=1 + x)
                self.adminButtons[x].grid(column=1, row=1 + x, padx=(415, 0))

    def adminScroll(self, event):
        self.adminDBcanvas.config(scrollregion=self.adminDBcanvas.bbox('all'))

    def back_Btn(self):
        global room
        for child in root.winfo_children():
            child.destroy()
        room = AdminPanel()

    def RemoveAdmin(self, number):
        global room, user
        if msg.askyesno(ROOT_TITLE, "Are you sure you wish to remove adminship from %s?" % (self.adminNames[number]['text'])):
            WriteInLog("Master admin {} has removed adminship from {}.".format(user["name"], self.adminNames[number]['text']))

            db_query("UPDATE `accounts` SET `is_admin` = 0 WHERE `name` = '%s'" % (self.adminNames[number]['text']), "u")

            for child in root.winfo_children():
                child.destroy()
            room = AdminDatabase()


class AccountDatabase:
    def __init__(self):
        global user
        self.accounts = []

        db_accounts = db_query("SELECT `name`, `is_admin`, `is_masteradmin` FROM `accounts`", "s")

        for account in db_accounts:
            if not int(account[1]) and not int(account[2]):
                self.accounts.append(account[0])

        if not self.accounts:
            root.update()
            tk.Label(root, font=("Flux", 16, "bold"), bg="white", text="There are no accounts in the database.").place(x=root.winfo_width() / 2, y=root.winfo_height() / 2, anchor=tk.CENTER)
            tk.Button(root, font=("Flux", 14, "bold"), text="Back", command=self.go_back).place(x=root.winfo_width() / 2, y=root.winfo_height() / 2 + 30, anchor=tk.CENTER)

        else:
            self.accountDBFrame = tk.Canvas(root, bg="white", bd=0)
            self.accountDBFrame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
            self.accountlst = tk.Frame(self.accountDBFrame, width=640, bg="white")
            self.accountDBFrame.create_window((0, 0), window=self.accountlst, anchor=tk.NW)
            self.adbscrollbar = tk.Scrollbar(self.accountDBFrame, orient=tk.VERTICAL, command=self.accountDBFrame.yview)
            self.adbscrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            self.accountDBFrame.config(yscrollcommand=self.adbscrollbar.set)
            self.accountDBFrame.bind("<Configure>", self.adbScroll)

            self.adbHeader = tk.Label(root, font=("Flux", 32, "bold"), text=("Account Database"), bg="white")
            self.adbHeader.pack(side=tk.TOP, anchor=tk.CENTER)

            self.backBtn = tk.Button(root, font=("Flux", 14, "bold"), text="Back", command=self.go_back)
            self.backBtn.pack(side=tk.BOTTOM, anchor=tk.SE)

            self.nameInfo = tk.Label(root, font=(12), text="Name: " + user["name"], bg="white")
            self.nameInfo.pack(side=tk.BOTTOM, anchor=tk.W, pady=(64, 0))

            tk.Label(self.accountlst, font=("Flux", 18, "bold"), text="Names", bg="white").grid(column=0, row=0)
            tk.Label(self.accountlst, font=("Flux", 18, "bold"), text="Set Admin", bg="white").grid(column=1, row=0, padx=(260, 2))
            tk.Label(self.accountlst, font=("Flux", 18, "bold"), text="Remove Account", bg="white").grid(column=2, row=0)

            self.accountNames = []
            self.accountButtons = []

            for each in self.accounts:
                self.accountButtons.append(tk.Button(self.accountlst, font=("Flux", 14, "bold"), text="Remove Account"))

            for each in self.accounts:
                self.accountNames.append(tk.Label(self.accountlst, font=("Flux", 16, "bold"), text=each, bg="white"))

            if user["is_masteradmin"]:
                self.adminButtons = []
                for each in self.accounts:
                    self.adminButtons.append(tk.Button(self.accountlst, font=("Flux", 14, "bold"), text="Set Admin"))
                for loop in range(0, len(self.accountNames)):
                    self.adminButtons[loop].bind("<Button-1>", lambda event, loop=loop: self.SetAdmin(event, int(loop)))
                    self.adminButtons[loop].grid(column=1, row=1 + loop, padx=(260, 2))

            for loop in range(0, len(self.accountNames)):
                self.accountNames[loop].grid(column=0, row=1 + loop)
                self.accountButtons[loop].bind("<Button-1>", lambda event, loop=loop: self.RemoveAccount(event, int(loop)))
                self.accountButtons[loop].grid(column=2, row=1 + loop)

            root.protocol("WM_DELETE_WINDOW", self.go_back)

    def adbScroll(self, event):
        self.accountDBFrame.config(scrollregion=self.accountDBFrame.bbox('all'))

    def RemoveAccount(self, event, number):
        global user, room
        if msg.askyesno(ROOT_TITLE, "Are you sure you wish to remove %s's account?" % (self.accountNames[number]['text'])):
            if user["is_masteradmin"]:
                WriteInLog("Master admin {} has removed {}'s account from the database.".format(user["name"], self.accountNames[number]['text']))

            else:
                WriteInLog("Admin {} has removed {}'s account from the database.".format(user["name"], self.accountNames[number]['text']))

            db_query("DELETE FROM `accounts` WHERE `name` = '%s'" % (self.accountNames[number]['text']), "d")

            for child in root.winfo_children():
                child.destroy()
            room = AccountDatabase()

    def SetAdmin(self, event, number):
        global name, room
        if msg.askyesno(ROOT_TITLE, "Are you sure you wish to give administrative powers to %s?" % (self.accountNames[number]['text'])):
            if user["is_masteradmin"]:
                WriteInLog("Master admin {} has given adminship to {}.".format(user["name"], self.accountNames[number]['text']))
            else:
                WriteInLog("Admin {} has given adminship to {}.".format(user["name"], self.accountNames[number]['text']))

            db_query("UPDATE `accounts` SET `is_admin` = 1 WHERE `name` = '%s'" % (self.accountNames[number]['text']), "u")

            for child in root.winfo_children():
                child.destroy()

            room = AccountDatabase()

    def go_back(self):
        global room
        for child in root.winfo_children():
            child.destroy()

        room = AdminPanel()


class AdminStock:
    def __init__(self):
        global user

        self.editing = False
        self.adding = False

        self.astockCanvas = tk.Canvas(root, bg="white", bd=0)
        self.astockCanvas.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        self.stockList = tk.Frame(self.astockCanvas, width=640, bg="white")
        self.astockCanvas.create_window((0, 0), window=self.stockList, anchor=tk.NW)
        self.astockScrollbar = tk.Scrollbar(self.astockCanvas, orient=tk.VERTICAL, command=self.astockCanvas.yview)
        self.astockScrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.astockCanvas.config(yscrollcommand=self.astockScrollbar.set)
        self.astockCanvas.bind("<Configure>", self.astockScroll)
        self.actionbuttons = tk.Frame(root, bg="white")
        self.actionbuttons.pack(side=tk.BOTTOM, fill=tk.X)
        self.stockHeader = tk.Label(root, font=("Flux", 32, "bold"), text="Items stock", bg="white")
        self.stockHeader.pack(side=tk.TOP, anchor=tk.CENTER)

        self.backBtn = tk.Button(self.actionbuttons, font=("Flux", 14, "bold"), text="Back", command=lambda: self.goBack())
        self.backBtn.pack(side=tk.RIGHT)

        self.addItem = tk.Button(self.actionbuttons, font=("Flux", 14, "bold"), text="Add Item", command=lambda: self.add_item(int(len(self.itemNames))))
        self.addItem.pack(side=tk.RIGHT)

        self.nameInfo = tk.Label(root, font=(12), text="Name: " + user["name"], bg="white")
        self.nameInfo.pack(side=tk.BOTTOM, anchor=tk.W, pady=(64, 0))

        tk.Label(self.stockList, font=("Flux", 14, "bold"), text="Name", bg="white").grid(column=0, row=0, padx=(30, 0), sticky=tk.W)
        tk.Label(self.stockList, font=("Flux", 14, "bold"), text="Price", bg="white").grid(column=1, row=0, padx=(30, 0), sticky=tk.W)
        tk.Label(self.stockList, font=("Flux", 14, "bold"), text="Stock", bg="white").grid(column=2, row=0, padx=(30, 0), sticky=tk.W)
        tk.Label(self.stockList, font=("Flux", 14, "bold"), text="Update", bg="white").grid(column=3, row=0, padx=(30, 0), sticky=tk.W)
        tk.Label(self.stockList, font=("Flux", 14, "bold"), text="Remove", bg="white").grid(column=4, row=0, padx=(30, 0), sticky=tk.W)

        self.item_DB = db_query("SELECT * FROM `items`", "s")

        self.itemNames = []
        self.itemPrice = []
        self.itemStock = []

        self.updateButtons = []
        self.removeButtons = []
        self.doneButtons = []
        self.cancelButtons = []

        self.items = {}

        for item in self.item_DB:
            self.items.update({item[0]: [item[1], item[2]]})

        if not self.items:
            self.message = tk.Label(self.stockList, font=("Flux", 18, "bold"), text="There are no items in the database.", bg="white")
            self.message.grid(column=2, row=1, columnspan=5, pady=100)

        else:

            for x in range(len(self.items)):
                self.itemNames.append(tk.Entry(self.stockList, font=("Flux", 14, "bold"), disabledbackground="lightgrey", disabledforeground="black", bg="powderblue", relief=tk.SUNKEN, width=12, justify="center"))
                self.itemPrice.append(tk.Entry(self.stockList, font=("Flux", 14, "bold"), disabledbackground="lightgrey", disabledforeground="black", bg="powderblue", relief=tk.SUNKEN, width=12, justify="center"))
                self.itemStock.append(tk.Entry(self.stockList, font=("Flux", 14, "bold"), disabledbackground="lightgrey", disabledforeground="black", bg="powderblue", relief=tk.SUNKEN, width=12, justify="center"))
                self.updateButtons.append(tk.Button(self.stockList, font=("Flux", 11, "bold"), text="Update", command=lambda x=x: self.updateBtn(x)))
                self.removeButtons.append(tk.Button(self.stockList, font=("Flux", 11, "bold"), text="Remove", command=lambda x=x: self.removeItem(x)))
                self.doneButtons.append(tk.Button(self.stockList, font=("Flux", 11, "bold"), text="Done", command=lambda x=x: self.doneBtn(x)))
                self.cancelButtons.append(tk.Button(self.stockList, font=("Flux", 11, "bold"), text="Cancel", command=self.cancel))

            for a in range(len(self.items)):
                self.itemNames[a].grid(column=0, row=(1 + a), padx=(30, 0))
                self.itemNames[a].bind("<Button-1>", lambda event, a=a: self.inputFocus(event, number=a, item=self.itemNames))
                self.itemNames[a].bind("<KeyPress>", lambda event, a=a: self.inputFocus(event, number=a, item=self.itemNames))
                self.itemPrice[a].grid(column=1, row=(1 + a), padx=(30, 0))
                self.itemPrice[a].bind("<Button-1>", lambda event, a=a: self.inputFocus(event, number=a, item=self.itemPrice))
                self.itemPrice[a].bind("<KeyPress>", lambda event, a=a: self.inputFocus(event, number=a, item=self.itemPrice))
                self.itemStock[a].grid(column=2, row=(1 + a), padx=(30, 0))
                self.itemStock[a].bind("<Button-1>", lambda event, a=a: self.inputFocus(event, number=a, item=self.itemStock))
                self.itemStock[a].bind("<KeyPress>", lambda event, a=a: self.inputFocus(event, number=a, item=self.itemStock))
                self.updateButtons[a].grid(column=3, row=(1 + a), padx=(30, 0))
                self.removeButtons[a].grid(column=4, row=(1 + a), padx=(30, 0))

            for x in range(len(self.items)):
                self.itemNames[x].insert(0, list(self.items.keys())[x])
                self.itemNames[x].config(state=tk.DISABLED)
                self.itemPrice[x].insert(0, self.items[list(self.items.keys())[x]][0])
                self.itemPrice[x].config(state=tk.DISABLED)
                self.itemStock[x].insert(0, self.items[list(self.items.keys())[x]][1])
                self.itemStock[x].config(state=tk.DISABLED)

        root.protocol("WM_DELETE_WINDOW", self.goBack)

    def astockScroll(self, event):
        self.astockCanvas.config(scrollregion=self.astockCanvas.bbox('all'))

    def updateBtn(self, number):
        self.editing = True
        self.itemNames[number].config(state=tk.NORMAL)
        self.itemNames[number].config(bg="lightblue")
        self.itemPrice[number].config(state=tk.NORMAL)
        self.itemPrice[number].config(bg="lightblue")
        self.itemStock[number].config(state=tk.NORMAL)
        self.itemStock[number].config(bg="lightblue")

        self.updateButtons[number].grid_forget()
        self.removeButtons[number].grid_forget()
        self.doneButtons[number].grid(column=3, row=1 + number, padx=(30, 0))
        self.cancelButtons[number].grid(column=4, row=1 + number, padx=(30, 0))

    def doneBtn(self, number):
        global name, room
        if (len(str(self.itemNames[number].get())) != 0 and len(str(self.itemPrice[number].get())) != 0 and len(str(self.itemStock[number].get())) != 0):
            try:
                float(self.itemPrice[number].get())
            except ValueError:
                msg.showerror(ROOT_TITLE, "Price must be positive integer or a real number (more than 0).")
                self.itemPrice[number].config(bg="red")
            else:
                if float(self.itemPrice[number].get()) <= 0:
                    msg.showerror(ROOT_TITLE, "Price must be positive integer or a real number (more than 0).")
                    self.itemPrice[number].config(bg="red")
                else:
                    try:
                        int(self.itemStock[number].get())
                    except ValueError:
                        msg.showerror(ROOT_TITLE, "Stock must be positive integer (more than 0).")
                        self.itemStock[number].config(bg="red")
                    else:
                        if int(self.itemStock[number].get()) <= 0:
                            msg.showerror(ROOT_TITLE, "Stock must be positive integer (more than 0).")
                        else:
                            self.itemNames[number].config(state=tk.DISABLED)
                            self.itemPrice[number].config(state=tk.DISABLED)
                            self.itemStock[number].config(state=tk.DISABLED)

                            self.doneButtons[number].grid_forget()
                            self.updateButtons[number].grid(column=3, row=1 + number)
                            self.removeButtons[number].grid(column=4, row=1 + number)

                            if self.itemStock[number].get() == "0" or self.itemStock[number].get() == 0:
                                if not self.adding:
                                    self.removeItem(number)
                                else:
                                    self.itemStock[number].config(bg="red")
                                    msg.showinfo(ROOT_TITLE, "Stock cannot be 0. Item addition cancelled")

                            if not self.adding:
                                if user["is_masteradmin"]:
                                    WriteInLog("Master Admin {} has updated item '{}' in the database.".format(user["name"], self.itemNames[number].get()))
                                else:
                                    WriteInLog("Admin {} has updated item '{}' in the database.".format(user["name"], self.itemNames[number].get()))

                                db_query("UPDATE `items` SET `price` = %f, `stock` = %i WHERE `name` = '%s'" % (float(self.itemPrice[number].get()), int(self.itemStock[number].get()), self.itemNames[number].get()), "u")
                            else:
                                if user["is_masteradmin"]:
                                    WriteInLog("Master Admin {} has added '{}' to the database.".format(user["name"], self.itemNames[number].get()))
                                else:
                                    WriteInLog("Admin {} has added '{}' to the database.".format(user["name"], self.itemNames[number].get()))

                                db_query("INSERT INTO `items` (`name`, `price`, `stock`) VALUES ('%s', %f, %i)" % (self.itemNames[number].get(), float(self.itemPrice[number].get()), int(self.itemStock[number].get())), "i")

                            self.editing = False
                            self.adding = False
                            for child in root.winfo_children():
                                child.destroy()
                            room = AdminStock()

        else:
            if len(str(self.itemNames[number].get())) == 0:
                self.itemNames[number].config(bg="red")
                msg.showinfo(ROOT_TITLE, "Item name cannot be empty.")
            if len(str(self.itemPrice[number].get())) == 0:
                self.itemPrice[number].config(bg="red")
                msg.showinfo(ROOT_TITLE, "Item price cannot be empty.")
            if len(str(self.itemStock[number].get())) == 0:
                self.itemStock[number].config(bg="red")
                msg.showinfo(ROOT_TITLE, "Item stock cannot be empty.")

    def removeItem(self, number):
        global user, room
        remove = self.itemNames[number].get()
        if msg.askyesno("Remove item", "Are you sure you wish to remove %s from the database?" % (remove)):
            if user["is_masteradmin"]:
                WriteInLog("Master Admin {} has removed '{}' from the database.".format(user["name"], remove))

            else:
                WriteInLog("Admin {} has removed '{}' from the database.".format(user["name"], remove))

            db_query("DELETE FROM `items` WHERE `name` = '%s'" % (remove), "d")

            for child in root.winfo_children():
                child.destroy()
            room = AdminStock()

    def add_item(self, number):
        if not self.editing:
            if not self.item_DB:
                self.message.grid_forget()

            self.editing = True
            self.adding = True

            self.itemNames.append(tk.Entry(self.stockList, font=("Flux", 14, "bold"), state=tk.NORMAL, disabledbackground="lightgrey", disabledforeground="black", bg="powderblue", relief=tk.SUNKEN, width=12, justify="center"))
            self.itemPrice.append(tk.Entry(self.stockList, font=("Flux", 14, "bold"), state=tk.NORMAL, disabledbackground="lightgrey", disabledforeground="black", bg="powderblue", relief=tk.SUNKEN, width=12, justify="center"))
            self.itemStock.append(tk.Entry(self.stockList, font=("Flux", 14, "bold"), state=tk.NORMAL, disabledbackground="lightgrey", disabledforeground="black", bg="powderblue", relief=tk.SUNKEN, width=12, justify="center"))

            self.updateButtons.append(tk.Button(self.stockList, font=("Flux", 11, "bold"), text="Update", command=lambda number=number: self.updateBtn(number)))
            self.removeButtons.append(tk.Button(self.stockList, font=("Flux", 11, "bold"), text="Remove", command=lambda number=number: self.removeItem(number)))
            self.doneButtons.append(tk.Button(self.stockList, font=("Flux", 11, "bold"), text="Done", command=lambda number=number: self.doneBtn(number)))
            self.cancelButtons.append(tk.Button(self.stockList, font=("Flux", 11, "bold"), text="Cancel", command=self.cancel))

            self.itemNames[number].grid(column=0, row=(1 + number), padx=(30, 0))
            self.itemPrice[number].grid(column=1, row=(1 + number), padx=(30, 0))
            self.itemStock[number].grid(column=2, row=(1 + number), padx=(30, 0))
            self.doneButtons[number].grid(column=3, row=(1 + number), padx=(30, 0))
            self.cancelButtons[number].grid(column=4, row=(1 + number), padx=(30, 0))

            self.itemNames[number].bind("<Button-1>", lambda event, number=number: self.inputFocus(event, number=number, item=self.itemNames))
            self.itemNames[number].bind("<KeyPress>", lambda event, number=number: self.inputFocus(event, number=number, item=self.itemNames))
            self.itemPrice[number].bind("<Button-1>", lambda event, number=number: self.inputFocus(event, number=number, item=self.itemPrice))
            self.itemPrice[number].bind("<KeyPress>", lambda event, number=number: self.inputFocus(event, number=number, item=self.itemPrice))
            self.itemStock[number].bind("<Button-1>", lambda event, number=number: self.inputFocus(event, number=number, item=self.itemStock))
            self.itemStock[number].bind("<KeyPress>", lambda event, number=number: self.inputFocus(event, number=number, item=self.itemStock))

            self.itemNames[number].bind("<Button-1>", lambda event, number=number: self.inputFocus(event, number=number, item=self.itemNames))
            self.itemNames[number].bind("<KeyPress>", lambda event, number=number: self.inputFocus(event, number=number, item=self.itemNames))
            self.itemPrice[number].bind("<Button-1>", lambda event, number=number: self.inputFocus(event, number=number, item=self.itemPrice))
            self.itemPrice[number].bind("<KeyPress>", lambda event, number=number: self.inputFocus(event, number=number, item=self.itemPrice))
            self.itemStock[number].bind("<Button-1>", lambda event, number=number: self.inputFocus(event, number=number, item=self.itemStock))
            self.itemStock[number].bind("<KeyPress>", lambda event, number=number: self.inputFocus(event, number=number, item=self.itemStock))

            root.update()
            self.astockCanvas.update()
            self.stockList.update()
            self.astockScrollbar.update()
            self.astockCanvas.config(scrollregion=self.astockCanvas.bbox('all'))

        else:
            msg.showinfo(ROOT_TITLE, "Please finish your editing first!")

    def goBack(self):
        global room
        if not self.editing:
            for child in root.winfo_children():
                child.destroy()
            room = AdminPanel()
        else:
            msg.showinfo("Incomplete editing.", "You have not finished editing the database.")

    def inputFocus(self, event, item, number):
        item[number].config(bg='blue')
        if item[number]['state'] != tk.DISABLED:
            item[number].config(fg="white")

        if item[number] != self.itemNames[number] and self.itemNames[number]['bg'] != 'red':
            self.itemNames[number].config(bg='lightblue')
            self.itemNames[number].config(fg='black')

        if item[number] != self.itemPrice[number] and self.itemPrice[number]['bg'] != 'red':
            self.itemPrice[number].config(bg='lightblue')
            self.itemPrice[number].config(fg='black')

        if item[number] != self.itemStock[number] and self.itemStock[number]['bg'] != 'red':
            self.itemStock[number].config(bg='lightblue')
            self.itemStock[number].config(fg='black')

    def cancel(self):
        global room
        for child in root.winfo_children():
            child.destroy()

        room = AdminStock()


class TransactionScreen:
    def __init__(self):
        global user
        root.protocol('WM_DELETE_WINDOW', self.goBack)

        tk.Label(root, font=("Flux", 32, "bold"), text="List of orders", bg="white").pack(side=tk.TOP, anchor=tk.CENTER)

        self.customer_names = []

        orders = db_query("SELECT `customer_id` FROM `orders`", "s")

        for order in orders:
            self.customer_names.append(db_query("SELECT `name` FROM `accounts` WHERE `id` = %i" % (order[0]), "s")[0][0])

        self.tsCanvas = tk.Canvas(root, bg="white")
        self.tsCanvas.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        self.tsFrame = tk.Frame(self.tsCanvas, bg="white")
        root.update()
        self.tsCanvas.create_window((0, 0), window=self.tsFrame, anchor=tk.NW, width=(self.tsCanvas.winfo_width() - 20))
        self.tsScroll = tk.Scrollbar(self.tsCanvas, orient=tk.VERTICAL, command=self.tsCanvas.yview)
        self.tsScroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.tsCanvas.config(yscrollcommand=self.tsScroll.set)
        self.tsCanvas.bind("<Configure>", self.tsScrollcmd)

        tk.Button(root, font=("Flux", 14, "bold"), text="Back", command=self.goBack).pack(side=tk.BOTTOM, anchor=tk.E)
        tk.Label(root, font=12, text="Name: " + str(user["name"]), bg="white").pack(side=tk.BOTTOM, anchor=tk.W, pady=(20, 0))

        if not self.customer_names:
            tk.Label(self.tsFrame, font=("Flux", 18, "bold"), text="There are no pending orders", bg="white").pack(anchor=tk.CENTER, padx=170, pady=60, fill=tk.BOTH)

        else:
            self.nameLabels = []
            for x in range(len(self.customer_names)):
                self.nameLabels.append(tk.Label(self.tsFrame, font=("Flux", 20, "bold"), text=str(self.customer_names[x]), bg="white", cursor="hand2"))
                self.nameLabels[x].pack(anchor=tk.CENTER, fill=tk.X, pady=(10, 0))
                self.nameLabels[x].bind("<Motion>", lambda event, x=x: self.mouse_enter(event, x))
                self.nameLabels[x].bind("<Leave>", lambda event, x=x: self.mouse_leave(event, x))
                self.nameLabels[x].bind("<Button-1>", lambda event, x=x: self.open_screen(event, x))

    def tsScrollcmd(self, event):
        self.tsCanvas.config(scrollregion=self.tsCanvas.bbox('all'))

    def goBack(self):
        global room
        for child in root.winfo_children():
            child.destroy()

        room = AdminPanel()

    def mouse_enter(self, event, number):
        self.nameLabels[number].config(bg="lightblue")

    def mouse_leave(self, event, number):
        self.nameLabels[number].config(bg="white")

    def open_screen(self, event, number):
        global customer_id, room
        customer_id = db_query("SELECT `id` FROM `accounts` WHERE `name` = '%s'" % (self.nameLabels[number]['text']), "s")[0][0]
        for child in root.winfo_children():
            child.destroy()

        room = CustomerOrders()


class CustomerOrders:

    def __init__(self):
        global user, customer_id, room
        root.protocol('WM_DELETE_WINDOW', self.go_back)

        self.customer_name = db_query("SELECT `name` FROM `accounts` WHERE `id` = %i" % (int(customer_id)), "s")[0][0]

        self.coCanvas = tk.Canvas(root, bg="white")
        self.coCanvas.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        self.coFrame = tk.Frame(self.coCanvas, bg="white")
        self.coCanvas.create_window((0, 0), window=self.coFrame, anchor=tk.NW)
        self.coScroll = tk.Scrollbar(self.coCanvas, command=self.coCanvas.yview)
        self.coScroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.coCanvas.config(yscrollcommand=self.coScroll.set)
        self.coCanvas.bind("<Configure>", self.co_scroll)

        tk.Label(root, font=("Flux", 32, "bold"), text="%s's orders" % (self.customer_name), bg="white").pack(side=tk.TOP, anchor=tk.CENTER)
        self.actionButtons = tk.Frame(root, bg="white")
        self.actionButtons.pack(side=tk.BOTTOM, anchor=tk.SE)
        tk.Button(self.actionButtons, font=("Flux", 14, "bold"), text="Back", command=self.go_back).pack(side=tk.RIGHT)
        tk.Button(self.actionButtons, font=("Flux", 14, "bold"), text="Order complete", command=self.order_complete).pack(side=tk.RIGHT)
        tk.Label(root, font=12, text="Name: " + str(user["name"]), bg="white").pack(side=tk.BOTTOM, anchor=tk.SW, pady=(40, 0))

        tk.Label(self.coFrame, font=("Flux", 14, "bold"), text="Item Names", bg="white").grid(row=0, column=0, padx=(30, 0))
        tk.Label(self.coFrame, font=("Flux", 14, "bold"), text="Item Number", bg="white").grid(row=0, column=1, padx=(250, 0))

        item_stuff = db_query("SELECT `items`, `number_ordered` FROM `orders` WHERE `customer_id` = %i" % (int(customer_id)), "s")
        print(item_stuff)

        items_ordered = item_stuff[0][0].split(",")
        numbers_ordered = item_stuff[0][1].split(",")

        self.itemNames = []
        self.itemNumbers = []
        for x in range(len(items_ordered)):
            self.itemNames.append(tk.Label(self.coFrame, font=("Flux", 14, "bold"), text=str(items_ordered[x]), bg="white"))
            self.itemNumbers.append(tk.Label(self.coFrame, font=("Flux", 14, "bold"), text=str(numbers_ordered[x]), bg="white"))

        for items in range(len(self.itemNames)):
            self.itemNames[items].grid(column=0, row=1 + items, padx=(30, 0))
            self.itemNumbers[items].grid(column=1, row=1 + items, padx=(250, 0))

    def co_scroll(self, event):
        self.coCanvas.config(scrollregion=self.coCanvas.bbox('all'))

    def go_back(self):
        global room
        for child in root.winfo_children():
            child.destroy()

        room = TransactionScreen()

    def order_complete(self):
        global user, room, customer_id
        if user["is_masteradmin"]:
            WriteInLog("Master Admin {} has confirmed that customer {}'s ordered item(s) have been delivered.".format(user["name"], self.customer_name))
        else:
            WriteInLog("Admin {} has confirmed that customer {}'s ordered item(s) have been delivered.".format(user["name"], self.customer_name))
        order_items = {}
        for x in range(len(self.itemNames)):
            if int(self.itemNumbers[x]['text']) != 0:
                order_items.update({self.itemNames[x]['text']: int(self.itemNumbers[x]['text'])})
        stock_array = {}

        stock = db_query("SELECT * FROM `items`", "s")

        for item in stock:
            stock_array.update({item[0]: item[2]})

        for item in order_items:
            stock_array[item] -= order_items[item]

        for item in stock_array:
            db_query("UPDATE `items` SET 'stock' = %i WHERE `name` = '%s'" % (stock_array[item], item), "u")

        db_query("DELETE FROM `orders` WHERE `customer_id` = %i" % (int(customer_id)), "d")

        msg.showinfo(ROOT_TITLE, "Item database updated.")

        for child in root.winfo_children():
            child.destroy()

        room = TransactionScreen()


class CustomerPanel:
    def __init__(self):
        global user

        self.cpCanvas = tk.Canvas(root, bg="white")
        self.cpCanvas.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        self.itemList = tk.Frame(self.cpCanvas, bg="white", width=640)
        self.cpCanvas.create_window((0, 0), window=self.itemList, anchor=tk.NW)
        self.cpScroll = tk.Scrollbar(self.cpCanvas, orient=tk.VERTICAL, command=self.cpCanvas.yview)
        self.cpScroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.cpCanvas.config(yscrollcommand=self.cpScroll.set)
        self.cpCanvas.bind("<Configure>", self.customerScroll)

        self.panelHeader = tk.Label(root, font=("Flux", 32, "bold"), text="Purchase items", bg="white")
        self.panelHeader.pack(side=tk.TOP, anchor=tk.CENTER)

        self.actionButtons = tk.Frame(root)
        self.actionButtons.pack(side=tk.BOTTOM, anchor=tk.SE)

        self.nameInfo = tk.Label(root, font=(12), text="Name: " + user["name"], bg="white")
        self.nameInfo.pack(side=tk.BOTTOM, anchor=tk.SW, pady=(90, 0))

        self.logoutBtn = tk.Button(self.actionButtons, font=("Flux", 14, "bold"), text="Logout", command=self.logOut)
        self.logoutBtn.pack(side=tk.RIGHT)
        self.addItem = tk.Button(self.actionButtons, font=("Flux", 14, "bold"), text="Add to shopping cart", command=self.toCart)
        self.addItem.pack(side=tk.RIGHT)

        self.item_DB = db_query("SELECT * FROM `items`", "s")

        if not self.item_DB:
            message = tk.Label(self.itemList, font=("Flux", 18, "bold"), text="Sorry but we're sold out!", bg="white")
            message.pack(anchor=tk.W, padx=200, pady=119)

        else:
            tk.Label(self.itemList, font=("Flux", 14, "bold"), text="Name", bg="white").grid(column=0, row=0, padx=(30, 0))
            tk.Label(self.itemList, font=("Flux", 14, "bold"), text="Price", bg="white").grid(column=1, row=0, padx=(100, 0))
            tk.Label(self.itemList, font=("Flux", 14, "bold"), text="Stock", bg="white").grid(column=2, row=0, padx=(100, 0))
            tk.Label(self.itemList, font=("Flux", 14, "bold"), text="Purchase number", bg="white").grid(column=3, row=0, sticky=tk.E)

            self.items = {}

            for item in self.item_DB:
                self.items.update({item[0]: [item[1], item[2]]})

            self.itemNames = []
            self.itemPrice = []
            self.itemStock = []
            self.purchase_number = []

            for name, info in self.items.items():
                self.itemNames.append(tk.Label(self.itemList, font=("Flux", 14, "bold"), bg="white", text=name))
                self.itemPrice.append(tk.Label(self.itemList, font=("Flux", 14, "bold"), bg="white", text=info[0]))
                self.itemStock.append(tk.Label(self.itemList, font=("Flux", 14, "bold"), bg="white", text=info[1]))
                self.purchase_number.append(tk.Entry(self.itemList, font=("Flux", 14, "bold"), bg="lightgrey", relief=tk.SUNKEN, width=12, justify="center"))
                x = list(self.items.keys()).index(name)
                self.purchase_number[x].bind("<Button-1>", lambda event, x=x: self.inputFocus(event, x))
                self.purchase_number[x].bind("<KeyPress>", lambda event, x=x: self.inputFocus(event, x))
                self.purchase_number[x].insert(0, "0")

            for a in range(len(self.item_DB)):
                self.itemNames[a].grid(column=0, row=1 + a, padx=(30, 0))
                self.itemPrice[a].grid(column=1, row=1 + a, padx=(100, 0))
                self.itemStock[a].grid(column=2, row=1 + a, padx=(100, 0))
                self.purchase_number[a].grid(column=3, row=1 + a, padx=(92, 0))
        global shopping_cart
        shopping_cart = ShoppingCart()
        shopping_cart.cart.lift()
        root.protocol('WM_DELETE_WINDOW', self.logOut)

    def customerScroll(self, event):
        self.cpCanvas.config(scrollregion=self.cpCanvas.bbox('all'))

    def toCart(self):
        global name
        global shopping_cart
        error_detected = False
        for each in self.purchase_number:
            if len(each.get()) == 0:
                each.insert(0, "0")

            try:
                int(each.get())

            except ValueError:
                msg.showinfo(ROOT_TITLE, "Invalid input. Input must be a positive integer.")
                self.purchase_number[self.purchase_number.index(each)].config(bg="red")
                error_detected = True

            else:
                if int(each.get()) < 0:
                    msg.showinfo(ROOT_TITLE, "Invalid input. Input must be a positive integer.")
                    self.purchase_number[self.purchase_number.index(each)].config(bg="red")
                    error_detected = True
                else:
                    if int(each.get()) <= int(list(self.items.values())[self.purchase_number.index(each)][1]):

                        if len(each.get()) > 0:

                            db_query("DELETE FROM `orders` WHERE `customer_id` = %i" % (db_query("SELECT `id` FROM `accounts` WHERE `name` = '%s'" % (user["name"]), "s")[0][0]), "d")

                            if int(each.get()) != 0:
                                cart_items.update({str(self.itemNames[self.purchase_number.index(each)]['text']): int(each.get())})
                                cart_prices.update({str(self.itemNames[self.purchase_number.index(each)]['text']): int(self.itemPrice[self.purchase_number.index(each)]['text'])})

                    else:
                        msg.showinfo(ROOT_TITLE, "Input number exceeds value in stock.")
                        self.purchase_number[self.purchase_number.index(each)].config(bg="red")
                        error_detected = True

        if not error_detected:
            shopping_cart.cart.destroy()
            shopping_cart = ShoppingCart()
            shopping_cart.cart.lift()

    def inputFocus(self, event, number):
        for each in self.purchase_number:
            if self.purchase_number.index(each) == number:
                each.config(bg="lightblue")
            else:
                if each['bg'] != "red":
                    each.config(bg="lightgrey")

                if len(self.purchase_number[self.purchase_number.index(each)].get()) == 0:
                    self.purchase_number[self.purchase_number.index(each)].insert(0, "0")

    def logOut(self):
        global user, room
        if cart_items != {}:

            if msg.askyesno(ROOT_TITLE, "Are you sure you wish cancel your order and log out?"):
                WriteInLog("Customer {} has logged out.".format(user["name"]))
                for child in root.winfo_children():
                    child.destroy()

                room = MainMenu()
                user["name"] = ""

        else:
            WriteInLog("Customer {} has logged out.\n".format(user["name"]))
            for child in root.winfo_children():
                child.destroy()

            room = MainMenu()
            user["name"] = ""


class ShoppingCart:
    def __init__(self):
        global name
        global cart_items

        self.customerID = db_query("SELECT `id` FROM `accounts` WHERE `name` = '%s'" % (user["name"]), "s")[0][0]

        order_items = db_query("SELECT * FROM `orders` WHERE `customer_id` = %i" % (int(self.customerID)), "s")

        if order_items:
            order_items = order_items[0]
            names = order_items[1].split(",")
            numbers = order_items[2].split(",")

            for x in range(len(names)):
                cart_items.update({names[x]: numbers[x]})

        self.cart = tk.Toplevel()
        self.cart.title("Shopping Cart")
        self.cart.resizable(0, 0)
        self.cart.config(background="white")
        self.cart.protocol("WM_DELETE_WINDOW", self.passOn)

        self.cartCanvas = tk.Canvas(self.cart, bg="white")
        self.cartFrame = tk.Frame(self.cart, bg="white")
        self.cartScroll = tk.Scrollbar(self.cartCanvas, orient=tk.VERTICAL, command=self.cartCanvas.yview)
        self.cartCanvas.config(yscrollcommand=self.cartScroll.set)
        self.cartCanvas.bind("<Configure>", self.cartScrollcmd)
        self.buyItems = tk.Button(self.cart, font=("Flux", 12, "bold"), text="Buy Items", command=self.buyItems)
        self.removeAll = tk.Button(self.cart, font=("Flux", 12, "bold"), text="Remove All", command=self.remove_all)

        if cart_items == {}:
            self.cart.geometry("200x200")
            self.empty_cart = tk.Label(self.cart, font=("Flux", 12, "bold"), text="No items in shopping cart", bg="white")
            self.cart.update()
            self.empty_cart.place(x=(self.cart.winfo_width() / 2), y=(self.cart.winfo_height() / 2), anchor=tk.CENTER)
        else:
            self.cart.geometry("698x200")
            self.initialize()
            self.placeItems()

    def initialize(self):
        self.cartNames = list(tk.Label(self.cartFrame, font=("Flux", 12, "bold"), text=list(cart_items.keys())[a], bg="white") for a in range(len(list(cart_items.keys()))))
        self.cartNumber = list(tk.Label(self.cartFrame, font=("Flux", 12, "bold"), text=list(cart_items.values())[b], bg="white") for b in range(len(list(cart_items.keys()))))
        self.cartReturnTextVar = list(tk.StringVar() for c in range(len(list(cart_items.keys()))))
        for stuff in self.cartReturnTextVar:
            stuff.set("0")
        self.cartReturn = list(tk.Entry(self.cartFrame, font=("Flux", 12, "bold"), textvariable=self.cartReturnTextVar[d], bg="lightgrey", justify="center", relief=tk.SUNKEN) for d in range(len(list(cart_items.keys()))))
        self.returnButton = list(tk.Button(self.cartFrame, font=("Flux", 12, "bold"), text="Return", command=lambda e=e: self.returnItem(e)) for e in range(len(list(cart_items.keys()))))
        self.remove_item = list(tk.Button(self.cartFrame, font=("Flux", 12, "bold"), text="Remove Item", command=lambda f=f: self.removeItem(f)) for f in range(len(list(cart_items.keys()))))

    def placeItems(self):
        tk.Label(self.cartFrame, font=("Flux", 12, "bold"), text="Item Name", bg="white").grid(row=0, column=0, pady=8)
        tk.Label(self.cartFrame, font=("Flux", 12, "bold"), text="Number of items purchased", bg="white").grid(row=0, column=1, padx=12, pady=8)
        tk.Label(self.cartFrame, font=("Flux", 12, "bold"), text="Number of items to return", bg="white").grid(row=0, column=2, padx=12, pady=8)
        tk.Label(self.cartFrame, font=("Flux", 12, "bold"), text="Return", bg="white").grid(row=0, column=3, padx=12, pady=8)
        tk.Label(self.cartFrame, font=("Flux", 12, "bold"), text="Remove Item", bg="white").grid(row=0, column=4, padx=12, pady=8)
        self.cartCanvas.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        self.cartScroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.cartCanvas.create_window((0, 0), window=self.cartFrame, anchor=tk.NW)
        self.buyItems.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.removeAll.pack(side=tk.LEFT, fill=tk.X, expand=True)

        for items in range(len(self.cartNames)):
            self.cartNames[items].grid(row=items + 1, column=0)
            self.cartNumber[items].grid(row=items + 1, column=1, padx=12)
            self.cartReturn[items].grid(row=items + 1, column=2, padx=12)
            self.cartReturn[items].bind("<Button-1>", lambda event, items=items: self.inputFocus(event, items))
            self.cartReturn[items].bind("<KeyPress>", lambda event, items=items: self.inputFocus(event, items))
            self.returnButton[items].grid(row=items + 1, column=3, padx=12)
            self.remove_item[items].grid(row=items + 1, column=4, padx=12)

    def passOn(self):
        self.cart.bell()

    def remove_all(self):
        global cart_items
        global shopping_cart
        if msg.askyesno(ROOT_TITLE, "Are you sure you wish to remove all items from the shopping cart?"):
            db_query("DELETE FROM `orders` WHERE `customer_id` = %i" % (int(self.customerID)), "d")
            cart_items = {}
            shopping_cart.cart.destroy()
            del shopping_cart
            shopping_cart = ShoppingCart()

    def removeItem(self, number):
        global cart_items, shopping_cart
        if msg.askyesno(ROOT_TITLE, "Are you sure you wish to remove %s from the shopping cart?" % (list(cart_items.keys())[number])):
            del(cart_items[list(cart_items.keys())[number]])

            for child in self.cartFrame.winfo_children():
                child.destroy()

            if cart_items != {}:
                self.initialize()
                self.placeItems()
            else:

                cart_items = {}
                shopping_cart.cart.destroy()
                del shopping_cart
                shopping_cart = ShoppingCart()

    def inputFocus(self, event, number):
        for each in self.cartReturn:
            if self.cartReturn.index(each) == number:
                each.config(bg="lightblue")
            else:
                if each['bg'] != 'red':
                    each.config(bg="lightgrey")

                if len(self.cartReturnTextVar[self.cartReturn.index(each)].get()) == 0:
                    self.cartReturnTextVar[self.cartReturn.index(each)].set("0")

    def returnItem(self, number):
        if len(self.cartReturnTextVar[number].get()) == 0:
            self.cartReturnTextVar[number].set("0")

        if self.cartReturnTextVar[number].get().isdigit():
            if int(self.cartReturnTextVar[number].get()) > 0:
                if int(self.cartReturnTextVar[number].get()) < int(list(cart_items.values())[number]):
                    cart_items[list(cart_items.keys())[number]] -= int(self.cartReturnTextVar[number].get())

                    for child in self.cartFrame.winfo_children():
                        child.destroy()

                    self.initialize()
                    self.placeItems()

                elif int(self.cartReturnTextVar[number].get()) == int(list(cart_items.values())[number]):
                    self.removeItem(number)
                else:
                    msg.showinfo(ROOT_TITLE, "You have not bought that many of that item.")
                    self.cartReturn[number].config(bg="red")
        else:
            msg.showinfo(ROOT_TITLE, "Invalid input. Input must be a positive integer.")
            self.cartReturn[number].config(bg="red")

    def buyItems(self):
        global room
        self.cart.destroy()
        for child in root.winfo_children():
            child.destroy()
        room = PurchaseScreen()

    def cartScrollcmd(self, event):
        self.cartCanvas.config(scrollregion=self.cartCanvas.bbox('all'))


class PurchaseScreen:
    def __init__(self):
        global user

        total_price = 0
        for items in cart_items:
            total_price += int(cart_items[items]) * int(cart_prices[items])
        self.Total = tk.Label(root, font=("Flux", 18, "bold"), text="Total price: " + str(total_price), bg="lightgrey", anchor=tk.E)
        self.Total.pack(side=tk.BOTTOM, anchor=tk.SE, fill=tk.X, pady=(0, 0))
        self.box = tk.Canvas(root, bg="white")
        self.box.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        self.purchaseFrame = tk.Frame(self.box, bg="white")
        self.box.create_window((0, 0), window=self.purchaseFrame, anchor=tk.NW)
        self.purchaseScroll = tk.Scrollbar(self.box, orient=tk.VERTICAL, command=self.box.yview)
        self.purchaseScroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.box.config(yscrollcommand=self.purchaseScroll.set)
        self.box.bind("<Configure>", self.purchaseScrollcmd)

        self.buyLabel = tk.Label(root, font=("Flux", 32, "bold"), text="Buy Items", bg="white")
        self.buyLabel.pack(side=tk.TOP, anchor=tk.CENTER)
        tk.Label(root, font=12, text="Name: " + str(user["name"]), bg="white").pack(side=tk.TOP, anchor=tk.NW)

        self.confirm = tk.Button(root, font=("Flux", 14, "bold"), text="Confirm purchase", command=self.ConfirmPurchase)
        self.confirm.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.goBack = tk.Button(root, font=("Flux", 14, "bold"), text="Back", command=self.go_back)
        self.goBack.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.buy_Items = list(tk.Label(self.purchaseFrame, font=("Flux", 14, "bold"), text=itemname, bg="white") for itemname in list(cart_items.keys()))
        self.buy_price = list(tk.Label(self.purchaseFrame, font=("Flux", 14, "bold"), text=itemprice, bg="white") for itemprice in list(cart_prices.values()))
        self.buy_number = list(tk.Label(self.purchaseFrame, font=("Flux", 14, "bold"), text=itemnumber, bg="white") for itemnumber in list(cart_items.values()))
        tk.Label(self.purchaseFrame, font=("Flux", 14, "bold"), text="Item name", bg="white").grid(row=0, column=0)
        tk.Label(self.purchaseFrame, font=("Flux", 14, "bold"), text="Item price", bg="white").grid(row=0, column=1)
        tk.Label(self.purchaseFrame, font=("Flux", 14, "bold"), text="Items added", bg="white").grid(row=0, column=2)
        for each in range(len(self.buy_Items)):
            self.buy_Items[each].grid(row=each + 1, column=0)
            self.buy_price[each].grid(row=each + 1, column=1, padx=150)
            self.buy_number[each].grid(row=each + 1, column=2, padx=100)

        root.protocol("WM_DELETE_WINDOW", self.go_back)

    def go_back(self):
        global room
        for child in root.winfo_children():
            child.destroy()

        room = CustomerPanel()

    def ConfirmPurchase(self):
        # item_Prices = {}
        # item_Stocks = {}
        global cart_items, cart_prices, user, room

        customerID = db_query("SELECT `id` FROM `accounts` WHERE `name` = '%s'" % (user["name"]), "s")[0][0]

        this_order = db_query("SELECT `items`, `number_ordered` FROM `orders` WHERE `customer_id` = %i" % (int(customerID)), "s")

        if this_order:

            db_query("UPDATE `orders` SET `items` = '%s', `number_ordered` '%s' WHERE `customer_id` = %i" % (",".join(list(cart_items.keys())), ",".join(list(cart_items.values())), int(customerID)), "u")

        else:
            db_query("INSERT INTO `orders` (`customer_id`, `items`, `number_ordered`) VALUES (%i, '%s', '%s')" % (customerID, ",".join(list(cart_items.keys())), ",".join(str(x) for x in list(cart_items.values()))), "i")

        msg.showinfo(ROOT_TITLE, "Your order has been placed. Thank you for purchasing at Sajeed's Python Super Market!")
        WriteInLog("Customer {} has placed/edited their order.".format(user["name"]))
        for child in root.winfo_children():
            child.destroy()
        room = MainMenu()
        cart_items = {}
        cart_prices = {}

    def purchaseScrollcmd(self, event):
        self.box.config(scrollregion=self.box.bbox('all'))


room = MainMenu()
root.mainloop()
raise SystemExit()
