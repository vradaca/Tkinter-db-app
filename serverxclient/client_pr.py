import tkinter as tk
from tkinter import StringVar
from tkinter import Menu
from tkinter import filedialog
from tkinter import ttk
from tkinter import Frame
from tkinter import messagebox
import socket
import threading
import time
from datetime import datetime
import sqlite3
from functools import reduce
import json

btn_list = []

class User: 
    def __init__(self, permission, username, password):
        self.permission = permission
        self.username = username
        self.password = password

def login():
    username = username_entry.get()
    password = password_entry.get()
    permission = permission_var.get()

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    server_host = socket.gethostname()
    server_port = 12345
    client_socket.connect((server_host, server_port))

    authentication_data = permission + ',' + username + ',' + password
    client_socket.send(authentication_data.encode())

    authentication_result = client_socket.recv(1024).decode()
    json_log = client_socket.recv(1024).decode('utf-8')

    if authentication_result == "True":
        user = User(permission, username, password)
        show_dashboard(user, json_log)
    else:
        messagebox.showerror("Auth Failed!", "Username or password are incorrect, please try again")

    # Close the client socket
    client_socket.close()

def show_dashboard(user, json_log):
    root.destroy()

    dashboard = tk.Tk()
    dashboard.title("Dashboard")
    dashboard.geometry("500x200")

    menubar = Menu(dashboard)
    filemenu = Menu(menubar ,tearoff=0)
    menubar.add_cascade(label = "Import DB", menu = filemenu)
    filemenu.add_command(label = "Import", command = lambda: importdb(dashboard, user))

    dashboard.config(menu = menubar)

    date_label = tk.Label(dashboard, text = "Date: " + datetime.now().strftime("%d.%m.%Y."))
    date_label.pack()

    time_label = tk.Label(dashboard, text = "Time: ")
    time_label.pack()

    welcome_label = tk.Label(dashboard, text="Welcome: " + user.username, font ='18')
    welcome_label.pack()

    log_button = tk.Button(dashboard, text = "Show last logged entry", command = lambda: show_last_log(dashboard, json_log))
    log_button.pack()

    stop_update = threading.Event()
    update_thread = threading.Thread(target = update_time, args = (time_label, stop_update))
    update_thread.start()

    def close_page():
        stop_update.set()
        update_thread.join()
        dashboard.destroy()
        

    dashboard.protocol("WM_DELETE_WINDOW", close_page)
    dashboard.mainloop()

def update_time(time_label, stop_update):
    while not stop_update.is_set():
        time_rn = time.strftime("%H:%M:%S")
        time_label.config(text= "Time: " +  time_rn)
        time.sleep(1)

def show_last_log(dash, json_log):

    frame = tk.Frame(dash)
    frame.pack()

    for key, value in json.loads(json_log).items():
        label = tk.Label(frame, text=f"{key}: {value}")
        label.pack()

    close_log_btn = tk.Button(frame, text = "Close log", command = (lambda: frame.destroy()))
    close_log_btn.pack()

def importdb(dash, user):

    if btn_list: 
        for btn in btn_list:
            btn.destroy()

    file_path = filedialog.askopenfilename(filetypes=[("Database Files", "*.db")])
    db = sqlite3.connect(file_path)
    cursor = db.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()

    if tables.__len__() <= 1:
        btn_list.append(tk.Button(dash, text = tables[0], command = lambda: view_table(tables[0], db, user)))
        btn_list[-1].pack(side='left', padx = 10)
    else:
        for x in tables:
            btn_list.append(tk.Button(dash, text = x, command = lambda name = x : view_table(name, db, user)))
            btn_list[-1].pack(side='left', padx = 10)


def view_table(name, datbas, user):

    curs = datbas.cursor()
    entries = []

    tree_viewer = tk.Tk()
    tree_viewer.title("Database Viewer") 
    tree_viewer.geometry("1010x400")

    curs.execute("SELECT * FROM " + name[0])
    recs = curs.fetchall()

    treeview = ttk.Treeview(tree_viewer)
    treeview["columns"] = tuple(range(len(recs[0])))

    for i, head in enumerate(curs.description):
        treeview.heading(i, text = head[0])
        entries.append(head[0])

    for rec in recs:
        treeview.insert("", "end", values=rec)

    insert_btn = tk.Button(tree_viewer, text = "Insert a record", command = lambda: insert_value(name[0], tree_viewer, treeview, datbas, entries, insert_btn))
    delete_btn = tk.Button(tree_viewer, text = "Delete a record", command = lambda: delete_value(name[0], treeview, datbas))
    change_btn = tk.Button(tree_viewer, text = "Change a record", command = lambda: change_value(name[0], tree_viewer,  treeview, datbas, entries, change_btn))
    view_items_btn = tk.Button(tree_viewer, text = "View the number of all available items", command = lambda: view_all_items(name[0], datbas, entries))
    filter_lbl = tk.Label(tree_viewer, text = "Filter by price: ")
    filter_txt = tk.Entry(tree_viewer)
    filter_btn = tk.Button(tree_viewer, text = "Filter", command = lambda: filter_price(tree_viewer, treeview, filter_txt.get(), entries))

    if user.permission == 'Spectator':
        insert_btn['state'] = tk.DISABLED
        delete_btn['state'] = tk.DISABLED
        change_btn['state'] = tk.DISABLED

    treeview.pack(anchor='w')
    insert_btn.pack(side='left')
    delete_btn.pack(side='left')
    change_btn.pack(side='left')
    view_items_btn.pack(side='left')
    filter_lbl.pack(side='left')
    filter_txt.pack(side='left')
    filter_btn.pack(side='left')
    tree_viewer.mainloop()

def insert_value(table_name, win, tree, datbas, header, insrt):

    insrt['state'] = tk.DISABLED
    curs = datbas.cursor()
    last_member = tree.item(tree.get_children()[-1])['values'][0]

    frame = Frame(win) # figure out duplicate frame creation issue
    frame.pack()

    entries_txt = []
    values_entries = []

    for x in header:
        entries_txt.append(tk.Entry(frame, name="txt" + x[0]))

    add_val_btn = tk.Button(frame, text="Add", command = lambda :confirm_add(insrt))
    cancel_btn = tk.Button(frame, text="Cancel", command = lambda: cancel_add(insrt))

    entries_txt.pop(0)

    for i, y in enumerate(entries_txt): #if it works it aint broken!!!!!!!
        i += 1
        tk.Label(frame, text = header[i] + ':').pack()
        y.pack()
        i -= 1
                

    add_val_btn.pack()
    cancel_btn.pack()

    def confirm_add(ins):

        sql = ''' INSERT INTO '''+ table_name + '''(''' + ','.join(map(str,header)) + ''')
            VALUES (?, ?, ?, ?)''' 
        
        for y in entries_txt: 
            values_entries.append(y.get())

        values_entries.insert(0, (last_member + 1)) 

        tree.insert("", 'end', values = values_entries)
        curs.execute(sql, values_entries)

        values_entries.clear()
        for x in entries_txt:
            x.delete(0, 'end')
            
        datbas.commit()
        ins['state'] = tk.NORMAL
        frame.destroy()
     
    def cancel_add(ins):
        ins['state'] = tk.NORMAL
        frame.destroy()

def delete_value(table_name, tree, datbas):

    curs = datbas.cursor()
    id_table = tree.heading(0)['text']

    if tree.selection():

        del_member = tree.item(tree.selection())['values']
        tree.delete(tree.selection())

        sql = '''DELETE FROM '''+ table_name + ''' WHERE ''' +id_table+ ''' = ''' +str(del_member[0])

        curs.execute(sql)
        datbas.commit()

    else:

        messagebox.showerror("Select item!", "Please select an item, before you delete")

def change_value(table_name, win, tree, datbas, header, change):

    change['state'] = tk.DISABLED
    curs = datbas.cursor()

    if tree.focus():
        frame_ch = Frame(win)
        frame_ch.pack()

        entries_txt_ch = []
        values_entries_ch = []
        header_change = []

        for x in header:
            entries_txt_ch.append(tk.Entry(frame_ch, name="txt" + x[0]))

        change_val_btn = tk.Button(frame_ch, text="Change Values", command = lambda :confirm_change(change))
        cancel_btn = tk.Button(frame_ch, text="Cancel", command = lambda: cancel_change(change))

        entries_txt_ch.pop(0)

        for i, y in enumerate(entries_txt_ch):
            i+=1
            tk.Label(frame_ch, text=header[i] + ':').pack()
            y.pack()
            i-=1

        change_val_btn.pack()
        cancel_btn.pack()

    else:
        messagebox.showerror("Select item!", "Please select an item, before you change value!")

    def confirm_change(chg):
        for i, y in enumerate(entries_txt_ch): 
            if y.get():
                values_entries_ch.append(y.get())
                header_change.append(header[i+1])
            
        for i, x in enumerate(header_change):
            tree.set(tree.focus(), column = (header.index(x)) , value = values_entries_ch[i])

        for j, x in enumerate(header_change):
            sql = ''' UPDATE ''' + table_name + ''' SET ''' + x + ''' = \'''' + values_entries_ch[j] +'''\' WHERE ''' + header[0] + ''' = ''' + str(tree.item(tree.focus())['values'][0]) + ''''''
            curs.execute(sql)

        values_entries_ch.clear()

        for x in entries_txt_ch:
            if x.get():
                x.delete(0, 'end')
        
        datbas.commit()
        chg['state'] = tk.NORMAL
        frame_ch.destroy()

    def cancel_change(chg):
        chg['state'] = tk.NORMAL
        frame_ch.destroy()
        
def view_all_items(table_name, db, header):
    
    curs = db.cursor()
    quants = []

    for x in header: 
        if x == 'quantity':
            sql = '''SELECT ''' + x + ''' FROM ''' + table_name + ''''''
            curs.execute(sql)
            quants_tuple = curs.fetchall()
    
    for tup in quants_tuple:
        quants.append(tup[0])

    sum = reduce((lambda x,y: x + y), list(map(int, quants)))

    messagebox.showinfo("Available items", f"The number of available items is:  {sum}" )    

def filter_price(win, tree, condition, header):

    original_ids = tree.get_children()
    original_items = []

    frame = tk.Frame(win)
    frame.pack(side="left")

    for id in original_ids:
        original_items.append(tree.item(id)['values'])
    
    for i, x in enumerate(header):
        if x == 'price':
            filtered_items = list(filter((lambda vals: float(vals[i]) > float(condition)), original_items))

    tree.delete(*tree.get_children())

    for filtered in filtered_items:
        tree.insert("", "end", values=filtered)

    cancel_filter_btn = tk.Button(frame, text = "Cancel", command= lambda: cancel_filter())
    cancel_filter_btn.pack(side="left")

    def cancel_filter():

        tree.delete(*tree.get_children())

        for original in original_items:

            tree.insert("", "end", values=original)

        frame.destroy()

# Create the login window
root = tk.Tk()
root.title("Login Form")
root.geometry("500x220")

instruction_label = tk.Label(root, text="Please enter your login credentials.", font='18')
instruction_label.pack()

username_label = tk.Label(root, text="Username:")
username_label.pack()

username_entry = tk.Entry(root)
username_entry.pack()

password_label = tk.Label(root, text="Password:")
password_label.pack()

password_entry = tk.Entry(root, show="*")
password_entry.pack()

permission_label = tk.Label(root, text = "Please select your permission level: ")
permission_label.pack()
permission_var = StringVar(root, "Admin")
admin_entry = tk.Radiobutton(root, variable = permission_var, text = "Admin", value = "Admin")
buyer_entry = tk.Radiobutton(root, variable = permission_var, text = "Spectator", value="Spectator")

admin_entry.pack()
buyer_entry.pack()

login_button = tk.Button(root, text = "Login", command = login)
login_button.pack()

root.mainloop()