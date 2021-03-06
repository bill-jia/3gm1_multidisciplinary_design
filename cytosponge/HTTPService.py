import cytosponge
import requests
import io
import socket
import logging
import sys

class HTTPService:
	POST = "POST"
	GET = "GET"
	timeout = (3.05, 27)

	def __init__(self):
		try:
			self.logger = logging.getLogger("cytosponge_training.HTTPService")
			self.cert_path = "l2s2_info/certificate.crt"
			self.key_path = "l2s2_info/key.decrypted.key"
			f = open("l2s2_info/apikey.txt", 'r')
			self.api_key = f.readline()
			self.base_url = "https://cued2018.xenplate.com/api"
			self.plate_template_id = "8114813b-6887-4ca2-a4b0-792ad633468d"
			self.plate_template_version = 10
			self.current_user = 8
			self.session = self.getSession(self.api_key, self.cert_path, self.key_path)
			self.serviceAvailable = self.internetConnectionAvailable()
			self.logger.info("HTTP Service initialized")
		except Exception as e:
			self.logger.error(cytosponge.format_error_message(e))
			sys.exit()

	def internetConnectionAvailable(self, host="8.8.8.8", port=53, timeout=3):
		try:
			socket.setdefaulttimeout(timeout)
			socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
			return True
		except Exception as e:
			self.logger.warn("Could not connect to the Internet")
			self.logger.warn(e.message)
			return False

	def getSession(self, api_key, cert_path, key_path):
		session = requests.Session()
		session.headers.update({'Authorization': 'X-API-KEY ' + api_key})
		session.cert = (cert_path, key_path)
		return session

	def makeRequest(self, endpoint, method, headers={}, *args, **kwargs):
		url = self.base_url + endpoint
		req = requests.Request(method, url, *args, **kwargs)
		prepped = self.session.prepare_request(req)
		prepped.headers.update(headers)
		#print(prepped.headers)
		resp = self.session.send(prepped, timeout = HTTPService.timeout)
		if resp.status_code == 404:
			self.logger.warn("Request timed out at " + url + "\n" + "Headers: " + str(prepped.headers))
			return {}
		elif resp.status_code == 503:
			self.logger.warn("L2S2 server not available")
			self.serviceAvailable = False
			return {}
		elif resp.status_code != 200:
			self.logger.warn("Request to L2S2 server failed")
			self.logger.warn(HTTPService.printResponse(resp))
			return {}
		try:
			self.serviceAvailable = True
			self.logger.debug("HTTP Request to URL: " + url + " successful: " + str(resp.headers))
			return resp.json()
		except ValueError as e:
			self.logger.warn(cytosponge.format_error_message(e))
			return {}

	def testConnection(self):
		return self.makeRequest("/file/connect", HTTPService.GET)

	def getRecord(self, id):
		params = {"record_id": id}
		resp = self.makeRequest("/record/read", HTTPService.GET, params = params)
		return resp

	def createRecord(self, first_names, surname, date_of_birth, id_number):
		record = {"record": {"first_names": first_names, "surname": surname, "date_of_birth": date_of_birth, "id_number": id_number}}
		resp = self.makeRequest("/record/create", HTTPService.POST, json=record)
		return resp

	def updateRecord(self, ids, first_names, surname, date_of_birth, id_number):
		record = {"record": {"id": ids, "first_names": first_names, "surname": surname, "date_of_birth": date_of_birth, "id_number": id_number}}
		resp = self.makeRequest("/record/update", HTTPService.POST, json=record)
		return resp

	def deleteRecord(self, ids):
		record_id = {"record_id": ids}
		resp = self.makeRequest("/record/delete", HTTPService.POST, json=record_id)
		return resp

	def searchRecord(self, prop, value):
		payload = {"filters":[{"operator":1, "property":prop, "value":value}]}
		resp = self.makeRequest("/record/search", HTTPService.POST, json=payload)
		return resp

	def uploadFile(self, data, fileName):
		self.testConnection()
		resp = self.makeRequest("/file/create", HTTPService.POST, headers={"X-Xenplate-File-Name": fileName}, data=data)
		return (resp["FileCreateResult"]["file_id"], fileName)

	# def uploadFile(self, filePath):
	# 	fileName = os.path.basename(filePath)
	# 	dummyResp = self.makeRequest("/file/connect", "GET")
	# 	with open(filePath, "rb") as file:
	# 		resp = self.makeRequest("/file/create", HTTPService.POST, headers={"X-Xenplate-File-Name": fileName}, data=file)
	# 	return resp

	def createPlateInstance(self, data, currentUser):
		payload = self.formatDataForPlate(data, currentUser)
		#print(payload)
		resp = self.makeRequest("/data/create", HTTPService.POST, json=payload)
		return resp

	def formatDataForPlate(self,data, currentUser):
		outputData = {"data": {
			"record_id": currentUser,
			"plate_template_id": self.plate_template_id,
			"plate_template_version": self.plate_template_version,
			"control_values": [
				{
					"id": 8,
					"value": data["test_id"]
				},
				{
					"id": 9,
					"value": data["test_case"]
				},
				{
					"id": 10,
					"value": data["oesophagus_length"]
				},
				{
					"id": 11,
					"value": data["score"]
				},
				{
					"id": 13,
					"value": data["feedback"]
				},
				{
					"id": 15,
					"value":"",
					"attachments": [
						{
							"description": "",
							"key": data["velocity_graph"],
							"original_file_name": data["velocity_graph_name"]
						}
					]
				},
				{
					"id": 17,
					"value":"",
					"attachments": [
						{
							"description": "",
							"key": data["tension_graph"],
							"original_file_name": data["tension_graph_name"]
						}
					]
				}
			]
		} }
		return outputData

	@staticmethod
	def printResponse(resp):
		return "Status Code: " + str(resp.status_code) + "\n" \
		+ str(resp.headers) + "\n" \
		+ str(resp.text) + "\n"
