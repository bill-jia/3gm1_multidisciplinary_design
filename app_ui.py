import wx
import serial
import threading
import time

testCase = 1
oesophagusLength = 30

testSignal = "99"
startSignal = "1"
endSignal = "-1"
COMport = 'COM3'

def writeStartSignal():
	# Write formatted data containing the test case and physical parameters
	return 0

def initializeSerialLink(COMport):
	serialLink = serial.Serial(COMport, 9600, timeout=1)
	return serialLink

def readSerialData(serialLink, event=None, timeout = None):
	if event is not None:
		event.wait()
		while event.isSet():
			try:
				if serialLink.in_waiting > 0:
					print("Attempt to Read")
					readOut = serialLink.readline().decode('ascii')
					print(readOut)
					break
				time.sleep(0.5)
			except:
				pass
	elif timeout is None:
		while True:
			try:
				if serialLink.in_waiting > 0:
					print("Attempt to Read")
					readOut = serialLink.readline().decode('ascii')
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
				if serialLink.in_waiting > 0:
					print("Attempt to Read")
					readOut = serialLink.readline().decode('ascii')
					print(readOut)
					break
				time.sleep(0.25)
			else:
				break


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
		time.sleep(2)

	def initializeDataListening(self):
		self.dataListeningThread = threading.Thread(name="data-listening", target = readSerialData, args=(serialLink, self.receivingData, None))
		self.dataListeningThread.start()

	def OnClickStart(self, event):
		if not self.dataListeningThread.is_alive():
			self.initializeDataListening()
		self.serialLink.write(startSignal.encode("utf-8"))
		self.receivingData.set()

	def OnClickStop(self, event):
		self.serialLink.write(endSignal.encode("utf-8"))
		self.receivingData.clear()
		# Collect incomplete data
		self.dataListeningThread = threading.Thread(name="data-listening", target = readSerialData, args=(serialLink, None, 2))
		self.dataListeningThread.start()


if __name__ == '__main__':
	uiApp = wx.App()
	serialLink = initializeSerialLink(COMport)
	frame = AppFrame(serialLink, None, title="Cytosponge Training")
	frame.Show()
	uiApp.MainLoop()
	
	