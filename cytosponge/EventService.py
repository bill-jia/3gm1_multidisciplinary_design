import cytosponge
import threading
import wx
import wx.lib.newevent

class EventService:
	def __init__(self, panel):
		self.receivingData = threading.Event()
		self.trainingFinished, self.EVT_TRAINING_FINISHED = wx.lib.newevent.NewEvent()
		self.panel = panel

	def postTrainingFinished(self):
		wx.PostEvent(self.panel, self.trainingFinished())
