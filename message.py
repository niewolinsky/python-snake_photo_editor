from tkinter import messagebox
from tkinter import Tk 

## FUNCTION DECLARED TO SHOW ERROR MESSAGES TO USER ##
## CREATED IN NEW FILE FOR PROBABLY MORE OPTIONS INCOMING ##
def message_window(text1, text2):
    Tk().withdraw()
    messagebox.showinfo(text1, text2)