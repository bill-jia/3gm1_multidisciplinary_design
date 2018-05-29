import cytosponge
import matplotlib.pyplot as plt
import io
import numpy as np
import copy
import logging

class DataService:

	testCaseMatrix = ["Normal", "Seizing", "Panic"]

	def __init__(self):
		# Initialize logging
		self.logger = logging.getLogger("cytosponge_training.DataService")


		#Initialize connection to L2S2
		self.httpService = cytosponge.HTTPService()

		self.time_increment = 1
		self.time = [0, 1, 2, 3, 4]
		self.displacement = []
		self.velocity = [0, 1, 2, 3, 4]
		self.demandForce = []
		self.lowerBoundV = []
		self.upperBoundV = []
		self.lowerBoundT = []
		self.upperBoundT = []
		self.velocityGraph = io.BytesIO()
		self.tensionGraph = io.BytesIO()
		self.velocityGraphUpload = io.BytesIO()
		self.tensionGraphUpload = io.BytesIO()
		self.currentUser = 8

		self.tension = [5, 5, 5, 5, 5]
		self.acceleration = []
		self.manualParameterControl = False
		self.updateOL = False
		self.updateTestCase = False
		self.oesophagusLength = 30
		self.sphincterStrength = 1
		self.testCase = "Normal" # Normal, Seize, or Panic
		self.score = 0
		self.feedback = ""

	def updateParameters(self, oesophagusLength, testCase):
		if self.manualParameterControl:
			if self.updateOL:
				self.oesophagusLength = oesophagusLength
			if self.updateTestCase:
				self.testCase = testCase
			self.updateOL = False
			self.updateTestCase = False
		else:
			self.oesophagusLength = np.random.randint(10, 51)
			self.testCase = DataService.testCaseMatrix[np.random.randint(3)]

	def parseData(self, data):
		arrays = data.split(" , ")
		raw_time = arrays[0].split(" ")
		raw_displacement = arrays[1].split(" ")
		raw_force = arrays[2].split(" ")

		self.time_increment = float(raw_time[1])
		self.time = [i*self.time_increment for i in range(0, (len(raw_displacement)-2))]
		self.displacement = [float(i) for i in raw_displacement[1:-1]]
		self.velocity = DataService.differentiate(self.displacement, self.time_increment)
		self.acceleration = DataService.differentiate(self.velocity, self.time_increment)
		self.tension = [float(i) for i in raw_force[1:-1]]

	def analyzeData(self, data={}):
		#CODE WHEN SERIAL
		self.parseData(data)
		
		### TBD
		# Calculate lower and upper bounds for a particular model
		self.demandForce = self.calculateModelForce()
		idealForce = self.calculateIdealForce()
		self.lowerBoundV, self.upperBoundV = self.calculateVelocityBounds(idealForce)
		self.lowerBoundT, self.upperBoundT = self.calculateForceBounds(idealForce)

		# Plot data
		self.plotVelocity()
		self.plotTension()

		# Develop a scoring system
		forceScore, forceFeedback = self.scoreFromForce()
		velocityScore, velocityFeedback = self.scoreFromVelocity()
		timeScore, timeFeedback = self.scoreFromTime()
		self.score = forceScore + velocityScore + timeScore
		
		# Give text versions of feedback
		self.feedback = forceFeedback + "; " + velocityFeedback + "; " + timeFeedback

	def wrapDataJSON(self):
		# TBD: Wrap data in JSON to send to L2S2
		data = {
			"test_id": 1,
			"test_case": self.testCase,
			"oesophagus_length": self.oesophagusLength,
			"score": self.score,
			"feedback": self.feedback,
			"raw_data": {
				"time": self.arrayToString(self.time),
				"tension": self.arrayToString(self.tension),
				"demand_force": self.arrayToString(self.demandForce),
				"displacement": self.arrayToString(self.displacement)
			}
		}
		return data

	def uploadData(self):
		self.httpService.testConnection()
		if self.httpService.serviceAvailable:
			data = self.wrapDataJSON()
			self.velocityGraphUpload.seek(0)
			self.tensionGraphUpload.seek(0)
			data["velocity_graph"], data["velocity_graph_name"] = self.httpService.uploadFile(self.velocityGraphUpload, "velocity_graph.png")
			data["tension_graph"], data["tension_graph_name"] = self.httpService.uploadFile(self.tensionGraphUpload, "tension_graph.png")
			self.httpService.createPlateInstance(data, self.currentUser)
			self.velocityGraphUpload.seek(0)
			self.tensionGraphUpload.seek(0)

	def arrayToString(self, array):
		outputString = ""
		for i in array:
			outputString = outputString + str(i) + " "
		return outputString

	def calculateModelForce(self):
		modelForce = []
		#TBD
		return modelForce

	def calculateIdealForce(self):
		idealForce = []
		# base model function
		# scale flat parts by oesophagus length
		# scale peaks by sphincter strength
		# scale peaks if seizing/panic
		# add additional peaks if test case is seizing
		# convert to time using velocity, locally apply Jacobian based on measurements
		return idealForce

	def calculateVelocityBounds(self, idealForce):
		lowerBoundV = []
		upperBoundV = []
		# TBD: How to actually do a bound for velocity?

		return (lowerBoundV, upperBoundV)
	
	def calculateForceBounds(self, idealForce):
		lowerBoundT = []
		upperBoundT = []
		#TBD: Scale by ideal force (+- 10%?)

		return (lowerBoundT, upperBoundT)

	def scoreFromForce(self):
		#TBD
		feedback = ""
		score = 0
		return (score, feedback)

	def scoreFromVelocity(self):
		#TBD
		feedback = ""
		score = 0
		return (score, feedback)

	def scoreFromTime(self):
		#TBD
		feedback = ""
		score = 0
		return (score, feedback)

	def plotToPNG(self, x, y, lowerBound, upperBound, xlabel, ylabel):
		fig1 = plt.figure()
		ax1 = fig1.add_subplot(1,1,1)
		ax1.plot(x, y)
		ax1.set_xlabel(xlabel)
		ax1.set_ylabel(ylabel)
		buf = io.BytesIO()
		fig1.savefig(buf, format='png')
		buf.seek(0)
		return buf

	def plotVelocity(self):
		self.velocityGraph = self.plotToPNG(self.time, self.velocity, self.lowerBoundV, self.upperBoundV, "Time", "Velocity")
		self.velocityGraphUpload = copy.deepcopy(self.velocityGraph)

	def plotTension(self):
		self.tensionGraph = self.plotToPNG(self.time, self.tension, self.lowerBoundT, self.upperBoundT, "Time", "Tension")
		self.tensionGraphUpload = copy.deepcopy(self.tensionGraph)

	@staticmethod
	def differentiate(data, time_increment):
		dData = [0]
		for i in range(1,len(data)):
			dData.append((data[i]-data[i-1])/time_increment)
		return dData