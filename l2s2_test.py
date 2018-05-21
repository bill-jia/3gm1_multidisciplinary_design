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

def print_response(resp):
	print(resp.status_code)
	print(resp.headers)
	print(resp.text)

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
	print_response(resp)
	return 0


def create_record(first_names, surname, date_of_birth, id_number):
	url = base_url + "/record/create"
	record = {"record": {"first_names": first_names, "surname": surname, "date_of_birth": date_of_birth, "id_number": id_number}}
	resp = s.post(url, json=record)
	print_response(resp)
	return 0

def update_record(ids, first_names, surname, date_of_birth, id_number):
	url = base_url + "/record/update"
	record = {"record": {"id": ids, "first_names": first_names, "surname": surname, "date_of_birth": date_of_birth, "id_number": id_number}}
	resp = s.post(url, json=record)
	print_response(resp)

def delete_record(ids):
	url = base_url + "/record/delete"
	record_id = {"record_id": ids}
	resp = s.post(url, json=record_id)
	print_response(resp)

def search_record(prop, value):
	url = base_url + "/record/search"
	payload = {"filters":[{"operator":1, "property":prop, "value":value}]}
	req = requests.Request()
	resp = s.post(url, json=payload)
	print_response(resp)

#params = {"record_id": 7304618795}

#resp = requests.get(url, headers={'Authorization': 'X-API-KEY ' + api_key}, cert=(cert_path, key_path))


#create_record("Shailen", "Patel", 6890486400, "123456")
#search_record("FirstNames", "Bill")
delete_record(9)