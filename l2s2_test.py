import requests

cert_path = "l2s2_info\\L2S2-2018-CUEDGroup1-20180509.crt"
key_path = "l2s2_info\\L2S2-2018-CUEDGroup1-20180509.key"
#pair_path = "L2S2-2018-CUEDGroup1-20180509.pfx"
f = open("apikey.txt", 'r')
api_key = f.readline()
url = "https://cued2018.xenplate.com/api/record/read"

params = {"record_id": 7304618795}

resp = requests.get(url, headers={'Authorization': 'X-API-KEY ' + api_key}, cert=(cert_path, key_path), params=params)
print(resp.status_code)
print(resp.headers)
print(resp.text)