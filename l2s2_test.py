import ssl
import requests
import json
import os
from requests.adapters import HTTPAdapter


cert_path = "l2s2_info\\certificate.crt"
key_path = "l2s2_info\\key.decrypted.key"
#pair_path = "L2S2-2018-CUEDGroup1-20180509.pfx"
f = open("l2s2_info\\apikey.txt", 'r')
api_key = f.readline()
base_url = "https://cued2018.xenplate.com/api"
plate_template_id = "8114813b-6887-4ca2-a4b0-792ad633468d"
plate_template_version = 5
CFG_FILE = "config.cfg"
current_user = 8

POST = "POST"
GET = "GET"

def pretty_print_POST(req):
	"""
	At this point it is completely built and ready
	to be fired; it is "prepared".

	However pay attention at the formatting used in 
	this function because it is programmed to be pretty 
	printed and may differ from the actual request.
	"""
	print('{}\n{}\n{}\n\n{}'.format(
		'-----------START-----------',
		req.method + ' ' + req.url,
		'\n'.join('{}: {}'.format(k, v) for k, v in req.headers.items()),
		req.body,
	))

def formatDataForPlate(data, currentUser):
	output = {
		"record_id": currentUser,
		"plate_template_id": plate_template_id,
		"plate_template_version": plate_template_version
	}
	return output

def printResponse(resp):
	print("Status Code: " + str(resp.status_code))
	print(resp.headers)
	print(resp.text)

def getSession():
	session = requests.Session()
	session.headers.update({'Authorization': 'X-API-KEY ' + api_key})
	session.cert = (cert_path, key_path)
	return session

s = getSession()

def makeRequest(endpoint, method, headers={}, *args, **kwargs):
	url = base_url + endpoint
	req = requests.Request(method, url, *args, **kwargs)
	prepped = s.prepare_request(req)
	prepped.headers.update(headers)
	print(prepped.headers)
	resp = s.send(prepped)
	printResponse(resp)
	return resp

def getRecord(id):
	params = {"record_id": id}
	resp = makeRequest("/record/read", GET, params = params)
	return resp

def createRecord(first_names, surname, date_of_birth, id_number):
	record = {"record": {"first_names": first_names, "surname": surname, "date_of_birth": date_of_birth, "id_number": id_number}}
	resp = makeRequest("/record/create", POST, json=record)
	return resp

def updateRecord(ids, first_names, surname, date_of_birth, id_number):
	record = {"record": {"id": ids, "first_names": first_names, "surname": surname, "date_of_birth": date_of_birth, "id_number": id_number}}
	resp = makeRequest("/record/update", POST, json=record)
	return resp

def deleteRecord(ids):
	record_id = {"record_id": ids}
	resp = makeRequest("/record/delete", POST, json=record_id)
	return resp

def searchRecord(prop, value):
	payload = {"filters":[{"operator":1, "property":prop, "value":value}]}
	resp = makeRequest("/record/search", POST, json=payload)
	return resp

def uploadFile(filePath):
	fileName = os.path.basename(filePath)
	dummyResp = makeRequest("/file/connect", "GET")
	with open(filePath, "rb") as file:
		resp = makeRequest("/file/create", POST, headers={"X-Xenplate-File-Name": fileName}, data=file)
	return resp

def createPlateInstance(data, currentUser):
	payload = formatDataForPlate(data, currentUser)
	print(payload)
	resp = makeRequest("/data/create", POST, json=payload)
	return resp

def formatDataForPlate(data, currentUser):
	outputData = {"data": {
		"record_id": currentUser,
		"plate_template_id": plate_template_id,
		"plate_template_version": plate_template_version,
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

#params = {"record_id": 7304618795}

#resp = requests.get(url, headers={'Authorization': 'X-API-KEY ' + api_key}, cert=(cert_path, key_path))


#create_record("Shailen", "Patel", 6890486400, "123456")
#search_record("FirstNames", "Bill")
#delete_record(9)
#printResponse(getRecord(8))
#printResponse(searchRecord("FirstNames", "Bill"))
#printResponse(uploadFile("data/test0.png"))

#0AB3531E6E187E0EC49B7C1477BB79264ADF9186.png
uploadFile("data/test0.png")
# test_data = {
# 	"test_id": 2,
# 	"test_case": "Seize",
# 	"oesophagus_length": 20,
# 	"score": 70,
# 	"feedback": "Okay",
# 	"velocity_graph": "0AB3531E6E187E0EC49B7C1477BB79264ADF9186.png",
# 	"velocity_graph_name": "test0.png",
# 	"tension_graph": "0AB3531E6E187E0EC49B7C1477BB79264ADF9186.png",
# 	"tension_graph_name": "test0.png"
# }
# printResponse(createPlateInstance(test_data, current_user))