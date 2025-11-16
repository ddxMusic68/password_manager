from cryptography.fernet import Fernet
import tkinter as tk
import json as js
import sys, os


# tkinter initialization
window = tk.Tk()
window.geometry("500x500")
window.title("Password Manager")


# cryptography funcs
def encrypt_message(message, key):
    encoded_message = message.encode() #turns message into bytes
    f = Fernet(key)
    encrypted_message = f.encrypt(encoded_message)
    return encrypted_message

def decrypt_message(encrypted_message, key):
    f = Fernet(key)
    decrypt_message = f.decrypt(encrypted_message)
    return decrypt_message.decode() #from bytes to string


# initialising json server
def resource_path(filename):
    if getattr(sys, 'frozen', False):  # if running as .exe
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = sys.path[0]
    return os.path.join(base_path, filename)

path = resource_path("encrypted_passwords.json")

if not os.path.exists(path):
    with open(path, "w") as f:
        f.write("{}") 


# tkinter funcs and variables
addpassword = tk.StringVar()
addapplication = tk.StringVar()
key_var = tk.StringVar()
password_shown = False

def get_text():
    password = addpassword.get()
    application = addapplication.get()
    key = key_var.get() #return bytes of key
    password = encrypt_message(password, key.encode()).decode()

    addapplication.set("")
    addpassword.set("")
    with open(path, "r+") as file:
        data = js.loads(file.read())
        data[f"{application}"] = f"{password}"
        file.seek(0) #so it will be truncated
        file.write(js.dumps(data))
    update_list()

def update_list():
    with open(path, "r") as file:
        data = file.read()
        data = js.loads(data)
        data = list(data)
        password_list.delete(0, tk.END) # clears data
        for app in data:
            password_list.insert(tk.END, app)

def func_show_password():
    global password_shown
    if password_shown:
        add_key.config(show="*")
        addpassword_input.config(show="*")
        password_shown = False
    else:
        add_key.config(show="")
        addpassword_input.config(show="")
        password_shown = True

def func_delete():
    selected = password_list.curselection()
    with open(path, "r+") as file:
        data = js.loads(file.read())
        data_list = list(data)
        data.pop(data_list[selected[0]])
        file.seek(0)
        file.truncate() # deletes json for new data
        file.write(js.dumps(data))
    update_list()

def func_copy_password():
    selected = password_list.curselection()
    key = key_var.get().encode()
    with open(path, "r+") as file:
        data = js.loads(file.read())
        data_list = list(data)
        encoded_password = data[data_list[selected[0]]].encode()
        password = decrypt_message(encoded_password, key)
        window.clipboard_clear()
        window.clipboard_append(password)


# tkinter gui
password_list = tk.Listbox(window) # list of application 
password_list.pack(side="left", fill="both", expand=True)
update_list() #updates list at the start

scrollbar = tk.Scrollbar(password_list) # scrollbar for list of applications
scrollbar.pack(side="right", fill="y")

password_list.config(yscrollcommand=scrollbar.set) # maps "scrollbar" to "password_list"
scrollbar.config(command=password_list.yview)

addapplication_label = tk.Label(window, text="application:") # input & label for applications
addapplication_label.pack()
addapplication_input = tk.Entry(window, textvariable=addapplication)
addapplication_input.pack()

addpassword_label = tk.Label(window, text="password:") # input & label for passwords
addpassword_label.pack()
addpassword_input = tk.Entry(window, textvariable=addpassword, show="*")
addpassword_input.pack()

key_label = tk.Label(window, text="key:") # cryptography key for Fernet
key_label.pack()
add_key = tk.Entry(window, textvariable=key_var, show="*")
add_key.pack()

submit_button = tk.Button(window, text="submit", command=get_text) # submits aplication and encrypts passwords to json file
submit_button.pack()

show_password = tk.Button(window, text="show passwords", command=func_show_password) # shows / covers passwords
show_password.pack()

delete = tk.Button(window, text="delete", command=func_delete)
delete.pack()

copy_password = tk.Button(window, text="copy password", command=func_copy_password)
copy_password.pack()


# tkinter mainloop
window.update()
window.mainloop()
