import wx
import serial

testSignal = "99"
startSignal = "1"
endSignal = "-1"
COMport = 'COM5'

class AppFrame(wx.Frame):
	def __init__(self, *args, **kw):
		# Initialize superclass
		super(AppFrame, self).__init__(*args, **kw)
		
		# Initialize serial link
		self.serialLink = serial.Serial(COMport, 9600, timeout=1)

		#Create a panel
		panel = wx.Panel(self)

		#Start and stop buttons
		self.startButton = wx.Button(self, label="Start", pos=(50, 40))
		self.stopButton = wx.Button(self, label="Stop", pos=(50, 100))
		self.Bind(wx.EVT_BUTTON, self.OnClickStart, self.startButton)
		self.Bind(wx.EVT_BUTTON, self.OnClickStop, self.stopButton)

	def OnClickStart(self, event):
		self.serialLink.write(startSignal.encode("utf-8"))

	def OnClickStop(self, event):
		self.serialLink.write(endSignal.encode("utf-8"))

if __name__ == '__main__':
	uiApp = wx.App()
	frame = AppFrame(None, title="Cytosponge Training")
	frame.Show()
	uiApp.MainLoop()
	#serialLink = serial.Serial(COMport, 9600, timeout=5)
	