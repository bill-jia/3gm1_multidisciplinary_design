import cytosponge
import matplotlib.pyplot as plt
import io
import numpy as np

class DataService:
	def __init__(self):
		self.time_increment = 1
		self.time = [0, 1, 2, 3, 4]
		self.displacement = []
		self.velocity = [0, 1, 2, 3, 4]
		self.tension = [5, 3, 8, 2, 1]
		self.acceleration = []

	def parseData(self, data):
		print(data)
		arrays = data.split(" , ")
		raw_time = arrays[0].split(" ")
		raw_displacement = arrays[1].split(" ")
		raw_force = arrays[2].split(" ")

		self.time_increment = float(raw_time[1])
		self.time = [i*self.time_increment for i in range(0, (len(raw_displacement)-2))]
		self.displacement = [float(i) for i in raw_displacement[1:-1]]
		#self.velocity = DataService.differentiate(self.displacement, self.time_increment)
		self.acceleration = DataService.differentiate(self.velocity, self.time_increment)
		#self.tension = [float(i) for i in raw_force[1:-1]]

	def plotToPNG(self, x, y, xlabel, ylabel):
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
		return self.plotToPNG(self.time, self.velocity, "Time", "Velocity")

	def plotTension(self):
		return self.plotToPNG(self.time, self.tension, "Time", "Tension")

	@staticmethod
	def differentiate(data, time_increment):
		dData = [0]
		for i in range(1,len(data)):
			dData.append((data[i]-data[i-1])/time_increment)
		return dData