__author__ = 'Thomas Gardner'
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
        self.comm = Communicator(self.settings)
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

        self.initializeGUI()

    def initializeGUI(self):
        # Define grid layout manager
        self.title("VirusTotal Client")
        self.grid()

        self.widgets.createLabel(0, 0, 4, "EW", "white", "blue", "w", self.TitleLabel, self)
        self.TitleLabel.set("VirusTotal Client")

        self.widgets.createLabel(0, 1, 2, "EW", "black", "white", "w", self.FileLabel, self)
        self.FileLabel.set("Choose a File")

        self.fileBtn = self.widgets.createButton(2, 1, 2, "EW", "Upload", None, self.setFileName, self)
        self.sfBtn = self.widgets.createButton(0, 2, 1, "EW", "Send File", None, self.VTsendFile, self)
        self.rfBtn = self.widgets.createButton(1, 2, 1, "EW", "Rescan File", None, self.VTrescanFile, self)
        self.rptBtn = self.widgets.createButton(2, 2, 1, "EW", "Report", None, self.VTgetReport, self)
        self.gearBtn = self.widgets.createButton(3, 2, 1, '', "Settings", None, self.changeSettings, self)
#        self.createIcons()

        self.grid_columnconfigure(0, weight=1)
        self.resizable(True, True)
        self.update()
        self.geometry(self.geometry())

    def changeSettings(self):
        # create new dialog for changing settings as a child class of 'self'
        settingsDialog = SettingsWindow(None)

    def createIcons(self):
        self.gear_raised = Tkinter.PhotoImage(file="images\gear_raised.gif")
        self.gear_sunken = Tkinter.PhotoImage(file="images\gear_sunken.gif")

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
#            self.settings.updateConfig('lastfile', response['filename'])
        else:
            tkMessageBox.showerror("Warning", "You must specify a resource ID to rescan a file.")

    def VTgetReport(self):
        resource_id = self.settings.getResource()
        if resource_id != '':
            response = self.comm.getReport(resource_id)
            self.comm.printReport(response)
        else:
            tkMessageBox.showerror("Warning", "You must specify a resource ID to retrieve a report.")

    # Uses a File Dialog helper class (tkFileDialog) to spawn a window for the user to choose a filename
    def setFileName(self):
        # Change filename settings after asking the user which filename he/she wants to upload
        newfile = str(self.askopenfilename(self, 'Upload a File'))
        self.settings.setFileName(newfile)
        # Change the content of FileLabel to reflect the selected filename
        filename = self.settings.getFileName()
        self.FileLabel.set(filename)

    # Helper function for getFileName()
    # tkFileDialog requires a separate function to properly create dialog for some reason
    def askopenfilename(self, parent, title):
        return tkFileDialog.askopenfilename(parent=parent, title=title)

# A class for the client's Settings GUI
class SettingsWindow(Tkinter.Tk):

    def __init__(self, parent):
        print "[+] Building SettingsWindow..."
        Tkinter.Tk.__init__(self, parent)
        # send 'self' (main GUI frame) to create "Change Settings" as a child class
        self.settingsDialog = CustomDialog(parent=parent, title="Change Settings")
        self.settingsFrame = self.settingsDialog.returnFrame()
        self.settings = Settings()
        # go to settingsFrame when spawned, and give it a grid layout
        self.settingsFrame.grid()
        self.settingsFrame.focus_set()
        self.initializeSettings()

    def initializeSettings(self):

        widgets = Widgets(frame=self.settingsFrame)

        # create label to the left of the 'resource' settings entry
        reportLabel = Tkinter.StringVar()
        widgets.createLabel(1, 0, 1, "EW", "black", None, Tkinter.CENTER, reportLabel, self.settingsFrame)
        reportLabel.set("Last Saved Report: ")

        # create label to hold the settings resource value
        inReport = Tkinter.StringVar()
        widgets.createLabel(2, 0, 3, "EW", "black", None, "w", inReport, self.settingsFrame)
        lastfile = self.settings.getFileName()
        if lastfile is '':
            inReport.set("None")
        else:
            inReport.set(self.settings.getFileName())

        apiLabel = Tkinter.StringVar()
        widgets.createLabel(1, 1, 1, "EW", "black", None, Tkinter.CENTER, apiLabel, self.settingsFrame)
        apiLabel.set("API Key: ")

        inAPI = Tkinter.StringVar()
        widgets.createLabel(2, 1, 3, "EW", "black", None, "w", inAPI, self.settingsFrame)
        apikey = self.settings.getAPI()
        if apikey is '':
            inAPI.set("None")
        else:
            inAPI.set(self.settings.getAPI())

        # create text entry for inputting the API key
        apiEntry = widgets.createEntry(2, 1, 3, "EW", inAPI, None, None, self.settingsFrame)

        # create Save/Cancel buttons for settingsFrame
        widgets.createButton(2, 3, 1, "EW", "Save & Exit", None, None, self.settingsFrame)
        widgets.createButton(4, 3, 1, "EW", "Cancel", None, lambda: self.cancel(frame=self.settingsDialog), self.settingsFrame)

        self.grid_columnconfigure(0, weight=1)
        # prevents Tk window from popping up
        self.withdraw()
        # update remaining running processes
        self.update_idletasks()
        self.resizable(True, True)
#        self.geometry(self.geometry)

    def setAPIKey(self, apikey):
        if apikey is "":
            tkMessageBox.showerror("Error", "You haven't specified an API Key")
        # double check the user actually wants to change his/her api key
        if tkMessageBox.askyesno("Warning", "Are you sure you want to change your API Key?"):
            self.settings.setAPI(apikey)

    def saveSettings(self, frame, newAPIKey):
        print "[+] Saving settings..."
        self.setAPIKey(newAPIKey)
        self.settings.updateConfig('apikey', newAPIKey)
        self.cancel(frame)
        pass

    def cancel(self, frame):
        # throw the focus on the main GUI (self) window
        self.focus_set()
        # destroy the specified frame
        frame.destroy()


# dedicated to creating new child dialogs
class CustomDialog(Tkinter.Toplevel):

    def __init__(self, parent, title="Client for VirusTotal"):
        Tkinter.Toplevel.__init__(self, parent)
        self.parent = parent
        # spawn custom dialog window as a child of parent class
        self.transient(parent)
        # default title is "Client for VirusTotal"
        self.title(title)

    # return the CustomDialog frame to add widgets to later
    def returnFrame(self):
        return Tkinter.Frame(self)


# dedicated to setting up all grid layout widgets
class Widgets():

    def __init__(self, frame):
        # frame refers to the frame used to assign the widgets to, usually 'self'
        self.frame = frame

    # helper function for creating labels quickly
    def createLabel(self, col, row, colsp, sticky, fg, bg, anchor, textVar, frame):
        if frame:
            label = Tkinter.Label(frame, textvariable=textVar, anchor=anchor, fg=fg, bg=bg)
        else:
            label = Tkinter.Label(self.frame, textvariable=textVar, anchor=anchor, fg=fg, bg=bg)
        label.grid(column=col, row=row, columnspan=colsp, sticky=sticky)

    # helper function for creating buttons quickly
    def createButton(self, col, row, colsp, sticky, text, image, command, frame):
        if frame:
            button = Tkinter.Button(frame, text=text, command=command, image=image)
        else:
            button = Tkinter.Button(self.frame, text=text, command=command, image=image)
        button.grid(column=col, row=row, columnspan=colsp, sticky=sticky)
        return button

    # helper function for creating text boxes quickly
    def createEntry(self, col, row, colsp, sticky, text, keyToBind, bind, frame):
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
