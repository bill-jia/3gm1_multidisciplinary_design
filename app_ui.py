import wx
import serial
import threading
import time

testCase = 1
oesophagusLength = 30

testSignal = "99"
startSignal = "1"
endSignal = "-1"
COMport = 'COM5'

def writeStartSignal():
	# Write formatted data containing the test case and physical parameters
	return 0

def initializeSerialLink(COMport):
	serialLink = serial.Serial(COMport, 9600, timeout=1)
	return serialLink

def readSerialData(serialLink, event):
	event.wait()
	while event.isSet():
		try:
			print("Attempt to Read")
			readOut = serialLink.readline().decode('ascii')
			time.sleep(1)
			print(readOut)
		except:
			pass

class AppFrame(wx.Frame):
	def __init__(self, serialLink, *args, **kw):
		# Initialize superclass
		print(*args)
		super(AppFrame, self).__init__(*args, **kw)

		# assign serial link
		self.serialLink = serialLink

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

	def initializeDataListening(self):
		self.dataListeningThread = threading.Thread(name="data-listening", target = readSerialData, args=(serialLink, self.receivingData))
		self.dataListeningThread.start()

	def OnClickStart(self, event):
		self.serialLink.write(startSignal.encode("utf-8"))
		self.receivingData.set()

	def OnClickStop(self, event):
		self.serialLink.write(endSignal.encode("utf-8"))
		self.receivingData.clear()
		if not (self.dataListeningThread.is_alive()):
			self.initializeDataListening()



if __name__ == '__main__':
	uiApp = wx.App()
	serialLink = initializeSerialLink(COMport)
	frame = AppFrame(serialLink, None, title="Cytosponge Training")
	frame.Show()
	uiApp.MainLoop()
	
	