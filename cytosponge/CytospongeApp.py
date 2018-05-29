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
		try:
			self.serialCommsService = cytosponge.SerialCommunicationService(COMport, self.EventService)
			self.logger.info("Serial communications initialized")
		except Exception as e:
			self.logger.error(cytosponge.format_error_message(e))
			sys.exit()

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
		self.controlSizer = wx.StaticBoxSizer(wx.VERTICAL,self,label="Controls")
		self.startStopSizer = wx.BoxSizer(wx.HORIZONTAL)
		self.graphDisplaySizer = wx.BoxSizer(wx.HORIZONTAL)


		# Start and stop buttons
		self.startButton = wx.Button(self, label="Start")
		self.stopButton = wx.Button(self, label="Stop")
		self.Bind(wx.EVT_BUTTON, self.OnClickStart, self.startButton)
		self.Bind(wx.EVT_BUTTON, self.OnClickStop, self.stopButton)

		# Add controls
		self.manualParameterControl = wx.CheckBox(self, label= "Set Parameters")
		self.oesophagusLengthControl = wx.Slider(self, value=self.DataService.oesophagusLength, minValue=10, maxValue=50, style = wx.SL_LABELS)
		self.testCaseSelection = wx.ComboBox(self, value=self.DataService.testCase, choices = ["Normal", "Seizing", "Panic"], style=wx.CB_READONLY)
		self.Bind(wx.EVT_CHECKBOX, self.OnCheckParams, self.manualParameterControl)
		self.Bind(wx.EVT_SCROLL_CHANGED, self.OnOLSlide, self.oesophagusLengthControl)
		self.Bind(wx.EVT_COMBOBOX, self.OnSelectTest, self.testCaseSelection)
		self.oesophagusLengthControl.Disable()
		self.testCaseSelection.Disable()
		# Flags to indicate whether parameter update is necessary before starting a test
		# Set up plot area

		# Test Image
		self.graphDisplay = wx.StaticBitmap(self, id=-1, size=(CytospongePanel.initialBMPX,CytospongePanel.initialBMPY))
		self.graphsReady = False

		# Initialize plot bitmap placeholders
		self.graphs = [wx.Bitmap(), wx.Bitmap()] # 0 is velocity, 1 is tension
		self.currGraph = 0
		self.prevButton = wx.Button(self, label="Prev")
		self.nextButton = wx.Button(self,label="Next")
		self.Bind(wx.EVT_BUTTON, self.ToggleGraph, self.prevButton)
		self.Bind(wx.EVT_BUTTON, self.ToggleGraph, self.nextButton)
		
		self.graphDisplaySizer.Add(self.prevButton, 0, wx.CENTER|wx.ALL|wx.ALIGN_CENTER, 10)
		self.graphDisplaySizer.Add(self.graphDisplay, 1, wx.EXPAND|wx.ALL, 10)
		self.graphDisplaySizer.Add(self.nextButton, 0, wx.CENTER|wx.ALL|wx.ALIGN_CENTER, 10)
		self.graphDisplaySizer.Hide(0)
		self.graphDisplaySizer.Hide(2)
		 
		# Bind software events
		self.Bind(self.EventService.EVT_TRAINING_FINISHED, self.OnTrainingFinished)


		# Map layout
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
		self.mainSizer.Add(self.controlSizer, 0, wx.ALIGN_TOP|wx.ALL|wx.FIXED_MINSIZE, 10)
		self.mainSizer.Add(self.graphDisplaySizer, 0, wx.ALIGN_TOP|wx.ALL, 10)
		self.SetSizer(self.mainSizer)

	def OnClickStart(self, event):
		if not self.EventService.receivingData.isSet():
			self.DataService.updateParameters(self.oesophagusLengthControl.GetValue(), self.testCaseSelection.GetValue())
			self.logger.info("Test started with parameters: OL - " + str(self.DataService.oesophagusLength) + ", TC - " + str(self.DataService.testCase))
			# ACTUAL CODE
			self.serialCommsService.writeData(CytospongeApp.startSignal)
			self.serialCommsService.listenForDataOnEvent(self.EventService.receivingData)
			self.EventService.setReceivingData()
			self.parent.SetStatusText("Training in progress")

		# No arduino test code
		# t = threading.Timer(2.0, self.setTrainingFinished)
		# t.start()


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
		self.DataService.analyzeData(self.serialCommsService.getIncomingData())
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
		if self.graphsReady:
			newPanelX, newPanelY = self.parent.GetSize()
			newBMPX = CytospongePanel.initialBMPX + (newPanelX-CytospongePanel.initialPanelX)
			newBMPY = CytospongePanel.initialBMPY + (newPanelY-CytospongePanel.initialPanelY)
			self.graphs[0] = wx.Bitmap(self.velocityIm.Rescale(newBMPX,newBMPY, quality=wx.IMAGE_QUALITY_HIGH))
			self.graphs[1] = wx.Bitmap(self.tensionIm.Rescale(newBMPX, newBMPY, quality=wx.IMAGE_QUALITY_HIGH))
			self.graphDisplay.SetBitmap(self.graphs[self.currGraph])

class CytospongeApp(wx.Frame):

	testSignal = "99"
	startSignal = "1"
	endSignal = "-1"
	

	def __init__(self, COMport, *args, **kw):
		#Initialize wx App
		self.uiApp = wx.App(False)

		# Initialize superclass
		super(CytospongeApp, self).__init__(*args, **kw)
		self.SetMinSize((265,400))
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
		self.panel.serialCommsService.writeData(CytospongeApp.endSignal)
		self.panel.logger.info("Program closed")
		event.Skip()

	def runApp(self):
		self.Fit()
		self.SetSize((265,400))
		self.Show()
		self.Bind(wx.EVT_SIZE, self.panel.ResizeGraph, self)
		self.uiApp.MainLoop()
