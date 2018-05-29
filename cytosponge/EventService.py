import cytosponge
import threading
import wx
import wx.lib.newevent
import logging

class EventService:
	def __init__(self, parent):
		self.logger = logging.getLogger("cytosponge_training.EventService")
		self.receivingData = threading.Event()
		self.trainingFinished, self.EVT_TRAINING_FINISHED = wx.lib.newevent.NewEvent()
		self.parent = parent

	def postTrainingFinished(self):
		try:
			wx.PostEvent(self.parent, self.trainingFinished())
		except Exception as e:
			self.logger.error(cytosponge.format_error_message(e))

	def setReceivingData(self):
		try:
			self.receivingData.set()
		except Exception as e:
			self.logger.error(cytosponge.format_error_message(e))

	def clearReceivingData(self):			
		try:
			self.receivingData.clear()
		except Exception as e:
			self.logger.error(cytosponge.format_error_message(e))
