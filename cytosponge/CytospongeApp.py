import cytosponge
import wx
import threading
import time
import numpy as np
import logging
import sys

class CytospongePanel(wx.Panel):
	initialBMPX = 600
	initialBMPY = 400
	initialPanelX = 1150
	initialPanelY = 510
	def __init__(self, parent, COMport):
		wx.Panel.__init__(self, parent)
		self.parent = parent
		# Initialize logging
		self.logger = logging.getLogger('cytosponge_training')
		self.logger.setLevel(logging.DEBUG)
		logfilehandler = logging.FileHandler('cytosponge.log')
		logfilehandler.setLevel(logging.DEBUG)
		consolehandler = logging.StreamHandler()
		consolehandler.setLevel(logging.ERROR)
		formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
		logfilehandler.setFormatter(formatter)
		consolehandler.setFormatter(formatter)
		self.logger.addHandler(logfilehandler)
		self.logger.addHandler(consolehandler)
		self.logger.info("Program started")
		# Initialize event signalling
		try:
			self.EventService = cytosponge.EventService(self)
			self.logger.info("Event service initialized")
		except Exception as e:
			self.logger.error(cytosponge.format_error_message(e))
			sys.exit()

		# Initialize serial communications service
		# try:
		# 	self.serialCommsService = cytosponge.SerialCommunicationService(COMport, self.EventService)
		# 	self.logger.info("Serial communications initialized")
		# except Exception as e:
		# 	self.logger.error(cytosponge.format_error_message(e))
		# 	sys.exit()

		# Initialize data analysis and manipulation
		try:
			self.DataService = cytosponge.DataService()
			self.logger.info("Data service initialized")
		except Exception as e:
			self.logger.error(cytosponge.format_error_message(e))
			sys.exit()

		try:
			self.CommandService = cytosponge.CommandService()
			self.logger.info("Command service initialized")
		except Exception as e:
			self.logger.error(cytosponge.format_error_message(e))
			sys.exit()

		# Create sizers for layout
		self.mainSizer = wx.BoxSizer(wx.HORIZONTAL)
		self.sidebarSizer = wx.BoxSizer(wx.VERTICAL)
		self.controlSizer = wx.StaticBoxSizer(wx.VERTICAL,self,label="Controls")
		self.loginSizer = wx.StaticBoxSizer(wx.HORIZONTAL, self, label="Login")
		self.startStopSizer = wx.BoxSizer(wx.HORIZONTAL)
		self.graphDisplaySizer = wx.BoxSizer(wx.HORIZONTAL)

		# Login Widgets
		self.loggedIn = False
		self.IDField = wx.TextCtrl(self, value=self.DataService.currentUserRecordID)
		self.loginButton = wx.Button(self, label="Set User")
		self.Bind(wx.EVT_BUTTON, self.OnClickLogin, self.loginButton)

		self.loginSizer.Add(self.IDField, 0, wx.ALIGN_LEFT|wx.ALL, 10)
		self.loginSizer.Add(self.loginButton, 0, wx.ALIGN_RIGHT|wx.ALL, 10)

		# Control Widgets
		self.startButton = wx.Button(self, label="Start")
		self.stopButton = wx.Button(self, label="Stop")
		self.manualParameterControl = wx.CheckBox(self, label= "Set Parameters")
		self.oesophagusLengthControl = wx.Slider(self, value=self.DataService.oesophagusLength, minValue=10, maxValue=50, style = wx.SL_LABELS)
		self.testCaseSelection = wx.ComboBox(self, value=self.DataService.testCase, choices = ["Normal", "Seizing", "Panic"], style=wx.CB_READONLY)

		self.Bind(wx.EVT_BUTTON, self.OnClickStart, self.startButton)
		self.Bind(wx.EVT_BUTTON, self.OnClickStop, self.stopButton)		
		self.Bind(wx.EVT_CHECKBOX, self.OnCheckParams, self.manualParameterControl)
		self.Bind(wx.EVT_SCROLL_CHANGED, self.OnOLSlide, self.oesophagusLengthControl)
		self.Bind(wx.EVT_COMBOBOX, self.OnSelectTest, self.testCaseSelection)
		# Manual Control disabled by default
		self.oesophagusLengthControl.Disable()
		self.testCaseSelection.Disable()

		# Relative Layout of controls
		self.startStopSizer.Add(self.startButton, 0, wx.CENTER|wx.ALL|wx.ALIGN_CENTER, 10)
		self.startStopSizer.Add(self.stopButton, 0, wx.CENTER|wx.ALL|wx.ALIGN_CENTER, 10)
		self.controlSizer.Add(self.startStopSizer, 0, wx.ALIGN_TOP, 10)
		staticBox1 = wx.StaticBoxSizer(wx.HORIZONTAL, self, label="Oesophagus Length (cm)")
		staticBox2 = wx.StaticBoxSizer(wx.HORIZONTAL, self, label="Test Case")
		staticBox1.Add(self.oesophagusLengthControl, 1, wx.CENTER|wx.EXPAND|wx.FIXED_MINSIZE, 10)
		staticBox2.Add(self.testCaseSelection, 0, wx.CENTER|wx.ALL|wx.ALIGN_CENTER|wx.EXPAND, 10)
		self.controlSizer.Add(self.manualParameterControl, 0, wx.CENTER|wx.ALL|wx.EXPAND, 10)
		self.controlSizer.Add(staticBox1, 0, wx.CENTER|wx.ALL|wx.EXPAND, 10)
		self.controlSizer.Add(staticBox2, 0, wx.CENTER|wx.ALL|wx.EXPAND, 10)

		# Initialize plot bitmap placeholders
		self.graphDisplay = wx.StaticBitmap(self, id=-1, size=(CytospongePanel.initialBMPX,CytospongePanel.initialBMPY))
		self.graphsReady = False

		self.graphs = [wx.Bitmap(), wx.Bitmap()] # 0 is velocity, 1 is tension
		self.currGraph = 0
		self.prevButton = wx.Button(self, label="Prev")
		self.nextButton = wx.Button(self,label="Next")
		self.Bind(wx.EVT_BUTTON, self.ToggleGraph, self.prevButton)
		self.Bind(wx.EVT_BUTTON, self.ToggleGraph, self.nextButton)
		
		# Place graph display widgets
		self.graphDisplaySizer.Add(self.prevButton, 0, wx.CENTER|wx.ALL|wx.ALIGN_CENTER, 10)
		self.graphDisplaySizer.Add(self.graphDisplay, 1, wx.EXPAND|wx.ALL, 10)
		self.graphDisplaySizer.Add(self.nextButton, 0, wx.CENTER|wx.ALL|wx.ALIGN_CENTER, 10)
		self.graphDisplaySizer.Hide(0)
		self.graphDisplaySizer.Hide(2)
		 
		# Bind software events
		self.Bind(self.EventService.EVT_TRAINING_FINISHED, self.OnTrainingFinished)


		# Map layout
		self.sidebarSizer.Add(self.loginSizer, 0, wx.ALIGN_TOP|wx.ALL|wx.FIXED_MINSIZE, 10)
		self.sidebarSizer.Add(self.controlSizer, 0, wx.ALIGN_TOP|wx.ALL|wx.FIXED_MINSIZE, 10)
		self.mainSizer.Add(self.sidebarSizer, 0, wx.ALIGN_TOP|wx.ALL|wx.FIXED_MINSIZE, 10)
		self.mainSizer.Add(self.graphDisplaySizer, 0, wx.ALIGN_TOP|wx.ALL, 10)
		self.SetSizer(self.mainSizer)

	def OnClickLogin(self, event):
		recordID = self.IDField.GetLineText(0)
		if recordID is not None and recordID != "" and recordID != self.DataService.currentUserRecordID:
			self.loggedIn = self.DataService.login(recordID)
		if recordID == "" or not self.loggedIn:
			self.logger.debug("Login attempt with invalid ID. Signup prompted")
			popupWindow = SignUpWindow(self, recordID)
			popupWindow.Show()
		else:
			self.parent.SetStatusText("Login Successful")
			self.logger.debug("Login successful")


	def OnClickStart(self, event):
		if not self.EventService.receivingData.isSet():
			self.DataService.updateParameters(self.oesophagusLengthControl.GetValue(), self.testCaseSelection.GetValue())
			self.logger.info("Test started with parameters: OL - " + str(self.DataService.oesophagusLength) + ", TC - " + str(self.DataService.testCase))
			# # ACTUAL CODE
			# self.serialCommsService.writeData(CytospongeApp.startSignal)
			# self.serialCommsService.listenForDataOnEvent(self.EventService.receivingData)
			# self.EventService.setReceivingData()
			# self.parent.SetStatusText("Training in progress")

		#No arduino test code
		self.parent.SetStatusText("Training in progress")
		t = threading.Timer(2.0, self.setTrainingFinished)
		t.start()


	def OnClickStop(self, event):
		if self.EventService.receivingData.isSet():
			self.serialCommsService.writeData(CytospongeApp.endSignal)
			self.logger.warn("Test stopped manually")
			# Collect incomplete data
			self.serialCommsService.collectEndData()

	def OnTrainingFinished(self, event):
		
		#ACTUAL CODE
		#self.serialCommsService.dataListeningThread.join()
		self.parent.SetStatusText("Training finished")
		# self.DataService.analyzeData(self.serialCommsService.getIncomingData())
		self.DataService.analyzeData()
		if self.loggedIn:
			uploadThread = threading.Thread(name="upload-data", target = self.DataService.uploadData(), args=(None))
			uploadThread.start()
		self.loadGraphImages()
		self.displayGraphs()

	def OnCheckParams(self, event):
		self.DataService.manualParameterControl = self.manualParameterControl.GetValue()
		if self.DataService.manualParameterControl:
			self.oesophagusLengthControl.Enable()
			self.testCaseSelection.Enable()
		else:
			self.oesophagusLengthControl.Disable()
			self.testCaseSelection.Disable()

	def OnOLSlide(self, event):
		self.DataService.updateOL = True

	def OnSelectTest(self, event):
		self.DataService.updateTestCase = True


	def ToggleGraph(self, event):
		self.currGraph = 1 - self.currGraph
		self.graphDisplay.SetBitmap(self.graphs[self.currGraph])
		self.parent.fSizer.Layout()

	def setTrainingFinished(self):
		self.EventService.postTrainingFinished()

	def loadGraphImages(self):
		self.velocityIm = wx.Image(self.DataService.velocityGraph)
		self.tensionIm = wx.Image(self.DataService.tensionGraph)

	def displayGraphs(self):
		self.graphs[0] = wx.Bitmap(self.velocityIm.Rescale(CytospongePanel.initialBMPX,CytospongePanel.initialBMPY, quality=wx.IMAGE_QUALITY_HIGH))
		self.graphs[1] = wx.Bitmap(self.tensionIm.Rescale(CytospongePanel.initialBMPX,CytospongePanel.initialBMPY, quality=wx.IMAGE_QUALITY_HIGH))

		self.graphDisplaySizer.Show(0)
		self.graphDisplaySizer.Show(2)
		
		self.currGraph = 0
		self.graphDisplay.SetBitmap(self.graphs[self.currGraph])
		self.parent.SetMinSize((850,375))
		self.parent.fSizer.Layout()
		self.parent.SetSize((CytospongePanel.initialPanelX,CytospongePanel.initialPanelY))
		self.graphsReady = True

	def ResizeGraph(self, event):
		event.Skip()
		print(self.parent.GetSize())
		if self.graphsReady:
			newPanelX, newPanelY = self.parent.GetSize()
			newBMPX = CytospongePanel.initialBMPX + (newPanelX-CytospongePanel.initialPanelX)
			newBMPY = CytospongePanel.initialBMPY + (newPanelY-CytospongePanel.initialPanelY)
			self.graphs[0] = wx.Bitmap(self.velocityIm.Rescale(newBMPX,newBMPY, quality=wx.IMAGE_QUALITY_HIGH))
			self.graphs[1] = wx.Bitmap(self.tensionIm.Rescale(newBMPX, newBMPY, quality=wx.IMAGE_QUALITY_HIGH))
			self.graphDisplay.SetBitmap(self.graphs[self.currGraph])

	def signUp(self, firstName, surname, idNumber):
		signUpSuccessful = self.DataService.signUp(firstName, surname, idNumber)
		if signUpSuccessful:
			self.parent.SetStatusText("Signup successful!")
			self.IDField.SetValue(self.DataService.currentUserRecordID)
		else:
			self.parent.SetStatusText("User signup failed!")
		return signUpSuccessful

class CytospongeApp(wx.Frame):

	testSignal = "99"
	startSignal = "1"
	endSignal = "-1"
	

	def __init__(self, COMport, *args, **kw):
		#Initialize wx App
		self.uiApp = wx.App(False)

		# Initialize superclass
		super(CytospongeApp, self).__init__(title="Cytosponge Training", *args, **kw)
		self.SetMinSize((265,485))
		#Create a panel
		self.panel = CytospongePanel(self, COMport)

		#fit Sizer
		self.fSizer = wx.BoxSizer(wx.VERTICAL)
		self.fSizer.Add(self.panel, 1, wx.EXPAND)
		self.SetSizer(self.fSizer)

		# Set events
		self.Bind(wx.EVT_CLOSE, self.terminateApp, self)

		#Create a status bar
		self.CreateStatusBar()
		self.SetStatusText("Welcome to Cytosponge Training! Start a Test!")
		time.sleep(2)
		self.runApp()

	def terminateApp(self, event):
		# self.panel.serialCommsService.writeData(CytospongeApp.endSignal)
		# self.panel.logger.info("Program closed")
		event.Skip()

	def runApp(self):
		self.Fit()
		self.SetSize((265,400))
		self.Show()
		self.Bind(wx.EVT_SIZE, self.panel.ResizeGraph, self)
		self.uiApp.MainLoop()

class SignUpWindow(wx.Frame):
	def __init__(self, parent, recordID, *args, **kwargs):
		super(SignUpWindow, self).__init__(parent, title="Signup User", *args, **kwargs)
		self.panel = wx.Panel(self)
		mainSizer = wx.BoxSizer(wx.VERTICAL)
		buttonSizer = wx.BoxSizer(wx.HORIZONTAL)
		self.parent = parent

		# First Dialog widgets
		self.text = wx.StaticText(self.panel, -1, "User ID not valid. Create a new user profile?")
		self.yesButton = wx.Button(self.panel, label="Yes")
		self.noButton = wx.Button(self.panel, label="No")
		self.Bind(wx.EVT_BUTTON, self.loadForm, self.yesButton)
		self.Bind(wx.EVT_BUTTON, self.closeDialog, self.noButton)

		#Form widgets
		self.firstNameLabel = wx.StaticText(self.panel, label="First Name(s)")
		self.firstNameCtrl = wx.TextCtrl(self.panel)
		self.surnameLabel = wx.StaticText(self.panel, label="Surname")
		self.surnameCtrl = wx.TextCtrl(self.panel)
		self.IDLabel = wx.StaticText(self.panel, label="ID Number")
		self.IDCtrl = wx.TextCtrl(self.panel, value=recordID)
		self.confirmButton = wx.Button(self.panel, label="Confirm")
		self.cancelButton = wx.Button(self.panel, label="Cancel")

		for control in [self.firstNameLabel, self.firstNameCtrl, self.surnameLabel, self.surnameCtrl, self.IDLabel, self.IDCtrl, self.confirmButton, self.cancelButton]:
			control.Show(False)
		
		buttonSizer.Add(self.yesButton, 0, wx.CENTER|wx.ALL|wx.ALIGN_CENTER, 10)
		buttonSizer.Add(self.noButton, 0, wx.CENTER|wx.ALL|wx.ALIGN_CENTER, 10)
		mainSizer.Add(self.text, 0, wx.CENTER|wx.ALL|wx.ALIGN_CENTER, 10)
		mainSizer.Add(buttonSizer, 0, wx.CENTER|wx.ALL|wx.ALIGN_CENTER, 10)
		self.panel.SetSizer(mainSizer)
		self.SetSize(300,150)
	
	def loadForm(self, event):
		self.text.Show(False)
		self.yesButton.Show(False)
		self.noButton.Show(False)
		newMainSizer = wx.BoxSizer(wx.VERTICAL)
		newButtonSizer = wx.BoxSizer(wx.HORIZONTAL)
		gridSizer = wx.FlexGridSizer(rows=3, cols=2, vgap=10, hgap=10)
		
		for control in [self.firstNameLabel, self.firstNameCtrl, self.surnameLabel, self.surnameCtrl, self.IDLabel, self.IDCtrl]:
			gridSizer.Add(control, 0, wx.ALIGN_LEFT|wx.ALL, 10)
			control.Show(True)
		
		newButtonSizer.Add(self.confirmButton, 0, wx.CENTER|wx.ALL|wx.ALIGN_CENTER, 10)
		newButtonSizer.Add(self.cancelButton, 0, wx.CENTER|wx.ALL|wx.ALIGN_CENTER, 10)
		self.confirmButton.Show(True)
		self.cancelButton.Show(True)
		self.Bind(wx.EVT_BUTTON, self.closeDialog, self.cancelButton)
		self.Bind(wx.EVT_BUTTON, self.parentSignUp, self.confirmButton)


		newMainSizer.Add(gridSizer, 0, wx.CENTER|wx.ALL|wx.ALIGN_CENTER, 10)
		newMainSizer.Add(newButtonSizer, 0, wx.CENTER|wx.ALL|wx.ALIGN_CENTER, 10)
		self.panel.SetSizer(newMainSizer)
		self.CreateStatusBar()
		self.SetStatusText("Enter user data")
		self.SetSize(300,300)

	def closeDialog(self, event):
		self.Destroy()

	def parentSignUp(self, event):
		firstName = self.firstNameCtrl.GetLineText(0)
		surname = self.surnameCtrl.GetLineText(0)
		idNumber = self.IDCtrl.GetLineText(0)
		
		for field in [firstName, surname, idNumber]:
			if field == '':
				self.SetStatusText("Field Missing Value!")
				return
		signUpSuccessful = self.parent.signUp(firstName, surname, idNumber)
		
		if not signUpSuccessful:
			self.SetStatusText("Signup failed!")
			return

		self.Destroy()