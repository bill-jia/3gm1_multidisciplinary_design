import cytosponge
import threading

class EventService:
	def __init__(self):
		self.receivingData = threading.Event()
		self.trainingFinished = threading.Event()