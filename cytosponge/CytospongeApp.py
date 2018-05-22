import cytosponge
import wx
import threading
import time
import numpy as np


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
		panel = wx.Panel(self)

		#Start and stop buttons
		self.startButton = wx.Button(self, label="Start", pos=(50, 40))
		self.stopButton = wx.Button(self, label="Stop", pos=(50, 100))
		self.Bind(wx.EVT_BUTTON, self.OnClickStart, self.startButton)
		self.Bind(wx.EVT_BUTTON, self.OnClickStop, self.stopButton)

		#Create a status bar
		self.CreateStatusBar()
		self.SetStatusText("Welcome to Cytosponge Training! Start a Test!")
		time.sleep(2)


	def runApp(self):
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

		velocityPath = self.DataService.plotVelocity()
		velocityIm = wx.Image(velocityPath)
		self.velocityGraph = wx.StaticBitmap(self, id=-1, bitmap=wx.Bitmap(velocityIm), pos=(40, 40), size=(100, 100))
		self.velocityGraph.refresh()