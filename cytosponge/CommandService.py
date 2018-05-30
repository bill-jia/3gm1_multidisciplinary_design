import cytosponge
import logging

class CommandService:
	CaseIndex = {"Normal": 2, "Spasms": 3, "Short": 4}
	def __init__(self, parent):
		self.test = 0
		self.logger = logging.getLogger("cytosponge_training.CommandService")
		self.DataService = parent.DataService

	def getStartSignal(self):
		startSignal = str(CommandService.CaseIndex[self.DataService.testCase]) + " " + str(1)
		return startSignal

	def getEndSignal(self):
		return str(-1)

	def getRetractSignal(self):
		return str(-2)
