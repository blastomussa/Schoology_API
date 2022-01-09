# Author: Blastomussa
# Date 1/8/22
# tk app that allows for manual creation of parent accounts and manual
# association to student accounts
import tkinter as tk
from Pylogy import *

API_KEY = '###########'
SECRET = '#############'

class MainApplication(tk.Frame):
    def __init__(self, master):
        self.master = master
        tk.Frame.__init__(self, self.master)
        self.configure_gui()
        self.create_widgets()
        self.schoology_init()

    def schoology_init(self):
        self.pylogy = Pylogy(API_KEY,SECRET)

    def configure_gui(self):
            self.master.title("Schoology API App")
            self.master.geometry("500x500")
            self.master.resizable(False, False)

    def create_widgets(self):
        # Entry Variables
        self.fname = tk.StringVar()
        self.lname = tk.StringVar()
        self.email = tk.StringVar()
        self.p_email = tk.StringVar()
        self.s_email = tk.StringVar()
        # Parent first, last and email entry fields and labels
        fname_label = tk.Label(self.master, text="First Name").grid(row=0,column=0)
        fname_entry = tk.Entry(self.master).grid(row=0,column=1)
        lname_label = tk.Label(self.master, text="Last Name").grid(row=1,column=0)
        lname_entry = tk.Entry(self.master).grid(row=1,column=1)
        email_label = tk.Label(self.master, text="Email").grid(row=2,column=0)
        email_entry = tk.Entry(self.master,textvariable=self.email).grid(row=2,column=1)
        # create parent button
        button1 = tk.Button(text='Create Parent', command=self.button1_click).grid(row=3,column=0)
        # NEED label with success or failure message

        # Student and parent email entry fields and labels
        semail_label = tk.Label(self.master, text="Student Email").grid(row=5,column=0)
        semail_entry = tk.Entry(self.master).grid(row=5,column=1)
        pemail_label = tk.Label(self.master, text="Parent Email").grid(row=6,column=0)
        pemail_entry = tk.Entry(self.master,textvariable=self.p_email).grid(row=6,column=1)
        # create parent association button
        button2 = tk.Button(text='Create Association', command=self.button2_click).grid(row=7,column=0)
        # NEED label with success or failure message


    def button1_click(self):
        fname = self.fname.get()
        lname = self.lname.get()
        email = self.email.get()
        response = self.pylogy.create_parent(fname,lname,email)
        if(response.status_code==200):
            pass # success message
        else:
            pass # error message

    def button2_click(self):
        print(self.p_email.get())

    # methods that take user input,calls schoology api and displays messages

if __name__ == '__main__':
   root = tk.Tk()
   main_app =  MainApplication(root)
   root.mainloop()
