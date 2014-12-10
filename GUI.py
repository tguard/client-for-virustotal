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
        # Create the GUI application
        # Initialize label references
        self.TitleLabel = Tkinter.StringVar()
        self.FileLabel = Tkinter.StringVar()
        self.Message = Tkinter.StringVar()
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
        self.rpt_raised = None
        self.rpt_sunken = None
        self.sf_raised = None
        self.sf_sunken = None
        self.banner = None
        self.createIcons(size=124)

        self.initializeGUI()

    def initializeGUI(self):
        # Define grid layout manager
        self.title("VirusTotal Client")
        self.grid()

        # Header for application
        self.TitleLabel.set("VirusTotal Client")
        Tkinter.Label(master=self, textvariable=self.TitleLabel, anchor="w", fg="white", bg="blue").grid(column=0, row=0, columnspan=4, sticky="EW")

        # Displays filename of currently selected file
        self.FileLabel.set("Choose a File")
        Tkinter.Label(master=self, textvariable=self.FileLabel, anchor="w", fg="black", bg="white").grid(column=0, row=1, columnspan=2, sticky="NSEW")

        # Create buttons for interacting with VirusTotal API
        self.fileBtn = Tkinter.Button(text="Upload", command=self.setFileName, image=None)
        self.fileBtn.grid(column=2, row=1, columnspan=2, sticky='EW')
        self.sfBtn = Tkinter.Button(text="Send File", command=self.VTsendFile, image=None)
        self.sfBtn.grid(column=0, row=2, columnspan=1, sticky='EW')
        self.rfBtn = Tkinter.Button(text="Rescan File", command=self.VTrescanFile, image=None)
        self.rfBtn.grid(column=1, row=2, columnspan=1, sticky='EW')
        self.rptBtn = Tkinter.Button(text="Report", command=self.VTgetReport, image=None)
        self.rptBtn.grid(column=2, row=2, columnspan=1, sticky='EW')
        self.gearBtn = Tkinter.Button(text="Settings", command=self.changeSettings, image=None)
        self.gearBtn.grid(column=3, row=2, columnspan=1, sticky='EW')

        self.grid_columnconfigure(0, weight=1)
        self.resizable(True, True)
        self.update()
        self.geometry(self.geometry())

    def changeSettings(self):
        SettingsWindow(None)

    def createIcons(self, size):
        # create all image references here
        self.gear_raised = Tkinter.PhotoImage(file="images\\"+str(size)+"\gear_raised.gif")
        self.gear_sunken = Tkinter.PhotoImage(file="images\\"+str(size)+"\gear_sunken.gif")
        self.rpt_raised = Tkinter.PhotoImage(file="images\\"+str(size)+"\\report_file_raised.gif")
        self.rpt_sunken = Tkinter.PhotoImage(file="images\\"+str(size)+"\\report_file_sunken.gif")
        self.sf_raised = Tkinter.PhotoImage(file="images\\"+str(size)+"\send_file_raised.gif")
        self.sf_sunken = Tkinter.PhotoImage(file="images\\"+str(size)+"\send_file_sunken.gif")
        self.banner = Tkinter.PhotoImage(file="images\\"+str(size)+"\\vt_header.gif")

    def VTsendFile(self):
        filename = self.FileLabel.get()
        if filename != "Choose a File":
            filename = self.settings.getFileName()
            # get response dict from VT
            response = self.comm.sendFile(filename)
            self.comm.prettyPrint(response)
            self.settings.updateConfig('resource', response['resource'])
            # cut off the directory path of filename in order to update config file
            filename = filename.split('/')[-1]
            self.settings.updateConfig('lastfile', filename)
        else:
            tkMessageBox.showerror("Warning", "Filename not specified. Please upload a file.")

    # rescan the last-scanned file based on its resource id
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
            report = self.comm.printReport(response)
            self.Message.set(report)
            # create label to store the report in
            Tkinter.Label(master=self, textvariable=self.Message, anchor="w", fg="black", bg="white").grid(column=0, row=3, columnspan=4, sticky="EW")
        else:
            tkMessageBox.showerror("Warning", "You must specify a resource ID to retrieve a report.")

    # Uses a File Dialog helper class (tkFileDialog) to spawn a window for the user to choose a filename
    def setFileName(self):
        # Change filename settings after asking the user which filename he/she wants to upload
        newfile = str(self.askopenfilename(self, 'Upload a File'))
        if newfile is not "":
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

        # create label to the left of the 'resource' settings entry
        reportLabelString = Tkinter.StringVar()
        reportLabelString.set("Last Saved Report: ")
        reportLabel = Tkinter.Label(master=self.settingsFrame, textvariable=reportLabelString, anchor=Tkinter.CENTER, fg="black", bg=None)
        reportLabel.grid(column=1, row=0, columnspan=1, sticky="EW")

        # create label to hold the settings resource value
        inReportText = Tkinter.StringVar()
        lastfile = self.settings.getFileName()
        if lastfile is '':
            inReportText.set("None")
        else:
            inReportText.set(lastfile)
        inReport = Tkinter.Label(master=self.settingsFrame, textvariable=inReportText, anchor="w", fg="black", bg=None)
        inReport.grid(column=2, row=0, columnspan=3, sticky="EW")

        # create label that displays next to API text entry box
        apiText = Tkinter.StringVar()
        apiText.set("API Key: ")
        apiLabel = Tkinter.Label(master=self.settingsFrame, textvariable=apiText, anchor=Tkinter.CENTER, fg="black", bg=None)
        apiLabel.grid(column=1, row=1, columnspan=1, sticky="EW")

        # create label that displays API key inside API text entry box
        apiEntryText = Tkinter.StringVar()
        apikey = self.settings.getAPI()
        if apikey is '':
            apiEntryText.set("None")
        else:
            apiEntryText.set(apikey)
        apiEntryLabel = Tkinter.Label(master=self.settingsFrame, textvariable=apiEntryText, anchor="w", fg="black", bg=None)
        apiEntryLabel.grid(column=2, row=1, columnspan=3, sticky="EW", padx=5)

        # create text entry for inputting the API key
        apiEntry = Tkinter.Entry(master=self.settingsFrame, textvariable=apiEntryText)
        apiEntry.grid(column=2, row=1, columnspan=3, sticky="EW")

        # create Save/Cancel buttons for settingsFrame
        self.saveBtn = Tkinter.Button(master=self.settingsFrame, text="Save & Exit", command=None, image=None)
        self.saveBtn.grid(column=2, row=3, columnspan=1, sticky="EW")
        self.cancelBtn = Tkinter.Button(master=self.settingsFrame, text="Cancel", command=lambda: self.cancel(frame=self.settingsDialog), image=None)
        self.cancelBtn.grid(column=4, row=3, columnspan=1, sticky="EW")

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
        # throw the focus on the main GUI (self) window and destroy 'frame'
        self.focus_set()
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


# For Debugging
if __name__ == "__main__":
    # Create new gui without a parent container
    try:
        gui = GUI(None)
        gui.mainloop()
    except Exception as e:
        print "[-] " + str(e)
        print_exc()
