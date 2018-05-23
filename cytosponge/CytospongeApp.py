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

		# Test Image
		velocityPath = "data/test0.png"
		velocityIm = wx.Image(velocityPath).Rescale(600, 400)
		self.velocityGraph = wx.StaticBitmap(self, id=-1, bitmap=wx.Bitmap(velocityIm), size=(600, 400))
		self.graphDisplaySizer.Add(self.velocityGraph, 1, wx.EXPAND|wx.ALL, 10)
		 
		# Bind software events
		self.Bind(self.EventService.EVT_TRAINING_FINISHED, self.OnTrainingFinished)

		self.mainSizer.Add(self.controlSizer, 0, wx.CENTER)
		self.mainSizer.Add(self.graphDisplaySizer, 0, wx.CENTER|wx.ALL, 10)
		self.SetSizer(self.mainSizer)

		self.currImage = 0

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


	def OnTrainingFinished(self, event):
		
		#ACTUAL CODE
		#self.serialCommsService.dataListeningThread.join()
		self.parent.SetStatusText("Training finished")
		#self.DataService.parseData(self.serialCommsService.getIncomingData())
		self.displayGraphs()

	def setTrainingFinished(self):
		self.EventService.postTrainingFinished()

	def displayGraphs(self):
		# width, height, velocityRGB = self.DataService.plotVelocity()
		# print(velocityRGB.tolist())
		# velocityIm = wx.Image(width, height, velocityRGB)

		#velocityPath = self.DataService.plotVelocity()
		#self.DataService.plotTension()
		#velocityPath = "data/test2.png"
		# velocityIm = wx.Image(velocityPath)
		# self.velocityGraph = wx.StaticBitmap(self, id=-1, bitmap=wx.Bitmap(velocityIm), pos=(40, 40), size=(200, 200))
		# self.graphDisplaySizer.Add(self.velocityGraph, 1, wx.EXPAND|wx.ALL, 10)
		
		# self.graphDisplaySizer.Hide(0)
		# self.graphDisplaySizer.Remove(0)
		# self.parent.fSizer.Layout()
		# self.parent.Fit()
		
		print("Displaying Graphs")
		self.graphDisplaySizer.Hide(0)
		self.graphDisplaySizer.Remove(0)
		self.currImage = 1-self.currImage
		velocityPath = "data/test" + str(self.currImage) + ".png"
		velocityIm = wx.Image(velocityPath).Rescale(600, 400)
		self.velocityGraph = wx.StaticBitmap(self, id=-1, bitmap=wx.Bitmap(velocityIm), size=(600, 400))
		self.graphDisplaySizer.Add(self.velocityGraph, 1, wx.EXPAND|wx.ALL, 10)
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
