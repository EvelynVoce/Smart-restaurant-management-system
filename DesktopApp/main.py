import os
import tkinter as tk
from tkinter import font
from tkinter import ttk
from tkinter import messagebox
from tkinter import colorchooser
import account_handling
from fridge import Fridge
from fridge_db import display_fridge_contents, login, signup,\
    display_item_alerts, generate_health_report, display_users, remove_items, remove_user
from datetime import datetime
from threading import Thread
import csv

bg_col: str = "grey"
fg_col: str = "white"
button_col: str = "dark grey"

root = tk.Tk()
root.geometry(f"{root.winfo_screenwidth()}x{root.winfo_screenheight()}+-5+0")
root.title("Monty Pythons")
root.config(bg=bg_col)


def change_background():
    global bg_col
    bg_col = colorchooser.askcolor()[1]
    root.config(bg=bg_col)


def change_foreground():
    global fg_col
    fg_col = colorchooser.askcolor()[1]


def close_app(event=None):
    root.destroy()


root.bind('<Escape>', close_app)


def clear_root():
    for ele in root.winfo_children():
        ele.destroy()


def underline(label):
    f = font.Font(label, label.cget("font"))  # Create custom font
    f.configure(underline=True)  # Underline font
    label.configure(font=f)  # Apply font to the given label


def create_back_button() -> tk.Button:
    back_button = tk.Button(root, text="back", font=("arial", 10, "bold"), bg=button_col)
    back_button.place(relx=0.90, rely=0.05, relwidth=0.1, relheight=0.05, anchor=tk.CENTER)
    return back_button


def get_role(roles: list[bool]) -> str:
    valid: bool = True if sum(roles) == 1 else False
    if not valid:
        messagebox.showinfo(message="ERROR: One and only one role may be selected at once")
        return "Role Invalid"
    role_vals = ("Head Chef", "Chef")
    return role_vals[roles.index(True)]


def create_account(username: str, password: str, name: str, restaurant: str, roles: list[bool]):
    role: str = get_role(roles)
    if role == "Role Invalid":
        return

    general_account = account_handling.Account(username, password, name, role, restaurant)
    account = account_handling.type_account(username, password, general_account)
    submission = signup(account.username, account.password, account.name, account.role, account.restaurant)
    if submission != "Unsuccessful query.":
        clear_root()
        item_alert(account) if account.role == "Head Chef" else profile_screen(account)


def login_account(username: str, password: str):
    clear_root()
    general_account = account_handling.Account(username, password)
    user_details = login(general_account.username, general_account.password)
    if user_details == "Incorrect login details provided.":
        clear_root()
        main_screen()
    else:
        general_account.name = user_details[0][0]
        general_account.role = user_details[0][1]
        general_account.restaurant = user_details[0][2]
        account = account_handling.type_account(username, password, general_account)
        item_alert(account) if account.role == "Head Chef" else profile_screen(account)


def read_file(relative_path: str) -> str:
    current_path = os.path.dirname(__file__)
    file_path = os.path.relpath(relative_path, current_path)

    with open(file_path, "r") as f:
        help_text: str = f.read()
    return help_text


def help_func(user_account: account_handling.Account, pageType: str):
    help_text: str = read_file(pageType)

    page_title = tk.Label(root, text="MontyFridges: Information Help Page",
                          font=("arial", 28, "bold"), fg=fg_col, bg=bg_col)
    page_title.place(relx=0.4, rely=0.05, anchor=tk.CENTER)
    underline(page_title)

    back_button = create_back_button()
    back_button.place(relx=0.90, rely=0.05, relwidth=0.15, relheight=0.05, anchor=tk.CENTER)
    back_button.config(command=lambda: clear_root() or fridge_contents(user_account))

    page_information = tk.Label(root, text=help_text,
                                font=("arial", 12, "bold"), fg="black", bg="white")
    page_information.place(relx=0.5, rely=0.5, relwidth=0.90, relheight=0.80, anchor=tk.CENTER)


def change_name_func(user_account: account_handling.Account):
    messagebox.showinfo(message="Feature not yet implemented")
    profile_screen(user_account)


def profile_screen(user_account: account_handling.Account):
    page_title = tk.Label(root, text="MontyFridges: Profile", font=("arial", 28, "bold"), fg=fg_col, bg=bg_col)
    page_title.place(relx=0.4, rely=0.05, anchor=tk.CENTER)
    underline(page_title)

    change_name = tk.Button(root, text="Change username", font=("arial", 10, "bold"),
                            bg=button_col, command=lambda: clear_root() or change_name_func(user_account))
    change_name.place(relx=0.10, rely=0.05, relwidth=0.15, relheight=0.05, anchor=tk.CENTER)

    back_button = create_back_button()
    back_button.place(relx=0.70, rely=0.05, relwidth=0.15, relheight=0.05, anchor=tk.CENTER)
    back_button.config(command=lambda: clear_root() or fridge_contents(user_account))
    help_button = tk.Button(root, text="help", font=("arial", 10, "bold"),
                            bg=button_col, command=lambda: clear_root()
                            or help_func(user_account, "textFilesForSupport\\profileSupport.txt"))
    help_button.place(relx=0.75, rely=0.05, relwidth=0.08, relheight=0.05, anchor=tk.CENTER)

    username = tk.Label(root, text="Name: " + user_account.name,
                        font=("arial", 15, "bold"), fg=fg_col, bg=bg_col)
    username.place(relx=0.01, rely=0.2)

    role = tk.Label(root, text="Role: " + user_account.role,
                    font=("arial", 15, "bold"), fg=fg_col, bg=bg_col)
    role.place(relx=0.01, rely=0.3)

    restaurant = tk.Label(root, text="Restaurant: " + user_account.restaurant,
                          font=("arial", 15, "bold"), fg=fg_col, bg=bg_col)
    restaurant.place(relx=0.01, rely=0.4)


def generate_report(table):
    header = ["Item Name", "Stock", "Expiry Date", "Weight", "Allergy", "Recycling"]
    with open("report.csv", "w") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        for row in table.get_children():
            data_in_row = table.item(row)['values']
            writer.writerow(data_in_row)
            print(table.item(row)['values'])  # e.g. prints data in clicked cell


def get_safety_info(user: account_handling.Account):
    clear_root()
    page_title = tk.Label(root, text="MontyFridges: Safety report",
                          font=("arial", 28, "bold"), fg=fg_col, bg=bg_col)
    page_title.place(relx=0.385, rely=0.05, anchor=tk.CENTER)
    underline(page_title)

    back_button = create_back_button()
    back_button.config(command=lambda: clear_root() or fridge_contents(user))
    back_button.place(relx=0.855, rely=0.05, relwidth=0.10, relheight=0.05, anchor=tk.CENTER)

    table = create_table(generate_health_report, True)

    generate_report_button = tk.Button(root, text="Generate report", font=("arial", 10, "bold"),
                                       bg=button_col, command=lambda: generate_report(table))

    generate_report_button.place(relx=0.855, rely=0.115, relwidth=0.10, relheight=0.05, anchor=tk.CENTER)


def update_role(user: account_handling.Account, username: str, roles: list[str, str, str]):
    new_role: str = get_role(roles)
    user.manage_permissions(username, new_role)
    clear_root()
    change_staff_role(user)


def update_role_ui(user: account_handling.Account, table, event=None):
    cur_item = table.focus()
    row_data: dict = table.item(cur_item)
    item_values: list = row_data['values']
    username: str = item_values[0]
    old_role: str = item_values[1]

    pop_up = tk.Toplevel(root)
    pop_up.config(bg=bg_col)
    pop_up.title = "Change Role"
    pop_up.geometry("600x400")

    page_title = tk.Label(pop_up, text="MontyFridges: Change Role", font=("arial", 15, "bold"), fg=fg_col, bg=bg_col)
    page_title.place(relx=0.5, rely=0.05, anchor=tk.CENTER)
    underline(page_title)

    old_role_label = tk.Label(pop_up, text=f"Old Role: {old_role}", font=("arial", 12, "bold"), fg=fg_col, bg=bg_col)
    old_role_label.place(relx=0.1, rely=0.2)

    new_role_label = tk.Label(pop_up, text="New Role:", font=("arial", 12, "bold"), fg=fg_col, bg=bg_col)
    new_role_label.place(relx=0.1, rely=0.3)

    head_chef: bool = tk.BooleanVar()
    chef: bool = tk.BooleanVar()
    delivery_driver: bool = tk.BooleanVar()

    tk.Checkbutton(pop_up, text="Head Chef", variable=head_chef).place(relx=0.10, rely=0.45)
    tk.Checkbutton(pop_up, text="Chef", variable=chef).place(relx=0.10, rely=0.55)
    tk.Checkbutton(pop_up, text="Delivery Driver", variable=delivery_driver).place(relx=0.10, rely=0.65)

    change_role_button = tk.Button(pop_up, text="Commit Change", font=("arial", 10, "bold"),
                                   bg=button_col, command=lambda:
                                   update_role(user, username, [head_chef.get(), chef.get(), delivery_driver.get()]))

    change_role_button.place(relx=0.1, rely=0.75, relwidth=0.2, relheight=0.05)

    delete_user_button = tk.Button(pop_up, text="Delete", font=("arial", 10, "bold"),
                                   bg=button_col,
                                   command=lambda: Thread(target=remove_user, args=(username,), daemon=True).start()
                                   or table.delete(cur_item))
    delete_user_button.place(relx=0.1, rely=0.85, relwidth=0.2, relheight=0.05)


def change_staff_role(user: account_handling.Account):
    page_title = tk.Label(root, text="MontyFridges: Staff Management", font=("arial", 28, "bold"), fg=fg_col, bg=bg_col)
    page_title.place(relx=0.385, rely=0.05, anchor=tk.CENTER)
    underline(page_title)

    profile_button = tk.Button(root, text="Profile", font=("arial", 10, "bold"),
                               bg=button_col, command=lambda: clear_root() or profile_screen(user))
    profile_button.place(relx=0.175, rely=0.05, relwidth=0.15, relheight=0.05, anchor=tk.CENTER)

    back_button = create_back_button()
    back_button.place(relx=0.90, rely=0.05, relwidth=0.15, relheight=0.05, anchor=tk.CENTER)
    back_button.config(command=lambda: clear_root() or fridge_contents(user))

    help_button = tk.Button(root, text="help", font=("arial", 10, "bold"),
                            bg=button_col, command=lambda: clear_root()
                            or help_func(user, "textFilesForSupport\\staffManagementSupport.txt"))
    help_button.place(relx=0.75, rely=0.05, relwidth=0.10, relheight=0.05, anchor=tk.CENTER)

    table = create_table(display_users, False)
    user_entry = tk.Entry(root, relief=tk.GROOVE, bd=2, font=("arial", 13))
    user_entry.place(relx=0.10, rely=0.09, relwidth=0.605, relheight=0.05)

    table.bind('<ButtonRelease-1>', lambda event: update_role_ui(user, table, event))


def set_fridge_table(table) -> tuple:
    table['columns'] = [f'Col{x}' for x in range(1, 7)]
    headings: tuple = ("Item Name", "Stock", "Expiry Date", "Weight", "Allergy", "Recycling")
    return headings


def insert_fridge_table(function, table):
    for x, food_details in enumerate(function()):
        table.insert(parent='', index='end', iid=x,
                     text=x, values=[''.join(str(tuple_item)) for tuple_item in food_details[0:]])


def set_user_table(table) -> tuple:
    table['columns'] = [f'Col{x}' for x in range(1, 5)]
    headings: tuple = ("Username", "Name", "Role", "Restaurant")
    return headings


def insert_user_table(function, table):
    for x, user_details in enumerate(function()):
        table.insert(parent='', index='end', iid=x,
                     text=x, values=[''.join(str(tuple_item)) for tuple_item in user_details])


def create_table(function, fridge_table) -> ttk.Treeview:
    table = ttk.Treeview(root, height="5")
    style = ttk.Style(table)
    style.configure('TreeView', rowheight=30)
    style.theme_use('clam')

    headings = set_fridge_table(table) if fridge_table else set_user_table(table)
    table['show'] = 'headings'

    for column, heading in zip(table['columns'], headings):
        table.heading(column, text=heading)
        table.column(column, minwidth=0, width=100)
    table.place(relx=0.1, rely=0.15, relwidth=0.80, relheight=0.8)

    insert_fridge_table(function, table) if fridge_table else insert_user_table(function, table)
    if not fridge_table:
        table["displaycolumns"] = ("Col2", "Col3", "Col4")
    return table


def select_item(table, event=None):
    cur_item = table.focus()
    row_data: dict = table.item(cur_item)
    item_values: list = row_data['values']
    item_name = item_values[0]
    quantity = item_values[1]
    expiry = item_values[2]

    date = datetime.strptime(expiry, '%d %B %Y').date()
    formatted_expiry = date.strftime("%Y-%m-%d")

    Thread(target=remove_items, args=(item_name, formatted_expiry, quantity,), daemon=True).start()
    refresh_fridge_table(table)


def refresh_fridge_table(table):
    cur_item = table.focus()
    table.delete(cur_item)


def item_alert(user: account_handling.Account):
    clear_root()
    page_title = tk.Label(root, text="MontyFridges: Almost expired items",
                          font=("arial", 28, "bold"), fg=fg_col, bg=bg_col)
    page_title.place(relx=0.385, rely=0.05, anchor=tk.CENTER)
    underline(page_title)

    back_button = create_back_button()
    back_button.config(command=lambda: clear_root() or fridge_contents(user))
    back_button.place(relx=0.855, rely=0.05, relwidth=0.10, relheight=0.05, anchor=tk.CENTER)
    create_table(display_item_alerts, True)


def fridge_contents(user: account_handling.Account):
    page_title = tk.Label(root, text="MontyFridges: Fridge Contents", font=("arial", 28, "bold"), fg=fg_col, bg=bg_col)
    page_title.place(relx=0.385, rely=0.05, anchor=tk.CENTER)
    underline(page_title)

    profile_button = tk.Button(root, text="Profile", font=("arial", 10, "bold"),
                               bg=button_col, command=lambda: clear_root() or profile_screen(user))
    profile_button.place(relx=0.136, rely=0.05, relwidth=0.0725, relheight=0.05, anchor=tk.CENTER)

    home_button = tk.Button(root, text="Home", font=("arial", 10, "bold"),
                            bg=button_col, command=lambda: clear_root() or main_screen())
    home_button.place(relx=0.60, rely=0.05, relwidth=0.15, relheight=0.05, anchor=tk.CENTER)

    help_button = tk.Button(root, text="help", font=("arial", 10, "bold"),
                            bg=button_col, command=lambda: clear_root() or help_func(user, "textFilesForSupport\\fridgeContentsSupport.txt"))
    help_button.place(relx=0.75, rely=0.05, relwidth=0.08, relheight=0.05, anchor=tk.CENTER)

    search_button = tk.Button(root, text="Search", font=("arial", 10, "bold"),
                              bg=button_col, command=lambda: clear_root() or help_func(user, "textFilesForSupport\\fridgeContentsSupport.txt"))
    search_button.place(relx=0.75, rely=0.115, relwidth=0.08, relheight=0.05, anchor=tk.CENTER)

    safety_report = tk.Button(root, text="safety", font=("arial", 10, "bold"),
                              bg=button_col, command=lambda: clear_root() or get_safety_info(user))
    safety_report.place(relx=0.855, rely=0.05, relwidth=0.10, relheight=0.05, anchor=tk.CENTER)

    fridge_entry = tk.Entry(root, relief=tk.GROOVE, bd=2, font=("arial", 13))
    fridge_entry.place(relx=0.10, rely=0.09, relwidth=0.605, relheight=0.05)

    table = create_table(display_fridge_contents, True)
    table.bind('<Delete>', lambda event: select_item(table, event))

    scroll_bar_y = tk.Scrollbar(root, command=table.yview)
    scroll_bar_y.place(relx=0.9, rely=0.15, relheight=0.8)

    scroll_bar_x = tk.Scrollbar(root, command=table.xview, orient='horizontal')
    scroll_bar_x.place(relx=0.1, rely=0.95, relwidth=0.8)

    if user.role == "Head Chef":

        item_alert_button = tk.Button(root, text="Item alert", font=("arial", 10, "bold"),
                                      bg=button_col, command=lambda: item_alert(user))
        item_alert_button.place(relx=0.23, rely=0.05, relwidth=0.0725, relheight=0.05, anchor=tk.CENTER)

        staff_management_button = tk.Button(root, text="Staff management", font=("arial", 10, "bold"),
                                            bg=button_col, command=lambda: clear_root() or change_staff_role(user))
        staff_management_button.place(relx=0.855, rely=0.115, relwidth=0.10, relheight=0.05, anchor=tk.CENTER)


def login_screen():
    login_title = tk.Label(root, text="MontyFridges: login", font=("arial", 28, "bold"), fg=fg_col, bg=bg_col)
    login_title.place(relx=0.50, rely=0.05, anchor=tk.CENTER)
    underline(login_title)

    back_button = create_back_button()
    back_button.config(command=lambda: clear_root() or main_screen())

    username_label = tk.Label(root, text="Username:", font=("arial", 15, "bold"), fg=fg_col, bg=bg_col)
    username_label.place(relx=0.20, rely=0.35)
    password_label = tk.Label(root, text="Password:", font=("arial", 15, "bold"), fg=fg_col, bg=bg_col)
    password_label.place(relx=0.20, rely=0.45)

    username_entry = tk.Entry(root, relief=tk.GROOVE, bd=2, font=("arial", 13))
    username_entry.place(relx=0.30, rely=0.35, relwidth=0.5, relheight=0.05)
    password_entry = tk.Entry(root, relief=tk.GROOVE, bd=2, font=("arial", 13), show="*")
    password_entry.place(relx=0.30, rely=0.45, relwidth=0.5, relheight=0.05)

    login_submission = tk.Button(root, text="login", font=("arial", 10, "bold"),
                                 bg=button_col, command=lambda:
                                 login_account(username_entry.get(), password_entry.get()))
    login_submission.place(relx=0.20, rely=0.65, relwidth=0.28, relheight=0.1)


def signup_screen():
    signup_title = tk.Label(root, text="MontyFridges: signup", font=("arial", 28, "bold"), fg=fg_col, bg=bg_col)
    signup_title.place(relx=0.5, rely=0.05, anchor=tk.CENTER)
    underline(signup_title)

    back_button = create_back_button()
    back_button.config(command=lambda: clear_root() or main_screen())

    username_label = tk.Label(root, text="Username:", font=("arial", 15, "bold"), fg=fg_col, bg=bg_col)
    username_label.place(relx=0.05, rely=0.25)
    signup_username_entry = tk.Entry(root, relief=tk.GROOVE, bd=2, font=("arial", 13))
    signup_username_entry.place(relx=0.20, rely=0.25, relwidth=0.2, relheight=0.05)

    password_label = tk.Label(root, text="Password:", font=("arial", 15, "bold"), fg=fg_col, bg=bg_col)
    password_label.place(relx=0.05, rely=0.35)
    signup_password_entry = tk.Entry(root, relief=tk.GROOVE, bd=2, font=("arial", 13), show="*")
    signup_password_entry.place(relx=0.20, rely=0.35, relwidth=0.2, relheight=0.05)

    name_label = tk.Label(root, text="Name:", font=("arial", 15, "bold"), fg=fg_col, bg=bg_col)
    name_label.place(relx=0.05, rely=0.45)
    name_entry = tk.Entry(root, relief=tk.GROOVE, bd=2, font=("arial", 13))
    name_entry.place(relx=0.20, rely=0.45, relwidth=0.2, relheight=0.05)

    role_label = tk.Label(root, text="Role:", font=("arial", 15, "bold"), fg=fg_col, bg=bg_col)
    role_label.place(relx=0.05, rely=0.55)

    head_chef: bool = tk.BooleanVar()
    chef: bool = tk.BooleanVar()

    tk.Checkbutton(root, text="Head Chef", font=("arial", 13), variable=head_chef).place(relx=0.20, rely=0.55, relwidth=0.08)
    tk.Checkbutton(root, text="Chef", font=("arial", 13), variable=chef).place(relx=0.32, rely=0.55, relwidth=0.08)

    restaurant_label = tk.Label(root, text="Restaurant:", font=("arial", 15, "bold"), fg=fg_col, bg=bg_col)
    restaurant_label.place(relx=0.05, rely=0.65)
    restaurant_entry = tk.Entry(root, relief=tk.GROOVE, bd=2, font=("arial", 13))
    restaurant_entry.place(relx=0.20, rely=0.65, relwidth=0.2, relheight=0.05)

    help_button = tk.Button(root, text="help", font=("arial", 10, "bold"),
                            bg=button_col, command=lambda: clear_root()
                            or help_func("steve", "textFilesForSupport\\fridgeContentsSupport.txt"))
    help_button.place(relx=0.75, rely=0.05, relwidth=0.08, relheight=0.05, anchor=tk.CENTER)

    submit_details = tk.Button(root, text="signup", font=("arial", 10, "bold"),
                               bg=button_col, command=lambda:
                               create_account(signup_username_entry.get(), signup_password_entry.get(),
                                              name_entry.get(), restaurant_entry.get(),
                                              [head_chef.get(), chef.get()]))
    submit_details.place(relx=0.20, rely=0.75, relwidth=0.2, relheight=0.05)


def main_screen():
    welcoming = tk.Label(root, text="MontyFridges", font=("arial", 28, "bold"), fg=fg_col, bg=bg_col)
    welcoming.place(relx=0.5, rely=0.05, anchor=tk.CENTER)
    underline(welcoming)

    login_button = tk.Button(root, text="login", font=("arial", 10, "bold"),
                             bg=button_col, command=lambda: clear_root() or login_screen())
    login_button.place(relx=0.25, rely=0.35, relwidth=0.2, relheight=0.1)

    signup_button = tk.Button(root, text="signup", font=("arial", 10, "bold"),
                              bg=button_col, command=lambda: clear_root() or signup_screen())
    signup_button.place(relx=0.55, rely=0.35, relwidth=0.2, relheight=0.1)

    colors = tk.Button(root, text="Background Color", font=("arial", 10, "bold"),
                       bg=button_col, command=change_background)
    colors.place(relx=0.75, rely=0.05, relwidth=0.1, relheight=0.05, anchor=tk.CENTER)

    colors = tk.Button(root, text="Foreground Color", font=("arial", 10, "bold"),
                       bg=button_col, command=change_foreground)
    colors.place(relx=0.90, rely=0.05, relwidth=0.1, relheight=0.05, anchor=tk.CENTER)


if __name__ == "__main__":
    main_screen()
    root.mainloop()
