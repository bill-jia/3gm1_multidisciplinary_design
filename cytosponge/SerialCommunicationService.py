import cytosponge
import serial
import threading
import time
import queue
import logging

class SerialCommunicationService:
	def __init__(self, COMport, EventService):
		self.serialLink = self.initializeSerialLink(COMport)
		self.dataListeningThread = None
		self.incomingData = queue.Queue()
		self.EventService = EventService
		self.logger = logging.getLogger('cytosponge_training.SerialCommunicationService')

	def initializeSerialLink(self, COMport):
		serialLink = serial.Serial(COMport, 9600, timeout=1)
		return serialLink

	def writeData(self, data):
		self.serialLink.write(data.encode("utf-8"))

	def listenForDataOnEvent(self, event):
		self.logger.debug("Reading on serial link from start button")
		if self.dataListeningThread is not None:
			self.dataListeningThread.join()
		self.dataListeningThread = threading.Thread(name="data-listening", target = self.readSerialData, args=(event, 30))
		self.dataListeningThread.start()

	def collectEndData(self):
		self.logger.debug("Reading on serial link from stop button")
		self.dataListeningThread = threading.Thread(name="data-listening", target = self.readSerialData, args=(None, 2))
		self.dataListeningThread.start()

	def readSerialData(self, event=None, timeout = None):
		if event is not None:
			event.wait()
		startTime = time.time()
		tryToRead = self.__tryReadSerial(startTime, event, timeout)
		while tryToRead:
			try:
				if self.serialLink.in_waiting > 0:
					print("Attempt to Read")
					readOut = self.serialLink.readline().decode('ascii')
					self.incomingData.put(readOut)
					self.EventService.clearReceivingData()
					self.EventService.postTrainingFinished()
					return
				time.sleep(0.25)
				tryToRead = self.__tryReadSerial(startTime, event, timeout)
			except:
				pass
		# Required because this should only post if exited through a ti
		if event is None or event.isSet():
			self.EventService.postTrainingFinished()

	def getIncomingData(self):
		return self.incomingData.get()

	def __tryReadSerial(self, timeStarted, event=None, timeout=None):
		delta = time.time() - timeStarted
		eventOk = True
		timeOk = True
		if event is not None:
			eventOk = event.isSet()
		if timeout is not None:
			timeOk = delta < timeout
		else:
			self.logger.warn("Serial link timed out while waiting for response")
		return eventOk and timeOk