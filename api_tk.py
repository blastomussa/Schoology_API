# tk app that allows for manual creation of parent accounts and manual
# association to student accounts
import configparser
import tkinter as tk
from Pylogy import *
from time import sleep

# Get API key and secret from config file
try:
    config = configparser.ConfigParser()
    config.read('config.ini')
    API_KEY = config['SCHOOLOGY_CLIENT']['API_KEY']
    SECRET = config['SCHOOLOGY_CLIENT']['SECRET']
except configparser.Error:
    print("Configuration Error...config.ini not found")
    exit()
except KeyError:
    print("Configuration Error...config not found")
    exit()


class MainApplication(tk.Frame):
    def __init__(self, master):
        self.master = master
        tk.Frame.__init__(self, self.master)
        self.configure_gui()
        self.create_widgets()
        self.schoology_init()

    def schoology_init(self):
        self.pylogy = Pylogy(API_KEY,SECRET)
        # arbitrary get call to check status code to determine API status
        try:
            self.pylogy.view_user(1)
            self.api_status.set('API Status: Connected')
            self.retry_connection.grid_remove()
        except requests.exceptions.ConnectionError:
            self.api_status.set('API Status: Check Network Connection...')
            self.retry_connection.grid(row=0,column=1,sticky='w')


    def configure_gui(self):
            self.master.title("Schoology API App")
            self.master.grid_columnconfigure(0, weight=1)

    # REFINE
    def create_widgets(self):
        # Entry Variables
        self.fname = tk.StringVar()
        self.lname = tk.StringVar()
        self.email = tk.StringVar()
        self.p_email = tk.StringVar()
        self.s_email = tk.StringVar()
        self.status1 = tk.StringVar()
        self.status2 = tk.StringVar()
        self.api_status = tk.StringVar()

        frame0 = tk.Frame(self.master)
        frame0.grid(row=0,sticky='we')
        frame1 = tk.Frame(self.master,relief='groove',bd=1)
        frame1.grid(row=1,sticky='we')
        frame1.grid_columnconfigure(0, weight=1)
        frame2 = tk.Frame(self.master,relief='groove',bd=1)
        frame2.grid(row=2,sticky='we')
        frame2.grid_columnconfigure(0, weight=1)
        frame3 = tk.Frame(self.master)
        frame3.grid(row=3,sticky='we')
        frame3.grid_columnconfigure(0, weight=1)

        tk.Label(frame0, text="Create Parent Accounts and Associations", font='-weight bold').grid(row=0,columnspan=2)

        # Parent first, last and email entry fields and labels
        tk.Label(frame1, text="First Name: ").grid(row=0,column=0,sticky='e')
        tk.Entry(frame1, textvariable=self.fname).grid(row=0,column=1)
        tk.Label(frame1, text="Last Name: ").grid(row=1,column=0,sticky='e')
        tk.Entry(frame1, textvariable=self.lname).grid(row=1,column=1)
        tk.Label(frame1, text="Email: ").grid(row=2,column=0,sticky='e')
        tk.Entry(frame1, textvariable=self.email).grid(row=2,column=1)
        # create parent button
        tk.Button(frame1,text='Create Parent', command=self.button1_click).grid(row=3,columnspan=2)
        # create status label
        tk.Label(frame1, textvariable=self.status1).grid(row=4,columnspan=2)
        # NEED label with success or failure message

        # Student and parent email entry fields and labels
        tk.Label(frame2, text="Student Email: ").grid(row=5,column=0,sticky='e')
        tk.Entry(frame2, textvariable=self.s_email).grid(row=5,column=1)
        tk.Label(frame2, text="Parent Email: ").grid(row=6,column=0,sticky='e')
        tk.Entry(frame2, textvariable=self.p_email).grid(row=6,column=1)
        # create parent association button
        tk.Button(frame2,text='Create Association', command=self.button2_click).grid(row=7,column=0,sticky='ew')
        tk.Button(frame2,text='Delete Association', command=self.button3_click).grid(row=7,column=1,sticky='ew')
        self.status2_label = tk.Label(frame2, textvariable=self.status2)
        self.status2_label.grid(row=8,columnspan=2)
        # API status label
        tk.Label(frame3, textvariable=self.api_status, font='-size 10').grid(row=0,sticky='w')
        self.retry_connection = tk.Button(frame3, text='Retry', font='-size 10', command=self.schoology_init)


    # REFINE
    def button1_click(self):
        fname = str(self.fname.get())
        lname = str(self.lname.get())
        email = str(self.email.get())
        self.fname.set('')
        self.lname.set('')
        self.email.set('')
        response = self.pylogy.create_parent(fname,lname,email)
        if(response.status_code==201):
            self.status1.set("Successfully created: {0}".format(email))
        else:
            self.status1.set(response.json())

    # REFINE; takes too long
    def button2_click(self):
        s_email = str(self.s_email.get())
        p_email = str(self.p_email.get())
        #force label to update before function has complete
        self.status2.set("Loading...this may take a minute.")
        self.status2_label.update_idletasks()

        # how do i run this in background; subprocess?
        # 2x quicker than sequential search
        try: self.hashtable
        except NameError: self.hashtable = None

        if (not self.hashtable):
            self.hashtable = self.build_hashtable(self.pylogy.list_users())
            s_suid = hashtable[s_email]['school_uid']
            p_suid = hashtable[p_email]['school_uid']


        response = self.pylogy.create_association(s_id,p_id)
        if(response.status_code>=200 and response.status_code<300):
            self.status2.set("Created association for: {}".format(s_email))
        else:
            try:
                x = response.json()
                y = x['association'][0]
                self.status2.set(y['message'])
            except KeyError:
                self.status2.set('{} Error'.format(response.status_code))
        self.s_email.set('')
        self.p_email.set('')

    # REFINE; takes too long
    def button3_click(self):
        s_email = str(self.s_email.get())
        p_email = str(self.p_email.get())
        #force label to update before function has complete
        #NOT WORKING WITH HASHTABLE
        self.status2.set("Loading...this may take a minute.")
        self.status2_label.update_idletasks()

        # how do i run this in background; subprocess?
        # 2x quicker than sequential search
        try: self.hashtable
        except NameError: self.hashtable = None

        if (not self.hashtable):
            self.hashtable = self.build_hashtable(self.pylogy.list_users())
            s_suid = hashtable[s_email]['school_uid']
            p_suid = hashtable[p_email]['school_uid']


        #s_id = self.pylogy.get_school_uid(s_email)
        #p_id = self.pylogy.get_school_uid(p_email)
        response = self.pylogy.delete_association(s_suid,p_suid)
        if(response.status_code>=200 and response.status_code<300):
            self.status2.set("Successfully deleted parent association")
        else:
            try:
                x = response.json()
                y = x['association'][0]
                self.status2.set(y['message'])
            except KeyError:
                self.status2.set('{} Error'.format(response.status_code))
        self.s_email.set('')
        self.p_email.set('')


    def build_hashtable(self,users):
        hashtable = {}
        for u in users:
            val = {
                'email': u['primary_email'],
                'id': u['uid'],
                'school_uid': u['school_uid']
            }
            hashtable[u['primary_email']] = val
        return hashtable



if __name__ == '__main__':
   root = tk.Tk()
   main_app =  MainApplication(root)
   root.mainloop()
