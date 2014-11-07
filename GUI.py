__author__ = 'Thomas'
# The module that defines all GUI programming and options
import Tkinter
# Creates file dialogs
import tkFileDialog
# Creates standard OK dialogs
import tkMessageBox
from Settings import *
from Communicator import *
# for printing stacktrace of error message
from traceback import print_exc

class GUI(Tkinter.Tk):

    def __init__(self, parent):
        print '[+] Building GUI environment...'
        # Inherit from Tkinter's parent class
        Tkinter.Tk.__init__(self, parent)
        self.parent = parent
        self.settings = Settings()
        self.comm = Communicator()
        # helper class for creating widgets
        # send self as desired frame to store widgets into
        self.widgets = Widgets(frame=self)
        # Create the GUI application
        # Initialize label references
        self.TitleLabel = Tkinter.StringVar()
        self.FileLabel = Tkinter.StringVar()
        # Initialize text entry references
        self.apiEntry = None
        # Initialize button references
        self.fileBtn = None
        self.sfBtn = None
        self.rfBtn = None
        self.rptBtn = None
        self.gearBtn = None
        # Initialize icon references
        self.gear_raised = None
        self.gear_sunken = None

        self.initializeGUI(self.settings)

    def initializeGUI(self, settings):
        # Define grid layout manager
        self.title("VirusTotal Client")
        self.grid()

        self.widgets.createLabel(0, 0, 4, "EW", "white", "blue", "w", self.TitleLabel)
        self.TitleLabel.set("VirusTotal Client")

        self.widgets.createLabel(0, 1, 2, "EW", "black", "white", "w", self.FileLabel)
        self.FileLabel.set("Choose a File")

#        self.apiEntry = self.widgets.createEntry(0, 2, 4, "EW", self.apiLabel, "<Return>", self.setAPIKey)
        # if there is no value in APIKey, set a default apiLabel
#        confKey = settings.getAPI()
#        if confKey == '':
#            self.apiLabel.set("Enter API Key")
#        else:
#            self.apiLabel.set(confKey)

        self.fileBtn = self.widgets.createButton(2, 1, 2, "EW", "Upload", None, self.setFileName)
        self.sfBtn = self.widgets.createButton(0, 2, 1, "EW", "Send File", None, self.VTsendFile)
        self.rfBtn = self.widgets.createButton(1, 2, 1, "EW", "Rescan File", None, self.VTrescanFile)
        self.rptBtn = self.widgets.createButton(2, 2, 1, "EW", "Report", None, self.VTgetReport)
        self.gearBtn = self.widgets.createButton(3, 2, 1, '', "Settings", None, self.changeSettings)
#        self.createIcons()

        self.grid_columnconfigure(0, weight=1)
        self.resizable(True, True)
        self.update()
        self.geometry(self.geometry())

    def createIcons(self):
        self.gear_raised = Tkinter.PhotoImage(file="images\gear_raised.gif")
        self.gearBtn.config(image=self.gear_raised)
#        self.gear_sunken = Tkinter.PhotoImage(file="images\gear_sunken.gif")

    def changeSettings(self):
        # send 'self' (main GUI frame) to create "Change Settings" as a child class
        dialog = CustomDialog(parent=self, title="Change Settings")
        settingsFrame = dialog.returnFrame()
        # set focus to settingsFrame when it is spawned
        settingsFrame.focus_set()
        # assign a grid layout manager to settingsFrame
        settingsFrame.grid()

        # create label to the left of the 'resource' settings entry
        reportLabel = Tkinter.StringVar()
        self.widgets.createLabel(1, 0, 1, "EW", "black", None, "w", reportLabel, settingsFrame)
        reportLabel.set("Last Saved Report: ")
        # create label to hold the settings resource value
        inReport = Tkinter.StringVar()
        self.widgets.createLabel(2, 0, 3, "EW", "black", None, "w", inReport, settingsFrame)
        inReport.set(self.settings.getResource())

        apiLabel = Tkinter.StringVar()
        self.widgets.createLabel(1, 1, 1, "EW", "black", None, "w", apiLabel, settingsFrame)
        inAPI = Tkinter.StringVar()
        self.widgets.createLabel(2, 1, 3, "EW", "black", None, "w", inAPI, settingsFrame)
        apiLabel.set("API Key: ")
        inAPI.set(self.settings.getAPI())

        fileLabel = Tkinter.StringVar()
        self.widgets.createLabel(1, 2, 1, "EW", "black", None, "w", fileLabel, settingsFrame)
        fileLabel.set("Last File: ")
        inFile = Tkinter.StringVar()
        self.widgets.createLabel(2, 2, 3, "EW", "black", None, "w", inFile, settingsFrame)
        try:
            inFile.set(self.settings.getFileName())
        except:
            inFile.set("No File Specified")

        # create text entry box for inputting the API Key and Last Saved Report in settingsFrame
        # don't bind any keys or functions to it
        apiEntry = self.widgets.createEntry(2, 1, 3, "EW", inAPI, None, None, settingsFrame)

        # create Save/Cancel buttons for settingsFrame
        self.widgets.createButton(2, 3, 1, "EW", "Save & Exit", None, lambda: self.saveSettings(dialog, apiEntry.get()), settingsFrame)
        self.widgets.createButton(4, 3, 1, "EW", "Cancel", None, lambda: self.cancel(dialog), settingsFrame)

        settingsFrame.grid_columnconfigure(0, weight=1)
#        settingsFrame.resizable(True, True)
        settingsFrame.update()
#        settingsFrame.geometry(self.geometry())

    def saveSettings(self, frame, newAPIKey):
        self.setAPIKey(newAPIKey)
        self.settings.updateConfig('apikey', newAPIKey)
        self.cancel(frame)
        pass

    def cancel(self, frame):
        # throw the focus on the main GUI (self) window
        self.focus_set()
        # destroy the specified frame
        frame.destroy()

    def VTsendFile(self):
        filename = self.FileLabel.get()
        if filename != "Choose a File":
            filename = self.settings.getFileName()
            # get response dict from VT
            response = self.comm.sendFile(filename)
            self.comm.prettyPrint(response)
            self.settings.updateConfig('resource', response['resource'])
            self.settings.updateConfig('lastfile', filename)
        else:
            tkMessageBox.showerror("Warning", "Filename not specified. Please upload a file.")

    def VTrescanFile(self):
        resource_id = self.settings.getResource()
        if resource_id != '':
            response = self.comm.reScan(resource_id)
            self.comm.prettyPrint(response)
        else:
            tkMessageBox.showerror("Warning", "You must specify a resource ID to rescan a file.")

    def VTgetReport(self):
        resource_id = self.settings.getResource()
        if resource_id != '':
            response = self.comm.getReport(resource_id)
            self.comm.printReport(response)
        else:
            tkMessageBox.showerror("Warning", "You must specify a resource ID to retrieve a report.")

    def setAPIKey(self, apikey):
        if apikey is " ---- none ---- ":
            tkMessageBox.showerror("Error", "You haven't specified an API Key")
        # double check the user actually wants to change his/her api key
        if tkMessageBox.askyesno("Warning", "Are you sure you want to change your API Key?"):
            self.settings.setAPI(apikey)

    # Uses a File Dialog helper class (tkFileDialog) to spawn a window for the user to choose a filename
    def setFileName(self):
        # Change filename settings after asking the user which filename he/she wants to upload
        newfile = str(self.askopenfilename(self, 'Upload a File'))
        self.settings.setFileName(newfile)
        # Change the content of FileLabel to reflect the selected filename
        filename = self.settings.getFileName()
        self.FileLabel.set(filename)

    # Helper function for getFileName(), because tkFileDialog requires a separate function to properly create dialog
    def askopenfilename(self, parent, title):
        return tkFileDialog.askopenfilename(parent=parent, title=title)


class CustomDialog(Tkinter.Toplevel):

    def __init__(self, parent, title="Client for VirusTotal"):
        Tkinter.Toplevel.__init__(self, parent)
        self.parent = parent
        # spawn custom dialog window as a child of parent class
        self.transient(parent)
        # default title is "Client for VirusTotal"
        self.title(title)
        self.result = None
        # create a "body" for a dialog, then set it to be the focus of the app
#        self.initial_focus = self.body(body)
#        body.pack(padx=5, pady=5)
#        self.buttonbox()
#        self.grab_set()
#        if not self.initial_focus:
#            self.initial_focus = self
#        self.protocol("WM_DELETE_WINDOW", self.cancel)
#        self.geometry("+%d+%d" % (parent.winfo_rootx()+50, parent.winfo_rooty()+50))
#        self.initial_focus.focus_set()
#        self.wait_window(self)

    # return the CustomDialog frame to add widgets to later
    def returnFrame(self):
        return Tkinter.Frame(self)

    def body(self, master):
        # create dialog body
        # return widget that should have initial focus
        pass

    def buttonbox(self):
        # add standard button box. override if you don't want the standard buttons
        box = Tkinter.Frame(self)
        w = Tkinter.Button(box, text="OK", width=10, command=self.ok, default=Tkinter.ACTIVE)
        w.pack(side=Tkinter.LEFT, padx=5, pady=5)
        w = Tkinter.Button(box, text="Cancel", width=10, command=self.cancel)
        w.pack(side=Tkinter.LEFT, padx=5, pady=5)
        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.cancel)
        box.pack()

    def ok(self, event=None):
        if not self.validate():
            # put focus back
            self.initial_focus.focus_set()
            return
        self.withdraw()
        self.update_idletasks()
        self.apply()

    def validate(self):
        # override
        return 1

    def apply(self):
        # override
        pass


class Widgets():

    def __init__(self, frame):
        # frame refers to the frame used to assign the widgets to, usually 'self'
        self.frame = frame

    # helper function for creating labels quickly
    def createLabel(self, col, row, colsp, sticky, fg, bg, anchor, textVar, frame=None):
        if frame:
            label = Tkinter.Label(frame, textvariable=textVar, anchor=anchor, fg=fg, bg=bg)
        else:
            label = Tkinter.Label(self.frame, textvariable=textVar, anchor=anchor, fg=fg, bg=bg)
        label.grid(column=col, row=row, columnspan=colsp, sticky=sticky)

    # helper function for creating buttons quickly
    def createButton(self, col, row, colsp, sticky, text, image, command, frame=None):
        if frame:
            button = Tkinter.Button(frame, text=text, command=command, image=image)
        else:
            button = Tkinter.Button(self.frame, text=text, command=command, image=image)
        button.grid(column=col, row=row, columnspan=colsp, sticky=sticky)
        return button

    # helper function for creating text boxes quickly
    def createEntry(self, col, row, colsp, sticky, text, keyToBind, bind, frame=None):
        if frame:
            apiEntry = Tkinter.Entry(frame, textvariable=text)
        else:
            apiEntry = Tkinter.Entry(self.frame, textvariable=text)
        apiEntry.grid(column=col, row=row, columnspan=colsp, sticky=sticky)
        apiEntry.bind(keyToBind, bind)
        return apiEntry


# For Debugging
if __name__ == "__main__":
    # Create new gui without a parent container
    try:
        gui = GUI(None)
        gui.mainloop()
    except Exception as e:
        print "[-] " + str(e)
        print_exc()
