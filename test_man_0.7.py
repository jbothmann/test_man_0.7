from tkinter import *
from tkinter import messagebox
from tkinter import filedialog
from tkSelectLabel import * #Local Import
from datetime import datetime
from struct import *
import serial
from time import sleep
import types
import json
import copy

version = "0.7"

serTimeout = 0.1

numberOfData = 32
numberOfControls = 32

ser = None #initialize serial connection to none

#base64 encoded bytestring which contains the favicon
encoded_string = b'iVBORw0KGgoAAAANSUhEUgAAAEAAAABACAYAAACqaXHeAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAASQSURBVHhe7ZpdbBRVFMf/K61AgFKxfegmoA9SC0E0JGCIBqg0giH6Ag+KL2BEjU3E+PEkbJAHNDHVaAL4EYUH06A+iAFMSSG8WROFAm2wHyDGpppAhLZJW+luOZ7LnAnb7el054tpnPml/5x77+69e8+ZO/djpikC+C++3CU2tiQBEBtbkgCIjS1JAMTGliQAYmNLEgCxsSUJgNjYcmdOg6WlwPp1wIYNQHU1h32afMA/ffOmpBmTtntDJp3XtdFRSTCm3P7M2MI2bG61l/e9N94EenqsvI00FZ7q1hJ1dhCN5qLV0SNq/8IdAS+9COzdx1c84jstmwWWLQMu/CYFtwmvZ2tWTw3nDQcPqM4bwhkBd/M939oK1NRIQYQMDAAPcj+uXJGCsYRzebZtmxrOGxoaJnTeEPwImDcP6OywbNT09loXYmhYCsYT/AjI7Jgazht2vOPovCHYEWDW+PPnrHXfiWPHLOVyUhAQ5eXAqlW851gPtJ0Hlj/K3k3inglAYPrhe30NzlfbOaLp0/X6QenhpUQrV+qfFSi4ADxRqzucr6FBq3Na/YgUTABKSohaz+hO5+v17Xr9CBVMALZu0R3OVy5LVD5Xrx+h/E+Cs2cDHReAqrQUOGAOIqd/9Tn5cXd7/wb27we6L0qZD+xIeFZmp37Fw9ZAnzXvaH1yIX8jIF3FV583PbNmScEdpu868AgfcgqPuC7wtxHavTs65w3l9wA7eePlA+8jIM33/B+XgWn2w42IuNjNh51FknGP9xGwaWP0zhsGByXhDe8BqF0jCY+Yjh89AjQ28ra1beyjLDc0HpKER8wt4EktP+mzczH67luiysqx7VUvJPrqS6KRG3odTd1dvrfV3gOw7kmi69f0jjmp4QOiVEpv0+jxx4h6/tTrFuqZp/U2XMjfMjhnDrBiBW+GilwJRrJAU5P10zZVvJS+8jJw6hTQ0gLcGAGWPmQ9UXKiuZlPfU9Jxgd2JCJRaSnR6V9uX9E+HlHfHCLalRl7pQs1PES0qEZv06WiDcBzz+oOTqaPPtTb86BwngkWS12dJFxw9Sqw613J+Ke4ACxZAiyYL5kAqbhXEi7IZID+fsn4Z/JJ0Gx2fubJafFiYN9e3vt3WuWjsm7fGkgOa7h5DWbW+JMn+BT3lxQK9fXAJx9LpgjOngWW86Trdc+gYd8LE+r5zfp96FYD/USb+Z7Pb9ssh5s2EjX9SPTvsF7PVm7EWiLz6wcg5wDMmEF0+ZLeIa96/z1r9i/8rYoKou2vEWXZUa1e49fj6wQg5wC8/ZbeGb9qbyN6YSvRgvlEM2cSzS0jquWzffNx/fvX/iFKp/U++tTEc0BlBdDVBZSVSUFImNfe5v1hKiUFCvWvAp9+LplgmXgVMC8VwnbeYCZZJ+fNgemzLyQTPPoIWPgA0N4OlJRIQUSYU+JqPnUGuOwVoo+APXuid/4EL5treaMUovOG8SPg/vuAAwedh2VYmH9k+P0ScPgwH5qOW9NUyPg7Df4PiPYsMAVIAiA2tiQBEBtbkgCIjS1JAMTGliQAYmNLEgCxMQX4DxvJZiayMybCAAAAAElFTkSuQmCC'

#draw the main viewer
root = Tk()
favicon = PhotoImage(data=encoded_string)
root.iconphoto(True, favicon) #sets the favicon for root and all toplevel()
root.title('Power Tools Test Manager')
running = True

#procedure to be taken when attempting to exit the program, which will prompt a save
def exitProgram():
    global running
    response = messagebox.askyesnocancel("Power Tools Test Manager", "Save before closing Test Manager?", parent=root.focus_get())
    if not response is None:
        if response:
            saveSession()
        running = False

root.protocol('WM_DELETE_WINDOW', exitProgram) #Override close button with exitProgram

#keep track of if the software is locked, if it is locked by password, and the password itself
locked = 0
passLocked = 0
password = ""

#class Theme, which holds values for the colors and styles that the program should use for all widgets.  Default values approximate Tkinter defaults.
class Theme:
    def __init__(self, colorsTitle="Default Gray", fontSizeTitle="Medium", fontTitle="Sans-Serif", bg="gray95", fg="black", contrastbg="white", contrastfg="black", selectbg="#00a2ed", selectfg="white", contrastselectbg="#00a2ed", contrastselectfg="white", fontSize=9, font="Helvetica"):
        #inititalize theme identifiers
        self.colorsTitle = colorsTitle
        self.fontSizeTitle = fontSizeTitle
        self.fontTitle = fontTitle

        #inititalize values
        self.bg = bg #colors to be used for most elements
        self.fg = fg
        self.contrastbg = contrastbg #colors to be used for elements that need to stand out from the background
        self.contrastfg = contrastfg
        self.selectbg = selectbg #colors used when highlighting text
        self.selectfg = selectfg
        self.contrastselectbg = contrastselectbg #colors used when highlighting text on contrast element
        self.contrastselectfg = contrastselectfg
        self.fontSize = fontSize
        self.font = font

    #Theme.apply, passing this method a common widget will automatically reconfigure its color and font to fit the theme
    def apply(self, widget):
        if isinstance(widget, list):  #if passed a list of widgets, recursively handle all widgets
            for oo in widget:
                self.apply(oo)
        if isinstance(widget, Tk) or isinstance(widget, Toplevel):
            widget.config(bg=self.bg)
        elif isinstance(widget, Frame):
            widget.config(bg=self.bg)
        elif isinstance(widget, LabelFrame):
            widget.config(bg=self.bg, fg=self.fg, font=(self.font, self.fontSize+2))
        elif isinstance(widget, Label):
            widget.config(bg=self.bg, fg=self.fg, font=(self.font, self.fontSize))
        elif isinstance(widget, Button) or isinstance(widget, Menubutton):
            widget.config(bg=self.bg, fg=self.fg, activebackground=self.bg, activeforeground=self.fg, font=(self.font, self.fontSize))
        elif isinstance(widget, Entry):
            widget.config(bg=self.contrastbg, fg=self.contrastfg, selectbackground=self.contrastselectbg, selectforeground=self.contrastselectfg, font=(self.font, self.fontSize))
        elif isinstance(widget, SelectLabel): #This conditional must come before Text, because SelectLabel extends Text
            widget.config(bg=self.bg, fg=self.fg, selectbackground=self.selectbg, selectforeground=self.selectfg, font=(self.font, self.fontSize))
        elif isinstance(widget, Text):
            widget.config(bg=self.contrastbg, fg=self.contrastfg, selectbackground=self.contrastselectbg, selectforeground=self.contrastselectfg, font=(self.font, self.fontSize))
        elif isinstance(widget, Checkbutton) or isinstance(widget, Radiobutton):
            widget.config(bg=self.bg, fg='black', activebackground=self.bg, activeforeground=self.bg, font=(self.font, self.fontSize))
        elif isinstance (widget, Menu):
            widget.config(bg=self.contrastbg, fg=self.contrastfg, activebackground=self.contrastselectbg, activeforeground=self.contrastselectfg, disabledforeground=None, font=(self.font, self.fontSize))
        return widget

#create a Theme object
T = Theme()

#class Test, holds all information about one test
class Test:
    #a separate tuple array to keep track of all comments in chronological order
    allComments = []

    #Constructor which creates a test with expandable data
    def __init__(self, address=-1, name="[test name]", serial="[serial number]", data=None, controlLabels=None):
        global dataFrame
        try:
            self.testNum = int(address) #Slave PLC address
        except ValueError as e:
            self.testNum = -1
        self.name = name #Should include name of unit, and test type, should be identifiably unique
        self.serial = serial #serial number of the unit #TODO: change to subtitle?
        self.status = "Offline"
        self.data = [] #data variables, a len 32 list of 4-lists, including a string defining the datum, a string defining the units, the number datum, and a boolean which determines if the datum is used
        #repair passed data if it is unsuitable or absent
        if not isinstance(data, list):
            data = [
                ["Cycles", "", 0, True]
                ]
        #handle given data, making sure that each entry is a proper 4-list   
        for ii in range(numberOfData):
            self.data.append(["", "", 0, False])
            if ii < len(data):
                if isinstance(data[ii], list):
                    if len(data[ii]) > 0:
                        if isinstance(data[ii][0], str):
                            self.data[ii][0] = data[ii][0] #set datum name, string
                            self.data[ii][3] = True #assume the data is used if it has a name
                            
                    if len(data[ii]) > 1:
                        if isinstance(data[ii][1], str):
                            self.data[ii][1] = data[ii][1] #set datum unit, string
                           
                    if len(data[ii]) > 2:
                        self.data[ii][2] = data[ii][2] #set datum value, currently accepts any value type
                           
                    if len(data[ii]) > 3:
                        if isinstance(data[ii][3], bool):
                            self.data[ii][3] = data[ii][3] #set show datum, boolean
                           
                elif isinstance(data[ii], str):
                    self.data[ii][0] = data[ii] #set datum name if only a string name is given
                    self.data[ii][3] = True #assume the data is used if it has a name
        #repair passed label if it is unsuitable or absent
        self.controlLabels = [] #control labels, a len 32 list of strings, which communicate what each control does
        if not isinstance(controlLabels, list):
            controlLabels = []
        #handle given labels, ensuring that each entry is a character string
        for ii in range(numberOfControls):
            self.controlLabels.append("")
            if ii < len(controlLabels):
                if isinstance(controlLabels[ii], str):
                    self.controlLabels[ii] = controlLabels[ii]
                    

        self.comments = [] #tuple list of additional notes, including error modes and manual measurements
        #contains a string representing time of report, and a string phrase description
        self.r = None #row that the test is drawn to in the main viewer
        self.c = None #column that the test is drawn to in the main viewer
        #boolean which allows the test to be hidden
        self.showTest = True
        
        #initialize labelWidgetFrame and its children.  This widget will show the title of the station and a small edit button
        self.labelWidgetFrame = Frame()
        self.stationNumLabel = Label(self.labelWidgetFrame, font=("Arial", 12))
        self.stationNumLabel.grid(row=0, column=0)
        self.button0 = Button(self.labelWidgetFrame, text="\U00002699", command=lambda: editTests(self.testNum))
        self.button0.grid(row=0, column=1)

        #initialize frame, which will be used to store the widgets
        self.frame = LabelFrame(dataFrame, labelwidget=self.labelWidgetFrame, padx=5, pady=5, relief=RIDGE)

        #initialize dataLabel, which will be used to display info
        self.dataLabel = SelectLabel(self.frame)
        #initialize statusIndicator, which will be used to visually represent the status of the test
        self.statusIndicator = Label(self.frame)

        #initialize two buttons, which will be used for test control
        self.button1 = Button(self.frame, width=14)
        self.button2 = Button(self.frame, width=14)

        #plot each widget into the frame
        self.dataLabel.grid(row=1)
        self.statusIndicator.grid(row=2, pady=2)
        #draw control buttons
        #self.button0.grid(row=0, column=1, sticky=E, pady=0)
        self.button1.grid(row=4, pady=2)
        self.button2.grid(row=5)
    
       
    #Test.draw, draws the information to the screen based on internal info
    #parameters are positional info which will determine where it is drawn
    def draw(self, r, c):
        global locked
        global dataFrame
        self.r = r
        self.c = c

        #apply theme to all widgets
        T.apply([self.labelWidgetFrame, self.stationNumLabel, self.button0, self.frame, self.dataLabel, self.statusIndicator, self.button1, self.button2])

        self.stationNumLabel.config(text="Station " + str(self.testNum), font=(T.font, T.fontSize+2))
        self.frame.grid(row=r, column=c, pady=3, padx=3) #regrid the frame

        #add correct information to widgets
        self.updateLabel()
        

    def redraw(self):
        self.draw(self.r, self.c)
        
    #TODO: Is this method doing too much?
    #updateLabel, reconfigures the widgets within the gui frame to accurately represent and control the incoming data
    def updateLabel(self):
        global root
        self.dataLabel.config(text=self.toString())
        if self.status == "In Progress":
            self.statusIndicator.config(text="\U00002B24   In Progress", fg="green")
            self.button1.config(text="Pause", command=lambda: pause(self.testNum), state=NORMAL)
            self.button2.config(text="More Controls", command=lambda: openControls(self.testNum), state=NORMAL)
        elif self.status == "Paused":
            self.statusIndicator.config(text="\U00002B24   Paused", fg="T.fg")
            self.button1.config(text="Resume", command=lambda: resume(self.testNum), state=NORMAL)
            self.button2.config(text="More Controls", command=lambda: openControls(self.testNum), state=NORMAL)
        elif self.status == "Offline":
            self.statusIndicator.config(text="\U00002B24   Offline", fg="red")
            self.button1.config(text="Pause", state=DISABLED)
            self.button2.config(text="More Controls", state=DISABLED)
        #in any other state, such as the PLC being offline, stopped, or in an error mode
        else:
            self.statusIndicator.config(text=None)
            self.button1.config(text="Pause", state=DISABLED)
            self.button2.config(text="More Controls", state=DISABLED)
            
        if locked:
            self.button0.config(text="\U00002699", state=DISABLED, command=lambda: editTests(self.testNum))
            self.button1.config(text="PAUSE LOCKED", state=DISABLED)
            self.button2.config(text="CONTROLS LOCKED", state=DISABLED)
        else:
            self.button0.config(text="\U00002699", state=NORMAL, command=lambda: editTests(self.testNum))

        #reconfigure the minimum size of the main window
        root.update_idletasks()
        root.minsize(width=max(root.winfo_reqwidth(),400), height=max(root.winfo_reqheight(),300))

    def set(self, newData):
        for ii in range(len(newData)):
            self.data[ii][2] = newData[ii]
        self.updateLabel()

    #four methods for updating the test's status, which will also update the datalabel:
    def setNormal(self):
        if not self.status == "In Progress":
            self.status = "In Progress"
            self.updateLabel()

    def setPaused(self):
        if not self.status == "Paused":
            self.status = "Paused"
            self.updateLabel()

    def setStopped(self): #unused state
        if not self.status == "Stopped":
            self.status = "Stopped"
            self.updateLabel()

    def setOffline(self):
        if not self.status == "Offline":
            self.status = "Offline"
            self.updateLabel()

    #appends a new comment to the test
    def addComment(self, phrase):
        self.comments.append((datetime.now().strftime("%m/%d/%Y, %H:%M:%S :"), phrase))
        Test.allComments.append((self.name, datetime.now().strftime("%m/%d/%Y, %H:%M:%S :"), phrase))     

    #Test.toString, will return a text representation of the data in the Test object
    def toString(self):
        string = self.name+"\nSerial Number: "+self.serial+"\n"
        for ii in range(numberOfData):
            if self.data[ii][3]:
                string += str(self.data[ii][0])+": "+f'{self.data[ii][2]:.2f}'+" "+str(self.data[ii][1])+"\n"
        return string.rstrip()

    def toStringPlusComments(self):
        return (str(self.toString()) + "\n" + str(self.getComments())).rstrip()

    def getComments(self):
        string = ""
        for time, phrase in self.comments:
            string += time + "\n" + phrase + "\n" 
        return string.rstrip()

    def getAllComments(self):
        string = ""
        for title, time, phrase in Test.allComments:
            string += title + "\n" + time + "\n" + phrase + "\n"
        return string.rstrip()

    def setControlLabels(self, newLabels):
        for ii in range(len(newLabels)):
            if isinstance(newLabels[ii], str):
                self.controlLabels[ii] = newLabels[ii]
            
#list which holds the array of tests, currently begins empty
tests = []
#Dictionary which will be used to link address to index in tests[]
testIndexDict = {}


#Default named values when creating a new test using the gui dialog
defaultValNames = [
    "Cycles",
    "Time Elapsed",
    "Torque",
    "Speed",
    "Current Draw",
    "Voltage",
    "Temperature",
    "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", ""
    ]


def pause(slID):
    if ser is None:
        messagebox.showerror("Power Tools Test Manager", "Not connected to a serial port", parent=root.focus_get())
    else:
        msg = [
            slID, #slave ID
            0x05, #MODBUS Command (Force Single Coil)
            0x40, #Coil Address (C50)
            0x31,
            0xFF, #set ON
            0x00
        ]
        msg = msg + getCRC(msg) #append CRC
        ser.write(bytes(msg))
        sleep(serTimeout)
        ser.reset_input_buffer()

def resume(slID):
    if ser is None:
        messagebox.showerror("Power Tools Test Manager", "Not connected to a serial port", parent=root.focus_get())
    else:
        msg = [
            slID, #slave ID
            0x05, #MODBUS Command (Force Single Coil)
            0x40, #Coil Address (C50)
            0x31,
            0x00, #set OFF
            0x00
        ]
        msg = msg + getCRC(msg) #append CRC
        ser.write(bytes(msg))
        sleep(serTimeout)
        ser.reset_input_buffer()

def control(slID, controlIndex, value):
    if ser is None:
        messagebox.showerror("Power Tools Test Manager", "Not connected to a serial port", parent=root.focus_get())
    else:
        msg = [
            slID, #slave ID
            0x05, #MODBUS Command (Force Single Coil)
            0x40, #Coil Address (C101 - C132)
            (controlIndex + 0x63),
            (value*0xFF), #set ON (0xFF) or OFF (0x00)
            0x00
        ]
        msg = msg + getCRC(msg) #append CRC
        ser.write(bytes(msg))
        sleep(serTimeout)
        ser.reset_input_buffer()

def pauseAll():
    if ser is None:
        messagebox.showerror("Power Tools Test Manager", "Not connected to a serial port", parent=root.focus_get())
    else:
        msg = [
            0x00, #address "0" to indicate a broadcast pause
            0x05, #MODBUS Command (Force Single Coil)
            0x40, #Coil Address (C50)
            0x31,
            0xFF, #set ON
            0x00
        ]
        msg = msg + getCRC(msg) #append CRC
        ser.write(bytes(msg))
        sleep(serTimeout)
        ser.reset_input_buffer()

def resumeAll():
    if ser is None:
        messagebox.showerror("Power Tools Test Manager", "Not connected to a serial port", parent=root.focus_get())
    else:
        msg = [
            0x00, #address "0" to indicate a broadcast pause
            0x05, #MODBUS Command (Force Single Coil)
            0x40, #Coil Address (C50)
            0x31,
            0x00, #set OFF
            0x00
        ]
        msg = msg + getCRC(msg) #append CRC
        ser.write(bytes(msg))
        sleep(serTimeout)
        ser.reset_input_buffer()
                                  
def saveSession():
    try:
        #open *.JSON file using system dialog
        file = filedialog.asksaveasfile(parent=root, initialdir = "/", title = "Save As", filetypes = (("JSON Files","*.json"),), defaultextension="*.*")
    except OSError as e: #catch errors relating to opening the file
        messagebox.showerror("Power Tools Test Manager", "Could not save file", parent=root.focus_get())
    else:
        if not file is None:
            testList = []
            for oo in tests:
                testList.append([oo.testNum, oo.name, oo.serial, oo.data, oo.controlLabels])
            json.dump(testList, file)
    finally:
        if not file is None:
            file.close()
        
def openSession():
    try:
        #open *.JSON file using system dialog
        file = filedialog.askopenfile(parent=root, initialdir = "/", title = "Open", filetypes = (("JSON Files","*.json"),))
    except OSError as e: #catch errors relating to opening the file
        messagebox.showerror("Power Tools Test Manager", "Could not open file", parent=root.focus_get())
    else:
        if not file is None:
            testList = json.load(file)
            for oo in testList:
                if len(oo) >= 5: #prevent oob errors
                    tests.append(Test(oo[0], oo[1], oo[2], oo[3], oo[4]))
                elif len(oo) >= 4: #0.5 version file support
                    tests.append(Test(oo[0], oo[1], oo[2], oo[3]))
    finally:
        if not file is None:
            file.close()
        update()
        
def connect():
    global ser
    #setup the new menu
    connector = T.apply(Toplevel())
    connector.title('Connect')
    connector.grab_set() #make window modal
    connector.focus_set()

    currentPort = 0

    #Add ports to dropdown menu
    def getCOMs():
        select(0)  #reset dropdown menu
        dropdown.menu.delete(0, END)
        for ii in range(256): #Scan all serial ports, and include all available ports in portList
            try:
                s = serial.Serial('COM%s' % (ii + 1))
                s.close()
                dropdown.menu.add_command(label='COM%s' % (ii + 1), command = lambda x=ii+1: select(x))
            except (OSError, serial.serialutil.SerialException):
                pass

    #select is called every time a new option is chosen from the dropdown menu.  It updates the window to the new state
    def select(port):
        nonlocal currentPort
        currentPort = port
        if currentPort > 0 and currentPort <= 256:
            dropdown.config(text='COM%s' % (currentPort)+" \U000025BC")
            connectButton.config(state=NORMAL)                       
        else:
            dropdown.config(text="Select a COM port \U000025BC")
            connectButton.config(state=DISABLED)

    #connects the program to the chosen COM port
    def connect():
        global ser
        global serTimeout
        try:
            if not ser is None:
                ser.close()
            ser = serial.Serial(port = 'COM%s' % (currentPort), baudrate=38400, parity=serial.PARITY_ODD, stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS, timeout=serTimeout)
            ser.reset_input_buffer()
        except serial.serialutil.SerialException:
            messagebox.showerror("Power Tools Test Manager", "Could not connect to COM port", parent=root.focus_get())
        else:
            connector.destroy()

    #draw port chooser dropdown
    dropdown = T.apply(Menubutton(connector, width=17, relief=RAISED))
    dropdown.menu = T.apply(Menu(dropdown, tearoff=0))
    dropdown["menu"] = dropdown.menu
    dropdown.grid(row=0, column=0, padx=5, pady=5)

    #refresh button
    T.apply(Button(connector, text='Rescan COM Ports', command=getCOMs)).grid(row=0, column=1, padx=5, pady=5)

    #connect Button
    connectButton = T.apply(Button(connector, text='Connect', command=connect))
    connectButton.grid(row=0, column=2, padx=5, pady=5)

    #close button
    T.apply(Button(connector, text='Cancel', command=connector.destroy)).grid(row=0, column=3, padx=5, pady=5)

    getCOMs() #scan ports to populate list for the first time

    #set min window size
    connector.update_idletasks()
    connector.minsize(width=max(connector.winfo_reqwidth(),0), height=max(connector.winfo_reqheight(),0))

#editTests, creates a new dialog for editting the information of each test
def editTests(initialTestNum=0):
    global tests
    if len(tests) == 0:
        messagebox.showerror("Power Tools Test Manager", "There are no tests to edit", parent=root.focus_get())
        return
    #setup the new menu
    editor = T.apply(Toplevel())
    editor.title("Edit Stations")
    editor.grab_set() #make window modal
    editor.focus_set()

    topFrame = T.apply(Frame(editor, bd=0))
    topFrame.pack(side=TOP)

    midFrame = T.apply(Frame(editor, bd=0))
    midFrame.pack(side=TOP)

    botFrame = T.apply(Frame(editor, bd=0))
    botFrame.pack(side=BOTTOM)

    #find the index associated with the given testNum, or resolve to a default value otherwise
    if initialTestNum in testIndexDict:
        currentTestIndex=testIndexDict[initialTestNum]
    else:
        currentTestIndex=-1

    #Draw empty fields, may want to disable in the future
    T.apply(Label(topFrame, text="PLC Slave Address: ")).grid(row=1, column=1)
    slaveAddressEntry = T.apply(Entry(topFrame))
    slaveAddressEntry.grid(row=1, column=2, pady=5, padx=10)
    
    T.apply(Label(topFrame, text="Station Name: ")).grid(row=2, column=1)
    nameEntry = T.apply(Entry(topFrame))
    nameEntry.grid(row=2, column=2, pady=5, padx=10)

    T.apply(Label(topFrame, text="Serial Number: ")).grid(row=3, column=1)
    serialEntry = T.apply(Entry(topFrame))
    serialEntry.grid(row=3, column=2, pady=5, padx=10)
    
    T.apply(Label(midFrame, text="Enter names and units for data types\n Select checkbox to display datatype on test manager:")).grid(row=2, column=0, columnspan=8)

    #Building an array of the interactable objects for expandable data
    numLabel = []
    valNameEntries = []
    unitEntries = []
    showEntry = []
    showEntryVar = []
    for ii in range(numberOfData):
        numLabel.append(T.apply(Label(midFrame, text=str(ii+1))))
        valNameEntries.append(T.apply(Entry(midFrame)))
        unitEntries.append(T.apply(Entry(midFrame, width=5)))
        showEntryVar.append(IntVar())
        showEntry.append(T.apply(Checkbutton(midFrame, variable=showEntryVar[ii], onvalue=1, offvalue=0)))

        numLabel[ii].grid(row=(ii%16+3), column=(int(ii/16)*4))
        valNameEntries[ii].grid(row=(ii%16+3), column=(int(ii/16)*4+1), padx=5)
        unitEntries[ii].grid(row=(ii%16+3), column=(int(ii/16)*4+2), padx=0)
        showEntry[ii].grid(row=(ii%16+3), column=(int(ii/16)*4+3))

    def save():
        tests[currentTestIndex].testNum = int(slaveAddressEntry.get()) 
        tests[currentTestIndex].name = nameEntry.get()
        tests[currentTestIndex].serial = serialEntry.get()
        for ii in range(numberOfData):
            tests[currentTestIndex].data[ii][0] = valNameEntries[ii].get()
            tests[currentTestIndex].data[ii][1] = unitEntries[ii].get()
            tests[currentTestIndex].data[ii][3] = bool(showEntryVar[ii].get())
        update()

    def apply():
        save()
        messagebox.showinfo("Power Tools Test Manager", "Changes Saved", parent=root.focus_get())

    def saveAndClose():
        save()
        editor.destroy()
    
    #select, fills fields with existing info when a test is selected 
    def select(testIndex):
        global tests
        nonlocal currentTestIndex
        currentTestIndex=testIndex
        if (currentTestIndex >= 0):
            dropdown.config(text=("Station "+str(tests[currentTestIndex].testNum)+": "+tests[testIndex].name+" \U000025BC"))

            slaveAddressEntry.config(state=NORMAL)
            slaveAddressEntry.delete(0, END)
            slaveAddressEntry.insert(0, tests[currentTestIndex].testNum)
            nameEntry.config(state=NORMAL)
            nameEntry.delete(0, END)
            nameEntry.insert(0, tests[currentTestIndex].name)
            serialEntry.config(state=NORMAL)
            serialEntry.delete(0, END)
            serialEntry.insert(0, tests[currentTestIndex].serial)
            
            for ii in range(numberOfData):
                valNameEntries[ii].config(state=NORMAL)
                valNameEntries[ii].delete(0, END)
                valNameEntries[ii].insert(0, tests[currentTestIndex].data[ii][0])
                unitEntries[ii].config(state=NORMAL)
                unitEntries[ii].delete(0, END)
                unitEntries[ii].insert(0, tests[currentTestIndex].data[ii][1])
                
                
                showEntry[ii].config(state=NORMAL)
                if tests[currentTestIndex].data[ii][3] == 1:
                    showEntry[ii].select()
                else:
                    showEntry[ii].deselect()

            saveButton.config(state=NORMAL)
            saveAndCloseButton.config(state=NORMAL)
            selectAllButton.config(state=NORMAL)
            deselectAllButton.config(state=NORMAL)
        else:
            dropdown.config(text=("Choose a station to edit \U000025BC"))
            
            slaveAddressEntry.delete(0, END)
            slaveAddressEntry.config(state=DISABLED)
            nameEntry.delete(0, END)
            nameEntry.config(state=DISABLED)
            serialEntry.delete(0, END)
            serialEntry.config(state=DISABLED)
            
            for ii in range(numberOfData):
                valNameEntries[ii].delete(0, END)
                valNameEntries[ii].config(state=DISABLED)
                unitEntries[ii].delete(0, END)
                unitEntries[ii].config(state=DISABLED)
                showEntry[ii].deselect()
                showEntry[ii].config(state=DISABLED)

            saveButton.config(state=DISABLED)
            saveAndCloseButton.config(state=DISABLED)
            selectAllButton.config(state=DISABLED)
            deselectAllButton.config(state=DISABLED)
            

    #quickly selects all data
    def selectAll():
        nonlocal showEntry
        for i in range(len(showEntry)):
            showEntry[i].select()
            
    #quickly deselects all data   
    def deselectAll():
        nonlocal showEntry
        for i in range(len(showEntry)):
            showEntry[i].deselect()

    #draw test chooser dropdown
    dropdown = T.apply(Menubutton(topFrame, text="[default]", relief=RAISED))
    dropdown.menu = T.apply(Menu(dropdown, tearoff=0))
    dropdown["menu"] = dropdown.menu
    for ii in range(len(tests)):
        dropdown.menu.add_command(label=("Station "+str(tests[ii].testNum)+": "+tests[ii].name), command=lambda x=ii: select(x))
    dropdown.grid(row=0, column=2, pady=5, padx=10)

    #save without closing button
    saveButton = T.apply(Button(botFrame, text="Apply Changes", command=apply))
    saveButton.grid(row=0, column=2, padx=5, pady=5)

    #save button
    saveAndCloseButton = T.apply(Button(botFrame, text="Save and Close", command=saveAndClose))
    saveAndCloseButton.grid(row=0, column=3, padx=5, pady=5)

    #cancel button
    T.apply(Button(botFrame, text="Close", command=editor.destroy)).grid(row=0, column=4, padx=5, pady=5)

    #Select All button
    selectAllButton = T.apply(Button(botFrame, text="Select All", command=selectAll))
    selectAllButton.grid(row=0, column=0, padx=5, pady=5)
    
    #Deselect All button
    deselectAllButton = T.apply(Button(botFrame, text="Deselect All", command=deselectAll))
    deselectAllButton.grid(row=0, column=1, padx=5, pady=5)

    select(currentTestIndex)

    #set min window size
    editor.update_idletasks()
    editor.minsize(width=max(editor.winfo_reqwidth(),300), height=max(editor.winfo_reqheight(),200))

#addTest(), adds a new test to the end of the list
def addTest():
    global tests
    global defaultValNames

    #setup the new menu
    adder = T.apply(Toplevel())
    adder.title("Add Station")
    adder.grab_set() #make window modal
    adder.focus_set()

    topFrame = T.apply(Frame(adder, bd=0))
    topFrame.pack(side=TOP)

    midFrame = T.apply(Frame(adder, bd=0))
    midFrame.pack(side=TOP)

    botFrame = T.apply(Frame(adder, bd=0))
    botFrame.pack(side=BOTTOM)

    #Draw empty fields
    T.apply(Label(topFrame, text="PLC Slave Address: ")).grid(row=0, column=0)
    slaveAddressEntry = T.apply(Entry(topFrame))
    slaveAddressEntry.grid(row=0, column=1, pady=5, padx=10)
    
    T.apply(Label(topFrame, text="Station Name: ")).grid(row=1, column=0)
    nameEntry = T.apply(Entry(topFrame))
    nameEntry.grid(row=1, column=1, pady=5, padx=10)

    T.apply(Label(topFrame, text="Serial Number: ")).grid(row=2, column=0)
    serialEntry = T.apply(Entry(topFrame))
    serialEntry.grid(row=2, column=1, pady=5, padx=10)

    T.apply(Label(topFrame, text="Enter names and units for data types.\n Select checkbox to display datatype on test manager:")).grid(row=3, column=0, columnspan=8)

    #Building an array of the interactable objects for expandable data
    numLabel = []
    valNameEntries = []
    unitEntries = []
    showEntry = []
    showEntryVar = []
    for ii in range(numberOfData):
        #populate lists
        numLabel.append(T.apply(Label(midFrame, text=str(ii+1))))
        valNameEntries.append(T.apply(Entry(midFrame)))
        unitEntries.append(T.apply(Entry(midFrame, width=5)))
        showEntryVar.append(IntVar())
        showEntry.append(T.apply(Checkbutton(midFrame, variable=showEntryVar[ii], onvalue=1, offvalue=0)))

        #populate entries with default values
        valNameEntries[ii].insert(0, defaultValNames[ii])
        
        #draw widgets to screen
        numLabel[ii].grid(row=(ii%16+3), column=(int(ii/16)*4))
        valNameEntries[ii].grid(row=(ii%16+3), column=(int(ii/16)*4+1), padx=5)
        unitEntries[ii].grid(row=(ii%16+3), column=(int(ii/16)*4+2), padx=0)
        showEntry[ii].grid(row=(ii%16+3), column=(int(ii/16)*4+3))

    #as a default, the first 2 fields will be selected
    showEntry[0].select()
    showEntry[1].select()

    #returns true if the station is added successfully, false otherwise
    def add():
        global tests
        global defaultValNames
        try:
            testNum = int(slaveAddressEntry.get()) #Slave PLC address

            #check for duplicate slave addresses and prompt the user if a duplicate is found
            if testNum>0 and testNum in [oo.testNum for oo in tests]:
                duplicateOk = messagebox.askyesno("Power Tools Test Manager", "That address is already in use.  Continue?", parent=root.focus_get())
            else:
                duplicateOk = True
                
            if duplicateOk:
                data = []
                for ii in range(numberOfData):
                    data.append([valNameEntries[ii].get(), unitEntries[ii].get(), 0, bool(showEntryVar[ii].get())])
                    
                tests.append(Test(slaveAddressEntry.get(), nameEntry.get(), serialEntry.get(), data))
                update()
                return True
            else:    
                return False
            
        except ValueError as e:
            messagebox.showerror("Power Tools Test Manager", "Invalid Address", parent=root.focus_get())
            return False

    def addDontExit():
        if add():
            messagebox.showinfo("Power Tools Test Manager", "Test Added", parent=root.focus_get())

    def addAndExit():
        if add():
            adder.destroy()

    #quickly selects all tests
    def selectAll():
        nonlocal showEntry
        for i in range(len(showEntry)):
            showEntry[i].select()
    #quickly deselects all tests   
    def deselectAll():
        nonlocal showEntry
        for i in range(len(showEntry)):
            showEntry[i].deselect()
    
    #save button
    T.apply(Button(botFrame, text="Add Station", command = addDontExit)).grid(row=0, column=2, padx=5, pady=5)
    #save button
    T.apply(Button(botFrame, text="Add and Close", command = addAndExit)).grid(row=0, column=3, padx=5, pady=5)
    #cancel button
    T.apply(Button(botFrame, text="Close", command=adder.destroy)).grid(row=0, column=4, padx=5, pady=5)
    #Select All button
    T.apply(Button(botFrame, text="Select All", command=selectAll)).grid(row=0, column=0, padx=5, pady=5)
    #Deselect All button
    T.apply(Button(botFrame, text="Deselect All", command=deselectAll)).grid(row=0, column=1, padx=5, pady=5)

    #set min window size
    adder.update_idletasks()
    adder.minsize(width=max(adder.winfo_reqwidth(),300), height=max(adder.winfo_reqheight(),200))

#deleteTest(), deletes a test after being selected from a drop-down menu
def deleteTest():
    global tests

    if len(tests) == 0:
        messagebox.showerror("Power Tools Test Manager", "There are no tests to delete", parent=root.focus_get())
        return
    
    #setup the new menu
    deleter = T.apply(Toplevel())
    deleter.title("Delete Stations")
    deleter.grab_set() #make window modal
    deleter.focus_set()

    optionsFrame = T.apply(Frame(deleter, bd=0))
    optionsFrame.pack(side=TOP)

    botFrame = T.apply(Frame(deleter, bd=0))
    botFrame.pack(side=BOTTOM)
    
    #list of all labels
    l = []
    #response list of IntVar()
    r = []
    #list of all checkbuttons
    c = []
    #draw the set of checkboxes to the screen
    for i in range(len(tests)):
        option = "Station "+str(tests[i].testNum)+": "+tests[i].name
        l.append(T.apply(Label(optionsFrame, text=option)))
        r.append(IntVar())
        r[i].set(0)
        c.append(T.apply(Checkbutton(optionsFrame, text=None, variable=r[i], onvalue=1, offvalue=0, padx=10)))

        l[-1].grid(row=i%10, column=(i//10)*2)
        c[i].grid(row=i%10, column=(i//10)*2+1)

    def delete():
        for ii in range(len(r)-1,-1,-1):
            if bool(r[ii].get()):
                del tests[ii]
        update()
        deleter.destroy()

    #quickly selects all tests
    def selectAll():
        nonlocal c
        for i in range(len(c)):
            c[i].select()

    #quickly deselects all tests   
    def deselectAll():
        nonlocal c
        for i in range(len(c)):
            c[i].deselect()

    #save button
    T.apply(Button(botFrame, text="Delete Stations", command = delete)).grid(row=1, column=2, padx=5, pady=5)
    #cancel button
    T.apply(Button(botFrame, text="Cancel", command=deleter.destroy)).grid(row=1, column=3, padx=5, pady=5)
    #Select All button
    T.apply(Button(botFrame, text="Select All", command=selectAll)).grid(row=1, column=0, padx=5, pady=5)
    #Deselect All button
    T.apply(Button(botFrame, text="Deselect All", command=deselectAll)).grid(row=1, column=1, padx=5, pady=5)

    deleter.update_idletasks()
    deleter.minsize(width=max(deleter.winfo_reqwidth(),300), height=max(deleter.winfo_reqheight(),200))

#changeView, opens a dialog which allows the user to choose which tests are drawn on the screen    
def changeView():
    global tests

    if len(tests) == 0:
        messagebox.showerror("Power Tools Test Manager", "There are no stations to show", parent=root.focus_get())
        return
    
    #setup the new menu
    view = T.apply(Toplevel())
    view.title("Hide/Show Stations")
    view.grab_set() #make window modal
    view.focus_set()

    T.apply(Label(view, text="Deselected stations will be hidden")).pack(side=TOP)

    topFrame = T.apply(LabelFrame(view, bd=0))
    topFrame.pack(side=TOP)

    botFrame = T.apply(LabelFrame(view, bd=0))
    botFrame.pack(side=BOTTOM)

    #dictionary linking option name to internal index
    l = []
    #response list of IntVar()
    r = []
    #list of all checkbuttons
    c = []
    #draw the set of checkboxes to the screen
    for i in range(len(tests)):
        option = "Test "+str(tests[i].testNum)+": "+tests[i].name
        l.append(T.apply(Label(topFrame, text=option)))
        r.append(IntVar())
        r[i].set(tests[i].showTest)
        c.append(T.apply(Checkbutton(topFrame, text=None, variable=r[i], onvalue=1, offvalue=0, padx=10)))

        l[-1].grid(row=i%10, column=(i//10)*2)
        c[-1].grid(row=i%10, column=(i//10)*2+1)
        
        if r[i].get() == 1:
            c[i].select()
        
    #save changes made during the dialog
    def save():
        for i in range(len(r)):
            tests[i].showTest=int(r[i].get())
        update()
        view.destroy()
        
    #quickly selects all tests
    def selectAll():
        nonlocal c
        for i in range(len(c)):
            c[i].select()
    #quickly deselects all tests   
    def deselectAll():
        nonlocal c
        for i in range(len(c)):
            c[i].deselect()
            
    #cancel button
    T.apply(Button(botFrame, text="Cancel", command=view.destroy).grid(row=0, column=3, padx=5, pady=5))
    #save button
    T.apply(Button(botFrame, text="Save", command=save).grid(row=0, column=2, padx=5, pady=5))
    #Select All button
    T.apply(Button(botFrame, text="Select All", command=selectAll).grid(row=0, column=0, padx=5, pady=5))
    #Deselect All button
    T.apply(Button(botFrame, text="Deselect All", command=deselectAll).grid(row=0, column=1, padx=5, pady=5))

    view.update_idletasks()
    view.minsize(width=max(view.winfo_reqwidth(),300), height=max(view.winfo_reqheight(),200))

#writeToFile, allows the user to store current test information in a .txt file of their choice
def writeToFile():
    global tests
    #setup the new menu
    writer = T.apply(Toplevel())
    writer.title("Write To File")
    writer.grab_set() #make window modal
    writer.focus_set()

    T.apply(Label(writer, text="Selected stations will appear on the file")).pack(side=TOP)

    topFrame = T.apply(LabelFrame(writer, bd=0))
    topFrame.pack(side=TOP)

    botFrame = T.apply(LabelFrame(writer, bd=0))
    botFrame.pack(side=BOTTOM)
    
    #dictionary linking option name to internal index
    l = []
    #response list of IntVar()
    r = []
    #list of all checkbuttons
    c = []
    #draw the set of checkboxes to the screen
    for i in range(len(tests)):
        option = "Station "+str(tests[i].testNum)+": "+tests[i].name
        l.append(T.apply(Label(topFrame, text=option)))
        r.append(IntVar())
        r[i].set(tests[i].showTest)
        c.append(T.apply(Checkbutton(topFrame, text=None, variable=r[i], onvalue=1, offvalue=0, padx=10)))

        l[-1].grid(row=i%10, column=(i//10)*2)
        c[-1].grid(row=i%10, column=(i//10)*2+1)
        
        if r[i].get() == 1:
            c[i].select()

    ctVar = BooleanVar()
    commentToggle = T.apply(Checkbutton(writer, text = "Include Comments?", variable = ctVar, onvalue=1, offvalue=0, padx=0))
    commentToggle.pack(side=BOTTOM)
    commentToggle.select()
        
    #writes specified info to file
    def save():
        try:
            #open *.txt file using system dialog
            file = filedialog.asksaveasfile(parent=writer, initialdir = "/", title = "Save As", filetypes = (("Text Files","*.txt"),), defaultextension="*.*")
        except OSError as e: #catch errors relating to opening the file
            messagebox.showerror("Power Tools Test Manager", "Could not open file", parent=root.focus_get())
        else:
            if not file is None:
                file.write("Snap-On Test Manager, Version "+version+"\n")
                file.write(datetime.now().strftime("Data Captured on %m/%d/%Y at %H:%M:%S"))
                for i in range(len(r)):
                    if r[i].get() == 1:
                        if ctVar.get():
                            file.write("\n\nStation "+str(tests[i].testNum)+": "+str(tests[i].toStringPlusComments()))
                        else:
                            file.write("\n\nStation "+str(tests[i].testNum)+": "+str(tests[i].toString()))
                writer.destroy()
        finally:
            if not file is None:
                file.close()
        
    #quickly selects all tests
    def selectAll():
        nonlocal c
        for i in range(len(c)):
            c[i].select()
            
    #quickly deselects all tests   
    def deselectAll():
        nonlocal c
        for i in range(len(c)):
            c[i].deselect()
            
    #cancel button
    T.apply(Button(botFrame, text="Cancel", command=writer.destroy)).grid(row=2, column=3, padx=5, pady=5)
    #save button
    T.apply(Button(botFrame, text="Save As", command=save)).grid(row=2, column=2, padx=5, pady=5)
    #Select All button
    T.apply(Button(botFrame, text="Select All", command=selectAll)).grid(row=2, column=0, padx=5, pady=5)
    #Deselect All button
    T.apply(Button(botFrame, text="Deselect All", command=deselectAll)).grid(row=2, column=1, padx=5, pady=5)

    #set window minimum size
    writer.update_idletasks()
    writer.minsize(width=max(writer.winfo_reqwidth(),300), height=max(writer.winfo_reqheight(),200))

#TODO: split into two separate menu options
#lockDisplay, will make most functions and buttons unusable
#can either be protected with a password, or unprotected
def lockDisplay():
    global locked
    global passLocked
    global password
    #setup the new menu
    locker = T.apply(Toplevel())
    locker.title("Lock Display")
    locker.grab_set() #make window modal
    locker.focus_set()
    
    passEntry = T.apply(Entry(locker))
    passEntry.grid(row=0, column=1, padx=5, pady=5)
    
    def lockWithPass():
        global locked
        global passLocked
        global password
        locked = 1
        passLocked = 1
        password = passEntry.get()
        update()
        locker.destroy()
        
    def lockWithoutPass():
        global locked
        global passLocked
        global password
        locked = 1
        passLocked = 0
        update()
        locker.destroy()
        
    def cancel():
        locker.destroy()

    #drawing locker controls
    T.apply(Label(locker, text="Enter Password:")).grid(row=0, column=0, padx=5, pady=5)   
    T.apply(Button(locker, text = "Lock with Password", command=lockWithPass)).grid(row=1, column=1, padx=5, pady=5)
    T.apply(Button(locker, text = "Lock without Password", command=lockWithoutPass)).grid(row=1, column=0, padx=5, pady=5)
    T.apply(Button(locker, text = "Cancel", command=cancel)).grid(row=1, column=2, padx=5, pady=5)

    #set window minimum size
    locker.update_idletasks()
    locker.minsize(width=max(locker.winfo_reqwidth(),0), height=max(locker.winfo_reqheight(),0))
    
#unlock display, either unlocks the display if it isn't password protected,
#or prompts for a password
def unlockDisplay():
    global locked
    global passLocked
    global password
    if not passLocked:
        locked = 0
        update()
    else:
        #setup the new menu
        unlocker = T.apply(Toplevel(padx=10))
        unlocker.title("Unlock Display")
        unlocker.grab_set() #make window modal
        unlocker.focus_set()
        
        passEntry = T.apply(Entry(unlocker, show="*"))
        passEntry.grid(row=0, column=1, padx=5, pady=5)

        def unlock():
            global locked
            global passLocked
            global password
            if passEntry.get() == password:
                locked = 0
                passLocked = 0
                password = ""
                update()
                unlocker.destroy()
            else:
                messagebox.showerror("Power Tools Test Manager", "Incorrect password", parent=root.focus_get())
            
        def cancel():
            unlocker.destroy()
            return

        #draw unlocker controls
        T.apply(Label(unlocker, text="Enter Password:")).grid(row=0, column=0, padx=5, pady=5)   
        T.apply(Button(unlocker, text = "Unlock", command=unlock)).grid(row=1, column=0, padx=5, pady=5)
        T.apply(Button(unlocker, text = "Cancel", command=cancel)).grid(row=1, column=1, padx=5, pady=5)

        #set window minimum size
        unlocker.update_idletasks()
        unlocker.minsize(width=max(unlocker.winfo_reqwidth(),0), height=max(unlocker.winfo_reqheight(),0))

#addComment, opens a new dialog which will allow the user to write and save comments for each test
def addComment():
    global tests
    
    if len(tests) == 0:
        messagebox.showerror("Power Tools Test Manager", "There are no tests to add a comment to", parent=root.focus_get())
        return
    
    #setup the new menu
    commenter = T.apply(Toplevel())
    commenter.title("Add a Comment")
    commenter.grab_set() #make window modal
    commenter.focus_set()
    
    #dictionary linking option name to internal index
    l = {}
    for i in range(len(tests)):
        l["Test "+str(tests[i].testNum)+": "+tests[i].name] = i
    
    #draw test chooser dropdown
    r=StringVar()
    r.set("Choose a station to add a comment")
    OptionMenu(commenter, r, *l.keys(), command=lambda r: saveButton.config(state=NORMAL)).grid(row=0, column=0, columnspan=2)
    
    commentEntry = Text(commenter, height=15, width=50)
    commentEntry.grid(row=1, column=0, columnspan=2)

    #adds the comment as a tuple to the test object, and closes the window
    def add():
        nonlocal commentEntry
        tests[l[r.get()]].addComment(commentEntry.get('1.0', 'end-1c'))
        commenter.destroy()
                                    
    #save button
    saveButton = Button(commenter, text="Add Comment", command=add, state=DISABLED)
    saveButton.grid(row=5, pady=5)
    #cancel button
    Button(commenter, text="Cancel", command=commenter.destroy).grid(row=5, column=1)

    #set min window size
    commenter.update_idletasks()
    commenter.minsize(width=max(commenter.winfo_reqwidth(),0), height=max(commenter.winfo_reqheight(),0))

#viewComments, opens a new dialog that allows the user to view the comments on a test, or all of the comments from all tests simultaneously  
def viewComments():
    global tests
    global allComments

    if len(tests) == 0:
        messagebox.showerror("Power Tools Test Manager", "There are no stations to view", parent=root.focus_get())
        return
    
    #setup the new menu
    commentViewer = T.apply(Toplevel())
    commentViewer.title("View Comments")
    commentViewer.grab_set() #make window modal
    commentViewer.focus_set()
    
    #dictionary linking option name to internal index
    l = {}
    l["View All"] = -1
    for i in range(len(tests)):
        l["Station "+str(tests[i].testNum)+": "+tests[i].name] = i

    commentLabel = Label(commentViewer, justify=LEFT, anchor = W)
    commentLabel.grid(row=1, column=0, columnspan=2, padx=10, pady=3)

    #draws the comments to the screen
    def displayComments(r):
        nonlocal commentLabel
        if r == "View All":
            string = Test.getAllComments()
        else:
            string = tests[l[r]].getComments()
        if string == "":
            string = "No Comments"
        commentLabel.config(text=string)

    #draw test chooser dropdown
    r=StringVar()
    r.set("View All")
    OptionMenu(commentViewer, r, *l.keys(), command=displayComments).grid(row=0, padx=10, pady=2)
    #draws comments to the screen for the first time
    displayComments(r.get())

    Button(commentViewer, text='Exit', command=commentViewer.destroy).grid(row=0, column=1, padx=5)

    #set min window size
    commentViewer.update_idletasks()
    commentViewer.minsize(width=max(commentViewer.winfo_reqwidth(),260), height=max(commentViewer.winfo_reqheight(),60))
    
#editControls():  presents the user with a window where they can assign labels to the PLC's control coils for each station.
#if given a valid TestNum from an existing station, the window will start with that station selected
def editControls(initialTestNum=0):
    global tests
    if len(tests) == 0:
        messagebox.showerror("Power Tools Test Manager", "There are no stations to edit", parent=root.focus_get())
        return
    #setup the new menu
    editor = T.apply(Toplevel())
    editor.title("Label Controls")
    editor.grab_set() #make window modal
    editor.focus_set()

    topFrame = T.apply(Frame(editor, bd=0))
    topFrame.pack(side=TOP)

    midFrame = T.apply(Frame(editor, bd=0))
    midFrame.pack(side=TOP)

    botFrame = T.apply(Frame(editor, bd=0))
    botFrame.pack(side=BOTTOM)

    if initialTestNum in testIndexDict:
        currentTestIndex=testIndexDict[initialTestNum]
    else:
        currentTestIndex=-1
    
    T.apply(Label(midFrame, text="Enter labels for control buttons")).grid(row=2, column=0, columnspan=8)

    #Building an array of the interactable objects
    numLabel = []
    controlNameEntries = []
    for ii in range(numberOfControls):
        numLabel.append(T.apply(Label(midFrame, text=str(ii+1))))
        controlNameEntries.append(T.apply(Entry(midFrame)))

        numLabel[ii].grid(row=(ii%16+3), column=(int(ii/16)*4))
        controlNameEntries[ii].grid(row=(ii%16+3), column=(int(ii/16)*4+1), padx=5)


    def save():
        for ii in range(numberOfControls):
            tests[currentTestIndex].controlLabels[ii] = controlNameEntries[ii].get()
        #update()

    def apply():
        save()
        messagebox.showinfo("Power Tools Test Manager", "Changes Saved", parent=root.focus_get())
        
    def saveAndClose():
        save()
        editor.destroy()

    
    #select, fills fields with existing info when a test is selected.  If a negative index is passed, the window will be populated with a default selection
    def select(testIndex):
        global tests
        nonlocal currentTestIndex
        currentTestIndex=testIndex
        if (currentTestIndex >= 0):
            dropdown.config(text=("Station "+str(tests[testIndex].testNum)+": "+tests[testIndex].name))
            saveButton.config(state=NORMAL, command=save)
            saveAndCloseButton.config(state=NORMAL)

            for ii in range(numberOfControls):
                controlNameEntries[ii].config(state=NORMAL)
                controlNameEntries[ii].delete(0, END)
                controlNameEntries[ii].insert(0, tests[currentTestIndex].controlLabels[ii])
        else:
            dropdown.config(text=("Choose a station to edit"))
            for ii in range(numberOfControls):
                controlNameEntries[ii].delete(0, END)
                controlNameEntries[ii].config(state=DISABLED)

            saveButton.config(state=DISABLED)
            saveAndCloseButton.config(state=DISABLED)

    #draw test chooser dropdown
    dropdown = T.apply(Menubutton(topFrame, text="[default]", relief=RAISED))
    dropdown.menu = T.apply(Menu(dropdown, tearoff=0))
    dropdown["menu"] = dropdown.menu
    for ii in range(len(tests)):
        dropdown.menu.add_command(label=("Station "+str(tests[ii].testNum)+": "+tests[ii].name), command=lambda x=ii: select(x))
    dropdown.grid()
    
    #save button
    saveButton = T.apply(Button(botFrame, text="Apply Changes", command=apply))
    saveButton.grid(row=0, column=2, padx=5, pady=5)

    #save and close button
    saveAndCloseButton = T.apply(Button(botFrame, text="Save and Close", command=saveAndClose))
    saveAndCloseButton.grid(row=0, column=3, padx=5, pady=5)

    #cancel button
    T.apply(Button(botFrame, text="Cancel", command=editor.destroy)).grid(row=0, column=4, padx=5, pady=5)

    #populate fields for the first time
    select(currentTestIndex)

    #set min window size
    editor.update_idletasks()
    editor.minsize(width=max(editor.winfo_reqwidth(),300), height=max(editor.winfo_reqheight(),200))

#openControls(): This function opens a new child window which will allow the user to see the status of the selected station's
#control coils, and toggle them on or off
#if given a valid TestNum from an existing station, the window will start with that station selected
def openControls(InitialTestNum=0):
    global tests
    global testIndexDict
    if len(tests) == 0:
        messagebox.showerror("Power Tools Test Manager", "There are no stations to control", parent=root.focus_get())
        return
    if ser is None:
        messagebox.showerror("Power Tools Test Manager", "Not connected to a serial port", parent=root.focus_get())
        return
    #setup the new menu
    tl = T.apply(Toplevel())
    tl.title("Label Controls")
    tl.grab_set() #make window modal
    tl.focus_set()

    topFrame = T.apply(Frame(tl, bd=0))
    topFrame.pack(side=TOP)

    midFrame = T.apply(Frame(tl, bd=0))
    midFrame.pack(side=TOP)

    botFrame = T.apply(Frame(tl, bd=0))
    botFrame.pack(side=BOTTOM)

    if InitialTestNum in testIndexDict:
        currentTestIndex=testIndexDict[InitialTestNum]
    else:
        currentTestIndex=-1

    #Building an array of the interactable objects
    numLabel = []
    controlButtons = []
    controlNameLabels = []
    for ii in range(numberOfControls):
        numLabel.append(T.apply(Label(midFrame, text=str(ii+1))))
        controlButtons.append(T.apply(Button(midFrame, width=8)))
        controlNameLabels.append(Label(midFrame, width=10, bg=T.contrastbg, fg=T.contrastfg, font=(T.font, T.fontSize), justify=LEFT))

        numLabel[ii].grid(row=(ii%16+3), column=(int(ii/16)*4))
        controlButtons[ii].grid(row=(ii%16+3), column=(int(ii/16)*4+1))
        controlNameLabels[ii].grid(row=(ii%16+3), column=(int(ii/16)*4+2), padx=5)

    
    def sendCommand(controlIndex, value):
        control(tests[currentTestIndex].testNum, controlIndex, value)
        update(currentTestIndex)


    dropdown = T.apply(Menubutton(topFrame, text="[default]", relief=RAISED))

    #update() is called whenever a new selection is made on the dropdown menu.  It reconfigures the window to reflect what wwas chosen.
    #if update() is passed an invalid index, then it will show a default selection
    def update(testIndex):
        nonlocal currentTestIndex
        currentTestIndex=testIndex
        if (currentTestIndex>=0): 
            dropdown.config(text=("Station "+str(tests[testIndex].testNum)+": "+tests[testIndex].name))
            for ii in range(numberOfControls):
                controlNameLabels[ii].config(text=tests[currentTestIndex].controlLabels[ii])

            retryCount = 0
            done = False
            while not done:  #If the data retrieval is unsuccessful, Try three times before showing that the PLC is offline
                retSuccess, newData = retrieveControlStatus(tests[currentTestIndex].testNum)
                if retSuccess:  #The data retrieval has been successful.  Exit the loop and populate controls with current data
                    done = True
                    for ii in range(numberOfControls):
                        if newData[ii]:         
                            controlButtons[ii].config(text="ON", fg="green", state=NORMAL, command=lambda x=ii: sendCommand(x+1, 0))
                        else:
                            controlButtons[ii].config(text="OFF", fg=T.fg, state=NORMAL, command=lambda x=ii: sendCommand(x+1, 1))
                else:
                    retryCount += 1 #try again

                if retryCount >= 3:  #The data retrieval has been unsuccessful three times.  Exit the loop and show controls offline
                    done = True
                    for ii in range(numberOfControls):
                        controlButtons[ii].config(text="OFFLINE", state=DISABLED, command=None)
        else:
            dropdown.config(text=("Choose a station to control"))
            for ii in range(numberOfControls):
                controlNameLabels[ii].config(text="")
                controlButtons[ii].config(text="", state=DISABLED)

    #close the current window and open the control label editor for the selected test
    def openControlEditor():
        tl.destroy()
        if currentTestIndex>=0:
            editControls(tests[currentTestIndex].testNum)
        else:
            editControls()
        
    #create and assign a menu to the dropdown menubutton.  This menu will allow the user to select which station they want to control.
    dropdown.menu = T.apply(Menu(dropdown, tearoff=0))
    dropdown["menu"] = dropdown.menu
    for ii in range(len(tests)):
        dropdown.menu.add_command(label=("Station "+str(tests[ii].testNum)+": "+tests[ii].name), command=lambda x=ii: update(x))
    dropdown.grid()

    update(currentTestIndex) #populate the screen for the first time

    T.apply(Button(botFrame, text="Edit Labels", command=openControlEditor)).grid(row=0, column=0, padx=5, pady=5)

    #refresh button
    T.apply(Button(botFrame, text="Refresh", command=lambda: update(currentTestIndex))).grid(row=0, column=1, padx=5, pady=5)

    #cancel button
    T.apply(Button(botFrame, text="Close", command=tl.destroy)).grid(row=0, column=3, padx=5, pady=5)
    
    #set min window size
    tl.update_idletasks()
    tl.minsize(width=max(tl.winfo_reqwidth(),300), height=max(tl.winfo_reqheight(),200))


#theme():  This function opens a window that will allow the user to select which colors, font, and text size the program uses
#As new selections are made, this window will be updated to give the user a preview of the theme they have selected
def theme():
    global T
    #initialize a new Theme() object based on the current global Theme
    newTheme=copy.deepcopy(T)

    #setup the new menu
    tl = newTheme.apply(Toplevel())
    tl.title("Configure Appearance")
    tl.grab_set() #make window modal
    tl.focus_set()

    topFrame = newTheme.apply(Frame(tl, bd=0))
    topFrame.pack(side=TOP)

    midFrame = newTheme.apply(Frame(tl, bd=0))
    midFrame.pack(side=TOP)

    botFrame = newTheme.apply(Frame(tl, bd=0))
    botFrame.pack(side=BOTTOM)

    terse = newTheme.apply(Label(topFrame, text="Current Theme: "+newTheme.colorsTitle+", "+newTheme.fontSizeTitle+" "+newTheme.fontTitle))
    terse.pack()

    def refresh():
        newTheme.colorsTitle = colorsVar.get()
        if colorsVar.get() == "Default Gray":
            newTheme.bg="gray95"
            newTheme.fg="black"
            newTheme.contrastbg="white"
            newTheme.contrastfg="black"
            newTheme.selectbg="#00a2ed"
            newTheme.selectfg="white"
            newTheme.contrastselectbg=newTheme.selectbg
            newTheme.contrastselectfg=newTheme.selectfg
        elif colorsVar.get() == "Monochrome":
            newTheme.bg="white"
            newTheme.fg="black"
            newTheme.contrastbg="gray90"
            newTheme.contrastfg="black"
            newTheme.selectbg="gray"
            newTheme.selectfg="black"
            newTheme.contrastselectbg=newTheme.selectbg
            newTheme.contrastselectfg=newTheme.selectfg
        elif colorsVar.get() == "Mint":
            newTheme.bg="#dbeed7"
            newTheme.fg="#3f000f"
            newTheme.contrastbg="white"
            newTheme.contrastfg="#3f000f"
            newTheme.selectbg="#3f000f"
            newTheme.selectfg="white"
            newTheme.contrastselectbg=newTheme.selectbg
            newTheme.contrastselectfg=newTheme.selectfg
        elif colorsVar.get() == "Night":
            newTheme.bg="#1d2951"
            newTheme.fg="white"
            newTheme.contrastbg="slategray"
            newTheme.contrastfg="white"
            newTheme.selectbg="white"
            newTheme.selectfg="slategray"
            newTheme.contrastselectbg=newTheme.selectbg
            newTheme.contrastselectfg=newTheme.selectfg
        elif colorsVar.get() == "Two-Tone":
            newTheme.bg="black"
            newTheme.fg="white"
            newTheme.contrastbg="white"
            newTheme.contrastfg="black"
            newTheme.selectbg="white"
            newTheme.selectfg="black"
            newTheme.contrastselectbg="black"
            newTheme.contrastselectfg="white"

        newTheme.fontSizeTitle = fontSizeVar.get()
        if newTheme.fontSizeTitle == "Small":
            newTheme.fontSize = 7
        elif newTheme.fontSizeTitle == "Medium":
            newTheme.fontSize = 9
        elif newTheme.fontSizeTitle == "Large":
            newTheme.fontSize = 11
        elif newTheme.fontSizeTitle == "Extra Large":
            newTheme.fontSize = 13

        newTheme.fontTitle = fontVar.get()
        if newTheme.fontTitle == "Sans-Serif":
            newTheme.font = "Helvetica"
        elif newTheme.fontTitle == "Serif":
            newTheme.font = "Times"
        elif newTheme.fontTitle == "Monospaced":
            newTheme.font = "Courier"

        newTheme.apply(tl)
        newTheme.apply(topFrame)
        newTheme.apply(midFrame)
        newTheme.apply(botFrame)
        newTheme.apply(terse)
        terse.config(text="Current Theme: "+newTheme.colorsTitle+", "+newTheme.fontSizeTitle+" "+newTheme.fontTitle)
        newTheme.apply([colorsHeader, fontSizeHeader, fontHeader, saveButton, cancelButton])
        for oo in r:
            newTheme.apply(oo)
        for oo in l:
            newTheme.apply(oo)

    r = [] #list of all radiobuttons
    l = [] #list of all accompanying labels

    colorsVar = StringVar(value=newTheme.colorsTitle)
    colorsOptions = ["Default Gray", "Monochrome", "Mint", "Night", "Two-Tone"]
    colorsHeader = newTheme.apply(Label(midFrame, text="Color theme:"))
    colorsHeader.grid(row=0, column=0, columnspan=2)

    for ii in range(len(colorsOptions)):
        r.append(newTheme.apply(Radiobutton(midFrame, variable=colorsVar, value=colorsOptions[ii], command=refresh)))
        l.append(newTheme.apply(Label(midFrame, text=colorsOptions[ii])))

        r[-1].grid(row=ii+1, column=0)
        l[-1].grid(row=ii+1, column=1)

    fontSizeVar = StringVar(value=newTheme.fontSizeTitle)
    fontSizeOptions = ["Small", "Medium", "Large", "Extra Large"]
    fontSizeHeader = newTheme.apply(Label(midFrame, text="Text Size:"))
    fontSizeHeader.grid(row=0, column=2, columnspan=2)

    for ii in range(len(fontSizeOptions)):
        r.append(newTheme.apply(Radiobutton(midFrame, variable=fontSizeVar, value=fontSizeOptions[ii], command=refresh)))
        l.append(newTheme.apply(Label(midFrame, text=fontSizeOptions[ii])))

        r[-1].grid(row=ii+1, column=2)
        l[-1].grid(row=ii+1, column=3)

    fontVar = StringVar(value=newTheme.fontTitle)
    fontOptions = ["Sans-Serif", "Serif", "Monospaced"]
    fontHeader = newTheme.apply(Label(midFrame, text="Font Family:"))
    fontHeader.grid(row=len(fontSizeOptions)+1, column=2, columnspan=2)

    for ii in range(len(fontOptions)):
        r.append(newTheme.apply(Radiobutton(midFrame, variable=fontVar, value=fontOptions[ii], command=refresh)))
        l.append(newTheme.apply(Label(midFrame, text=fontOptions[ii])))

        r[-1].grid(row=ii+len(fontSizeOptions)+2, column=2)
        l[-1].grid(row=ii+len(fontSizeOptions)+2, column=3)


    def save():
        global T
        T = newTheme
        update()
        tl.destroy()

    #save button
    saveButton = Button(botFrame, text="Save", command=save)
    saveButton.grid(row=0, column=0, padx=5, pady=5)

    #cancel button
    cancelButton = Button(botFrame, text="Cancel", command=tl.destroy)
    cancelButton.grid(row=0, column=3, padx=5, pady=5)

    #set min window size
    tl.update_idletasks()
    tl.minsize(width=max(tl.winfo_reqwidth(),300), height=max(tl.winfo_reqheight(),200))

#declaring dataFrame, which will hold all test widgets
dataFrame = LabelFrame(root, bd=0)
dataFrame.pack(side=TOP)

#Version label in the far right, on a window-spanning relief bar
ver = Frame(root, bd=1, relief=SUNKEN)
verText = Label(ver, text="version " + version)
verText.pack(side=RIGHT)
ver.pack(side=BOTTOM, fill='x')

botControl = Frame(root, bd=0)
botControl.pack(side=BOTTOM, pady=2)

pauseAllButton = Button(botControl, text="Pause All Tests", command=pauseAll)
pauseAllButton.grid(row=0, column=0)
resumeAllButton = Button(botControl, text="Resume All Tests", command=resumeAll)
resumeAllButton.grid(row=0, column=1)

menubar = Menu(root)

fileMenu = Menu(menubar, tearoff=0)
fileMenu.add_command(label="Save Session", command=saveSession)
fileMenu.add_command(label="Open Session", command=openSession)
fileMenu.add_command(label="Connect to Port", command=connect)
fileMenu.add_command(label="Write to File", command=writeToFile)
fileMenu.add_command(label="Exit", command=exitProgram)
menubar.add_cascade(label="File", menu=fileMenu)

functionsMenu = Menu(menubar, tearoff=0)
functionsMenu.add_command(label="Edit Stations", command=editTests)
functionsMenu.add_command(label="Add Station", command=addTest)
functionsMenu.add_command(label="Delete Station", command=deleteTest)
functionsMenu.add_command(label="Label Controls", command=editControls)
menubar.add_cascade(label="Edit", menu=functionsMenu)

viewMenu = Menu(menubar, tearoff=0)
viewMenu.add_command(label="Hide/Show Stations", command=changeView)
viewMenu.add_command(label="Theme", command=theme)
viewMenu.add_command(label="Lock Display", command=lockDisplay)
menubar.add_cascade(label="View", menu=viewMenu)

controlsMenu = Menu(menubar, tearoff=0)
controlsMenu.add_command(label="Pause/Resume")
controlsMenu.add_command(label="More Controls", command=openControls)
menubar.add_cascade(label="Control Tests", menu=controlsMenu)

#TODO: disable these functions, they're unsupported in this version
testCommentsMenu = Menu(menubar, tearoff=0)
testCommentsMenu.add_command(label="Add a Comment", command=addComment)
testCommentsMenu.add_command(label="View Comments", command=viewComments)
menubar.add_cascade(label="Test Comments", menu=testCommentsMenu)

root.config(menu=menubar)

#Draws the screen with the current parameters
def update():
    global root
    global dataFrame
    global testIndexDict
    #apply appearance theme to main window
    T.apply([root, dataFrame, ver, botControl, pauseAllButton, resumeAllButton])
    verText.config(bg=T.bg, fg=T.fg, font=(T.font, T.fontSize-2, "italic"))

    #forget all children in anticipation of reordering and redrawing them
    for child in dataFrame.winfo_children():
        child.grid_forget()
    placer = 0
    tests.sort(key=lambda x: x.testNum) #sort tests by test number/slave address
    testIndexDict = {} #reset dictonary
    for i in range(len(tests)):
        testIndexDict[tests[i].testNum] = i
        
        if tests[i].showTest:
            tests[i].draw(int(placer/10)+1, placer%10)
            placer += 1
    
    
    if not locked:
        fileMenu.entryconfig(0, label="Save Session", command=saveSession, state=NORMAL)
        fileMenu.entryconfig(1, label="Open Session", command=openSession, state=NORMAL)
        fileMenu.entryconfig(2, label="Connect to Port", command=connect, state=NORMAL)
        fileMenu.entryconfig(3, label="Write to File", command=writeToFile, state=NORMAL)
        fileMenu.entryconfig(4, label="Exit", command=exitProgram, state=NORMAL)
        
        functionsMenu.entryconfig(0, label="Edit Stations", command=editTests, state=NORMAL)
        functionsMenu.entryconfig(1, label="Add Station", command=addTest, state=NORMAL)
        functionsMenu.entryconfig(2, label="Delete Station", command=deleteTest, state=NORMAL)
        functionsMenu.entryconfig(3, label="Label Controls", command=editControls, state=NORMAL)
        
        viewMenu.entryconfig(0, label="Hide/Show Stations", command=changeView, state=NORMAL)
        viewMenu.entryconfig(1, label="Theme", command=theme, state=NORMAL)
        viewMenu.entryconfig(2, label="Lock Display", command=lockDisplay, state=NORMAL)
        
        controlsMenu.entryconfig(0, label="Pause/Resume", state=NORMAL) #TODO
        controlsMenu.entryconfig(1, label="More Controls", command=openControls, state=NORMAL)
        
        testCommentsMenu.entryconfig(0, label="Add a Comment", command=addComment, state=NORMAL)
        testCommentsMenu.entryconfig(1, label="View Comments", command=viewComments, state=NORMAL)
        
    else:
        fileMenu.entryconfig(0, label="Save Session", command=saveSession)
        fileMenu.entryconfig(1, label="Open Session", state=DISABLED)
        fileMenu.entryconfig(2, label="Connect to Port", state=DISABLED)
        fileMenu.entryconfig(3, label="Write to File", command=writeToFile)
        fileMenu.entryconfig(4, label="Exit", command=exitProgram)
        
        functionsMenu.entryconfig(0, label="Edit Stations", state=DISABLED)
        functionsMenu.entryconfig(1, label="Add Station", state=DISABLED)
        functionsMenu.entryconfig(2, label="Delete Station", state=DISABLED)
        functionsMenu.entryconfig(3, label="Label Controls", state=DISABLED)
        
        viewMenu.entryconfig(0, label="Hide/Show Stations", state=DISABLED)
        viewMenu.entryconfig(1, label="Theme", command=theme)
        viewMenu.entryconfig(2, label="Unlock Display", command=unlockDisplay)
        
        controlsMenu.entryconfig(0, label="Pause/Resume", state=DISABLED)
        controlsMenu.entryconfig(1, label="More Controls", state=DISABLED)
        
        testCommentsMenu.entryconfig(0, label="Add a Comment", command=addComment)
        testCommentsMenu.entryconfig(1, label="View Comments", command=viewComments)
        

    T.apply([fileMenu, functionsMenu, viewMenu, controlsMenu, testCommentsMenu])
    
    if locked or len(tests) == 0:
        pauseAllButton.config(state=DISABLED)
        resumeAllButton.config(state=DISABLED)
    else:
        pauseAllButton.config(state=NORMAL)
        resumeAllButton.config(state=NORMAL)

    root.update_idletasks()
    root.geometry(str(max(root.winfo_reqwidth(),400))+'x'+str(max(root.winfo_reqheight(),300)))
    root.minsize(width=max(root.winfo_reqwidth(),400), height=max(root.winfo_reqheight(),300))

           
#draw screen for the first time
update()



#when given a binary message as a list of ints, returns a 16 bit MODBUS CRC as a list of ints
def getCRC(msg):
    CRC = 0xFFFF
    
    for bx in msg: 
        CRC ^= bx
        for ii in range(8):
            LSB = CRC & 0x0001 #extract LSB
            CRC >>= 1 #right shift
            if LSB == 1:
                CRC ^= 0xA001 #xor per generation procedure

    return[(CRC & 0x00FF), (CRC >> 8)] # return CRC as a list of two ints, swapped per generation procedure


#retrieve, accepts a MODBUS slave ID to poll
#composes and sends a MODBUS command which will instruct the PLC to return its data registers DF101-132
#reads the returned message and decodes to retrieve data
#returns a 2-tuple containing a boolean and an array containing the new data
#returns true is the data message is acceptable, returns false if it detects an error or an empty message
def retrieve(slID):
    msg = [
        slID, #slave ID
        0x03, #MODBUS Command (Read Holding Registers)
        0x70, #Starting Address (DF101)
        0xC8,
        (numberOfData*2) // 0x100, #No. of points (64) (32 Floats)
        (numberOfData*2) % 0x100
    ]
    msg = msg + getCRC(msg) #append CRC
    ser.write(bytes(msg))

    b = ser.read(size=numberOfData*4+5)

    #parse binary response
    if b == b'':
        #print("Error, nothing returned, "+str(slID))
        return False, None
    
    if not len(b) == numberOfData*4+5: #133 bytes, 128 bytes for data (32x4 bytes/float) + 5
        #print("Error, incorrect length, length was "+str(len(b)))
        return False, None

    if not b[0] == slID: #slave ID
        #print("Error, wrong slID, slID was "+str(b[0])+", was polling "+str(slID))
        return False, None

    if not b[1] == 0x03: #MODBUS Command (Read Holding Registers)
        #print("Error, wrong command returned, command was "+str(b[1]))
        return False, None

    crc = getCRC(b[0:-2])
    if not [b[-2], b[-1]] == crc:
        #print("Error, wrong CRC returned, CRC was "+hex(b[131])+hex(b[132])+", calculated "+hex(crc[0])+hex(crc[1]))
        return False, None

    dataVals = []
    for ii in range(numberOfData):
        dataVals.append(unpack('>f',bytes([b[ii*4+5], b[ii*4+6], b[ii*4+3], b[ii*4+4]]))[0]) #ammend byteswapping, and convert from IEEE-754 to python float with unpack()
        
    return True, dataVals

#retrieveControlStatus, accepts a MODBUS slave ID to poll
#composes and sends a MODBUS command which will instruct the PLC to return its control coils C101-132
#reads the returned message and decodes to retrieve data
#returns a 2-tuple containing a boolean and an array containing the new data
#returns true is the data message is acceptable, returns false if it detects an error or an empty message
def retrieveControlStatus(slID):
    msg = [
        slID, #slave ID
        0x01, #MODBUS Command (Read Coil Status)
        0x40, #Starting Address (C101)
        0x64,
        numberOfControls // 0x100, #No. of points (32) (32 Coils)
        numberOfControls % 0x100
    ]
    msg = msg + getCRC(msg) #append CRC
    ser.write(bytes(msg))

    b = ser.read(size=-(-numberOfControls//8)+5) #upside down floor division does ceiling division

    #parse binary response
    if b == b'':
        #print("Error, nothing returned, "+str(slID))
        return False, None
    
    if not len(b) == -(-numberOfControls//8)+5: #9 bytes, 4 bytes for data (32/8 coils/byte) + 5
        #print("Error, incorrect length, length was "+str(len(b)))
        return False, None

    if not b[0] == slID: #slave ID
        #print("Error, wrong slID, slID was "+str(b[0])+", was polling "+str(slID))
        return False, None

    if not b[1] == 0x01: #MODBUS Command (Read Coil Status)
        #print("Error, wrong command returned, command was "+str(b[1]))
        return False, None

    crc = getCRC(b[0:-2])
    if not [b[-2], b[-1]] == crc:
        #print("Error, wrong CRC returned, CRC was "+hex(b[131])+hex(b[132])+", calculated "+hex(crc[0])+hex(crc[1]))
        return False, None

    dataVals = []
    for ii in range(numberOfControls):
        dataVals.append((b[int(ii/8)+3]) & (0x1 << ii%8)) #ammend bit ordering, and convert to a list of booleans
        
    return True, dataVals

#checkIfPaused(), accepts a MODBUS slave ID to poll.
#composes a MODBUS command which will instruct the PLC to return the state of it's C50 register.
#then parses the returned message, returning a 2-tuple
#first value will return True if the response is acceptable, returns False if it detects an erroneous or empty message
#second value returns True if the PLC is paused, False if not Paused, None otherwise
#may raise SerialException
def checkIfPaused(slID):
    msg = [
        slID, #slave ID
        0x01, #MODBUS Command (Read Coil Status)
        0x40, #Starting Address (C50) (Pause)
        0x31,
        0x00, #No. of points (1) (1 Coil)
        0x01
    ]
    msg = msg + getCRC(msg) #append CRC
    ser.write(bytes(msg))

    b = ser.read(size=6)

    #parse binary response
    if b == b'':
        #print("Error, nothing returned, address was"+str(slID))
        return False, None

    if not len(b) == 6: #6 bytes, 1 bytes for data + 5
        #print("Error, incorrect length, length was "+str(len(b)))
        return False, None

    if not b[0] == slID: #slave ID
        #print("Error, wrong slID, slID was "+str(b[0])+", was polling "+str(slID))
        return False, None

    if not b[1] == 0x01: #MODBUS Command (Read Coil Status)
        #print("Error, wrong command returned, command was "+hex(b[1])+", expected 0x01")
        return False, None

    if not b[2] == 0x01: #Num data bytes (1)
        #print("Error, incorrect byte count reported, "+str(b[2])+", expected 1")
        return False, None

    crc = getCRC(b[0:4])
    if not [b[4], b[5]] == crc:
        #print("Error, wrong CRC returned, CRC was "+hex(b[4])+hex(b[5])+", calculated "+hex(crc[0])+hex(crc[1]))
        return False, None

    if b[3] == 0x01: #C50 is set, test is paused
        return True, True
    elif b[3] == 0x00: #C50 is reset, test is not paused
        return True, False
    else:
        #print("Error, value recieved was neither true or false, recieved "+hex(b[3]))
        return False, None
    
#checkIfRunning(), accepts a MODBUS slave ID to poll.
#composes a MODBUS command which will instruct the PLC to return the state of it's SC11 register.
#then parses the returned message, returning a 2-tuple
#first value will return True if the response is acceptable, returns False if it detects an erroneous or empty message
#second value returns True if the PLC is in run mode, False if in stop mode, None otherwise
#may raise SerialException
def checkIfRunning(slID):
    msg = [
        slID, #slave ID
        0x02, #MODBUS Command (Read Input Status)
        0xF0, #Starting Address (SC11) (_PLC_Mode)
        0x0A,
        0x00, #No. of points (1) (1 Coils)
        0x01
    ]
    msg = msg + getCRC(msg) #append CRC
    ser.write(bytes(msg))

    b = ser.read(size=6)

    #parse binary response
    if b == b'':
        #print("Error, nothing returned, address was"+str(slID))
        return False, None

    if not len(b) == 6: #6 bytes, 1 bytes for data + 5
        #print("Error, incorrect length, length was "+str(len(b)))
        return False, None

    if not b[0] == slID: #slave ID
        #print("Error, wrong slID, slID was "+str(b[0])+", was polling "+str(slID))
        return False, None

    if not b[1] == 0x02: #MODBUS Command (Read Input Status)
        #print("Error, wrong command returned, command was "+hex(b[1])+", expected 0x01")
        return False, None

    if not b[2] == 0x01: #Num data bytes (1)
        #print("Error, incorrect byte count reported, "+str(b[2])+", expected 1")
        return False, None

    crc = getCRC(b[0:4])
    if not [b[4], b[5]] == crc:
        #print("Error, wrong CRC returned, CRC was "+hex(b[4])+hex(b[5])+", calculated "+hex(crc[0])+hex(crc[1]))
        return False, None

    if b[3] == 0x01: #SC11 is set, PLC is in Run mode
        return True, True
    elif b[3] == 0x00: #SC11 is reset, PLC is in Stop mode
        return True, False
    else:
        #print("Error, value recieved was neither true or false, recieved "+hex(b[3]))
        return False, None

#counter for retrying message receptions
retryCount = 0
#couter keeping track of current test INDEX in tests array
currTestPoll = 0
              
#main loop for recieving checking up and recieving from PLCs and continuing the GUI
#if the loop encounters an error while parsing three times in a row, it will mark the test as offline and proceed to poll the next test
while(running): #root.state() == 'normal'):
    if not ser is None: #If connected to a serial port 
        if currTestPoll < len(tests) and tests[currTestPoll].testNum > 0 and tests[currTestPoll].testNum <= 247:
            #ensure that the index is not out of bounds, which could possibly be caused by deleting tests, and check if test is associated with a valid slave ID before retrieving
            #print(f'{tests[currTestPoll].testNum:03d}')
            try:
                retSuccess, newData = retrieve(tests[currTestPoll].testNum) #send requests
                pauseSuccess, isPaused = checkIfPaused(tests[currTestPoll].testNum)
                runSuccess, isRunning = checkIfRunning(tests[currTestPoll].testNum)

                if retSuccess and pauseSuccess and runSuccess: #ensure that all requests were successful
                    #update test status based on results
                    if not isRunning:
                        tests[currTestPoll].setStopped()
                    elif isPaused:
                        tests[currTestPoll].setPaused()
                    else:
                        tests[currTestPoll].setNormal()
                        
                    tests[currTestPoll].set(newData)
                    currTestPoll += 1 #Increment to next test in list
                    retryCount = 0 #Reset retry counter
                else: 
                    retryCount += 1
            except serial.serialutil.SerialException: #handle case where serial port is unexpectedly disconnected during commuication
                ser.close()
                ser = None
                currTestPoll = 0
                retryCount = 0
                for oo in tests:
                    oo.setOffline()
                messagebox.showerror("Power Tools Test Manager", "Serial Port Disconnected", parent=root.focus_get())
        if retryCount >= 3: #If the same test has been polled three times, with no response or bad responses, set the test as offline and continue
            if currTestPoll < len(tests):
                tests[currTestPoll].setOffline()
            currTestPoll += 1
            retryCount = 0
        if currTestPoll >= len(tests): #reset poll index to zero
            currTestPoll = 0
    root.update() #maintain root window
    
root.destroy()
if not ser is None:
    ser.close()
#root.mainloop()
