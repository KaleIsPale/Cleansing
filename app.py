import os

import ttkbootstrap as ttk
from ttkbootstrap.dialogs.dialogs import Messagebox
from ttkbootstrap import Window
from ttkbootstrap.constants import *

from mailProcessing import main


class App(Window):
    def __init__(self, title="Cleansing - Spam Filter for GMail", themename="darkly", iconphoto='', size=[854,512], position=None, minsize=None, maxsize=None, resizable=None, hdpi=True, scaling=None, transient=None, overrideredirect=False, alpha=1):
        super().__init__(title, themename, iconphoto, size, position, minsize, maxsize, resizable, hdpi, scaling, transient, overrideredirect, alpha)
        self.authorized = os.path.exists('token.json')
        self.num_spam = 0
        self.num_ham = 0
        self.progressVar = ttk.DoubleVar()
        self.progressVar.set(0.0)

        self.addresses = ttk.StringVar()
        with open('verified_addresses.txt', 'r') as wb:
           self.addresses.set(wb.read())

        self.status = ttk.StringVar()
        self.status.set(f"""

        Status: {'Authorized' if self.authorized else 'Un-authorized'}
        Spam Mails: {self.num_spam}
        Ham Mails : {self.num_ham}
        """)

        self.build()


    def check_auth(self):
        if self.authorized:
            messageBox = Messagebox()
            messageBox.ok('Already Authorized!', title='')
    

    def build(self):
        self.buttonFrame = ttk.Frame(self)
        self.buttonFrame.pack(side=TOP)
        self.authorizationButton = ttk.Button(self.buttonFrame, text="Authorize", bootstyle='primary', command=self.check_auth).pack(padx=5, pady=(20, 5), side=LEFT)
        self.emptySpamButton = ttk.Button(self.buttonFrame, text="Clear all spam mails", bootstyle='primary').pack(padx=5, pady=(20, 5), side=LEFT)
        self.checkInboxButton = ttk.Button(self.buttonFrame, text="Check the entire Inbox for spam mails", bootstyle='primary', command=lambda: main(process=True, progressVar=self.progressVar, progressBar=self.progressBar)).pack(padx=5, pady=(20, 5), side=LEFT)
#main(process=True, progressVar=self.progressVar, progressBar=self.progressBar)
        self.notebook = ttk.Notebook(bootstyle='dark')
        self.notebook.pack(expand=1, fill=BOTH,padx=10, pady=(5, 30), side=BOTTOM)

        self.statusTab = ttk.Frame(self.notebook)
        self.notebook.add(self.statusTab, text="Stats")
        self.infoLabel = ttk.Label(self.statusTab, text=self.status.get(), font=('Roboto 15 normal'))
        self.infoLabel.pack()
        self.progressBar = ttk.Floodgauge(self.statusTab, value=self.progressVar.get(), length=350, mask='{}%')
        # self.progressBar.pack_forget()

        self.addressTab = ttk.Frame(self.notebook)
        self.notebook.add(self.addressTab, text="Verified Adresses")
        self.addressesLabel = ttk.Label(self.addressTab, text=self.addresses.get(), font=('Roboto 15 normal'))
        self.addressesLabel.pack()

app = App()
# ttk.Label(tab2, text= "This is a New Tab Context", font=('Helvetica 20 bold')).pack()
app.mainloop()