import wx
import serial
import threading
import time


class CytospongeApp(wx.Frame):

	testSignal = "99"
	startSignal = "1"
	endSignal = "-1"
	

	def __init__(self, COMport, *args, **kw):
		#Initialize wx App
		self.uiApp = wx.App()

		# Initialize superclass
		super(CytospongeApp, self).__init__(*args, **kw)

		# assign serial link
		self.serialLink = self.initializeSerialLink(COMport)

		# Initialize event signalling
		self.receivingData = threading.Event()
		self.initializeDataListening()

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

	def initializeSerialLink(self, COMport):
		serialLink = serial.Serial(COMport, 9600, timeout=1)
		return serialLink

	def readSerialData(self, event=None, timeout = None):
		if event is not None:
			event.wait()
			while event.isSet():
				try:
					if self.serialLink.in_waiting > 0:
						print("Attempt to Read")
						readOut = self.serialLink.readline().decode('ascii')
						print(readOut)
						break
					time.sleep(0.5)
				except:
					pass
			self.SetStatusText("Training Finished")
		elif timeout is None:
			while True:
				try:
					if self.serialLink.in_waiting > 0:
						print("Attempt to Read")
						readOut = self.serialLink.readline().decode('ascii')
						print(readOut)
						break
					time.sleep(0.5)
				except:
					pass
		else:
			timeStarted = time.time()
			while True:
				delta = time.time() - timeStarted
				if delta < timeout:
					if self.serialLink.in_waiting > 0:
						print("Attempt to Read")
						readOut = self.serialLink.readline().decode('ascii')
						print(readOut)
						break
					time.sleep(0.25)
				else:
					break

	def initializeDataListening(self):
		self.dataListeningThread = threading.Thread(name="data-listening", target = self.readSerialData, args=(self.receivingData, None))
		self.dataListeningThread.start()

	def OnClickStart(self, event):
		if not self.dataListeningThread.is_alive():
			self.initializeDataListening()
		self.serialLink.write(CytospongeApp.startSignal.encode("utf-8"))
		self.receivingData.set()
		self.SetStatusText("Training in progress")

	def OnClickStop(self, event):
		self.serialLink.write(CytospongeApp.endSignal.encode("utf-8"))
		self.receivingData.clear()
		# Collect incomplete data
		self.dataListeningThread = threading.Thread(name="data-listening", target = self.readSerialData, args=(None, 2))
		self.dataListeningThread.start()
		self.SetStatusText("Training stopped")