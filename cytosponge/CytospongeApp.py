import cytosponge
import wx
import threading
import time
import numpy as np


class CytospongePanel(wx.Panel):
	def __init__(self, parent):
		wx.Panel.__init__(self, parent)
		self.parent = parent

		# Initialize event signalling
		self.EventService = cytosponge.EventService(self)

		# Initialize serial communications service
		#self.serialCommsService = cytosponge.SerialCommunicationService(COMport, self.EventService)

		# Initialize data analysis and manipulation
		self.DataService = cytosponge.DataService()

		# Create sizers for layout
		self.mainSizer = wx.BoxSizer(wx.VERTICAL)
		self.controlSizer = wx.BoxSizer(wx.HORIZONTAL)
		self.graphDisplaySizer = wx.BoxSizer(wx.HORIZONTAL)


		#Start and stop buttons
		self.startButton = wx.Button(self, label="Start")
		self.stopButton = wx.Button(self, label="Stop")
		self.Bind(wx.EVT_BUTTON, self.OnClickStart, self.startButton)
		self.Bind(wx.EVT_BUTTON, self.OnClickStop, self.stopButton)
		self.controlSizer.Add(self.startButton, 0, wx.CENTER|wx.ALL|wx.ALIGN_CENTER, 10)
		self.controlSizer.Add(self.stopButton, 0, wx.CENTER|wx.ALL|wx.ALIGN_CENTER, 10)

		# Set up plot area

		# Test Image
		testPath = "data/test0.png"
		testIm = wx.Image(testPath).Rescale(600, 400)
		self.graphDisplay = wx.StaticBitmap(self, id=-1, size=(600, 400))

		# Initialize plot bitmap placeholders
		self.velocityGraph = wx.Bitmap()
		self.tensionGraph = wx.Bitmap()
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

		self.mainSizer.Add(self.controlSizer, 0, wx.CENTER)
		self.mainSizer.Add(self.graphDisplaySizer, 0, wx.CENTER|wx.ALL, 10)
		self.SetSizer(self.mainSizer)

		self.currGraph = 0

	def OnClickStart(self, event):
		
		# ACTUAL CODE
		# self.EventService.trainingFinished.clear()
		# self.serialCommsService.writeData(CytospongeApp.startSignal)
		# self.serialCommsService.listenForDataOnEvent(self.EventService.receivingData)
		# self.EventService.receivingData.set()
		self.parent.SetStatusText("Training in progress")
		t = threading.Timer(2.0, self.setTrainingFinished)
		t.start()


	def OnClickStop(self, event):
		# self.serialCommsService.writeData(CytospongeApp.endSignal)
		# self.EventService.receivingData.clear()
		# # Collect incomplete data
		# self.serialCommsService.collectEndData()
		self.parent.SetStatusText("Training stopped")
		self.new_button = wx.Button(self, label="test", name="test")
		self.graphDisplaySizer.Add(self.new_button, 0, wx.ALL, 5)
		self.parent.fSizer.Layout()
		self.parent.Fit()

	def ToggleGraph(self, event):
		self.currGraph = 1 - self.currGraph
		if self.currGraph == 0:
			self.graphDisplay.SetBitmap(self.velocityGraph)
		else:
			self.graphDisplay.SetBitmap(self.tensionGraph)
		self.parent.fSizer.Layout()
		self.parent.Fit()

	def OnTrainingFinished(self, event):
		
		#ACTUAL CODE
		#self.serialCommsService.dataListeningThread.join()
		self.parent.SetStatusText("Training finished")
		
		#WITH SERIAL
		#self.DataService.analyzeData(self.serialCommsService.getIncomingData())
		
		#WITHOUT SERIAL
		self.DataService.analyzeData()
		uploadThread = threading.Thread(name="upload-data", target = self.DataService.uploadData(), args=(None))
		uploadThread.start()
		uploadThread.join()
		self.loadGraphImages()
		self.displayGraphs()

	def setTrainingFinished(self):
		self.EventService.postTrainingFinished()

	def loadGraphImages(self):
		self.velocityIm = wx.Image(self.DataService.velocityGraph).Rescale(600,400)
		self.tensionIm = wx.Image(self.DataService.tensionGraph).Rescale(600,400)

	def displayGraphs(self):
		self.velocityGraph = wx.Bitmap(self.velocityIm)
		self.tensionGraph = wx.Bitmap(self.tensionIm)

		self.graphDisplaySizer.Show(0)
		self.graphDisplaySizer.Show(2)

		self.graphDisplay.SetBitmap(self.velocityGraph)
		self.currGraph = 0
		self.parent.fSizer.Layout()
		self.parent.Fit()

class CytospongeApp(wx.Frame):

	testSignal = "99"
	startSignal = "1"
	endSignal = "-1"
	

	def __init__(self, COMport, *args, **kw):
		#Initialize wx App
		self.uiApp = wx.App(False)

		# Initialize superclass
		super(CytospongeApp, self).__init__(*args, **kw)

		#Create a panel
		self.panel = CytospongePanel(self)

		#fit Sizer
		self.fSizer = wx.BoxSizer(wx.VERTICAL)
		self.fSizer.Add(self.panel, 1, wx.EXPAND)
		self.SetSizer(self.fSizer)
		#Create a status bar
		self.CreateStatusBar()
		self.SetStatusText("Welcome to Cytosponge Training! Start a Test!")
		time.sleep(2)
		self.runApp()

	def runApp(self):
		self.Fit()
		self.Show()
		self.uiApp.MainLoop()
