import cytosponge
import serial
import threading
import time
import queue

class SerialCommunicationService:
	def __init__(self, COMport, EventService):
		self.serialLink = self.initializeSerialLink(COMport)
		self.dataListeningThread = None
		self.incomingData = queue.Queue()
		self.EventService = EventService

	def initializeSerialLink(self, COMport):
		serialLink = serial.Serial(COMport, 9600, timeout=1)
		return serialLink

	def writeData(self, data):
		self.serialLink.write(data.encode("utf-8"))

	def listenForDataOnEvent(self, event):
		if self.dataListeningThread is None or not (self.dataListeningThread.is_alive()):
			self.dataListeningThread = threading.Thread(name="data-listening", target = self.readSerialData, args=(event, None))
			self.dataListeningThread.start()

	def collectEndData(self):
		self.dataListeningThread = threading.Thread(name="data-listening", target = self.readSerialData, args=(None, 2))
		self.dataListeningThread.start()

	def readSerialData(self, event=None, timeout = None):
		if event is not None:
			event.wait()
			while event.isSet():
				try:
					if self.serialLink.in_waiting > 0:
						print("Attempt to Read")
						readOut = self.serialLink.readline().decode('ascii')
						self.incomingData.put(readOut)
						break
					time.sleep(0.5)
				except:
					pass
		elif timeout is None:
			while True:
				try:
					if self.serialLink.in_waiting > 0:
						print("Attempt to Read")
						readOut = self.serialLink.readline().decode('ascii')
						self.incomingData.put(readOut)
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
						self.incomingData.put(readOut)
						break
					time.sleep(0.25)
				else:
					break
		self.EventService.postTrainingFinished()

	def getIncomingData(self):
		return self.incomingData.get()