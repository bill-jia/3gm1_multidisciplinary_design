import ssl
import requests
import json
from requests.adapters import HTTPAdapter


cert_path = "l2s2_info\\certificate.crt"
key_path = "l2s2_info\\key.decrypted.key"
#pair_path = "L2S2-2018-CUEDGroup1-20180509.pfx"
f = open("l2s2_info\\apikey.txt", 'r')
api_key = f.readline()
base_url = "https://cued2018.xenplate.com/api"
CFG_FILE = "config.cfg"

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

def get_session():
	session = requests.Session()
	session.headers.update({'Authorization': 'X-API-KEY ' + api_key})
	session.cert = (cert_path, key_path)
	return session

s = get_session()

def get_record(id):
	url = base_url + "/record/read"
	params = {"record_id": id}
	resp = s.get(url, params = params)
	print(resp.status_code)
	print(resp.headers)
	print(resp.text)
	return 0


def create_record(id, first_names, surname, date_of_birth, id_number):
	url = base_url + "/record/create"
	record = {"id" : id, "first_names": first_names, "surname": surname, "date_of_birth": date_of_birth, "id_number": id_number}
	resp = s.post(url, json=record)
	print(resp.status_code)
	print(resp.headers)
	print(resp.text)
	return 0

def search_record(prop, value):
	url = base_url + "/record/search"
	payload = {"filters":[{"operator":1, "property":prop, "value":value}]}
	req = requests.Request()
	resp = s.post(url, json=payload)
	print(resp.status_code)
	print(resp.headers)
	print(resp.text)

#params = {"record_id": 7304618795}

#resp = requests.get(url, headers={'Authorization': 'X-API-KEY ' + api_key}, cert=(cert_path, key_path))


#create_record(123456, "Bill", "Jia", "09/05/2018", "123456")
search_record("IdNumber", "7304618795")
#get_record(3)