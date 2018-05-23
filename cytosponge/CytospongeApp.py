import cytosponge
import wx
import threading
import time
import numpy as np


class CytospongePanel(wx.Panel):
	def __init__(self, parent):
		wx.Panel.__init__(self, parent)
		self.parent = parent
		# Create sizers for layout
		self.mainSizer = wx.BoxSizer(wx.VERTICAL)
		self.controlSizer = wx.BoxSizer(wx.HORIZONTAL)
		self.graphDisplaySizer = wx.BoxSizer(wx.HORIZONTAL)


		#Start and stop buttons
		self.startButton = wx.Button(self, label="Start")
		self.stopButton = wx.Button(self, label="Stop")
		self.Bind(wx.EVT_BUTTON, self.parent.OnClickStart, self.startButton)
		self.Bind(wx.EVT_BUTTON, self.parent.OnClickStop, self.stopButton)
		self.controlSizer.Add(self.startButton, 0, wx.CENTER|wx.ALL|wx.ALIGN_CENTER, 10)
		self.controlSizer.Add(self.stopButton, 0, wx.CENTER|wx.ALL|wx.ALIGN_CENTER, 10)

		# Test Image
		velocityPath = "data/test.png"
		velocityIm = wx.Image(velocityPath).Rescale(600, 400)
		self.velocityGraph = wx.StaticBitmap(self, id=-1, bitmap=wx.Bitmap(velocityIm), size=(600, 400))
		self.graphDisplaySizer.Add(self.velocityGraph, 1, wx.EXPAND|wx.ALL, 10)

		self.mainSizer.Add(self.controlSizer, 0, wx.CENTER)
		self.mainSizer.Add(self.graphDisplaySizer, 0, wx.CENTER|wx.ALL, 10)
		self.SetSizer(self.mainSizer)

class CytospongeApp(wx.Frame):

	testSignal = "99"
	startSignal = "1"
	endSignal = "-1"
	

	def __init__(self, COMport, *args, **kw):
		#Initialize wx App
		self.uiApp = wx.App()

		# Initialize superclass
		super(CytospongeApp, self).__init__(*args, **kw)
		
		# Initialize event signalling
		self.eventService = cytosponge.EventService()

		# Initialize serial communications service
		self.serialCommsService = cytosponge.SerialCommunicationService(COMport, self.eventService)

		# Initialize data analysis and manipulation
		self.DataService = cytosponge.DataService()

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

	def onTrainingFinished(self, event, x):
		self.serialCommsService.dataListeningThread.join()
		if event.isSet():
			self.SetStatusText("Training finished")
		self.DataService.parseData(self.serialCommsService.getIncomingData())
		self.displayGraphs()

	def OnClickStart(self, event):
		self.eventService.trainingFinished.clear()
		self.serialCommsService.writeData(CytospongeApp.startSignal)
		self.serialCommsService.listenForDataOnEvent(self.eventService.receivingData)
		self.eventService.receivingData.set()
		self.SetStatusText("Training in progress")
		finishedTrainingThread = threading.Thread(name="training-finished", target = self.onTrainingFinished, args=(self.eventService.trainingFinished, 0))
		finishedTrainingThread.start()

	def OnClickStop(self, event):
		self.serialCommsService.writeData(CytospongeApp.endSignal)
		self.eventService.receivingData.clear()
		# Collect incomplete data
		self.serialCommsService.collectEndData()
		self.SetStatusText("Training stopped")

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
		self.panel.graphDisplaySizer.Hide(0)
		self.panel.graphDisplaySizer.Remove(0)
		
		# velocityPath = "data/test2.png"
		# velocityIm = wx.Image(velocityPath).Rescale(600, 400)
		# self.velocityGraph = wx.StaticBitmap(self, id=-1, bitmap=wx.Bitmap(velocityIm), size=(600, 400))
		# self.graphDisplaySizer.Add(self.velocityGraph, 1, wx.EXPAND|wx.ALL, 10)

		self.randomButton = wx.Button(self, label="Random")
		self.panel.graphDisplaySizer.Add(self.randomButton, 0, wx.CENTER|wx.ALL|wx.ALIGN_CENTER, 10)

		self.fSizer.Layout()
		self.Fit()
