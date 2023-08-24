# from django.test import TestCase
from lib import api

# import requests
# import json

client = api.PortolaClient(host='portoladev.azurewebsites.net')
client.login('mdavis','P@ssw0rd')

# r = requests.post(SERVER + '/api/signin/', data={'username':'daniel.chang@jinkosloar.com','password':'kzpACUvV9H7RWY9j'})
# client.login('daniel.chang@jinkosloar.com','kzpACUvV9H7RWY9j')
print(client.whoami())
# should ahve a token now:
# print(r.text)
# print(r.request)
# Just need the value of the returned token
# token = json.loads(r.text)['token']
# # build header string
# auth_header = {'Authorization':'Token '+token}
#
# # get the restricted URL with Authorization
# r = requests.get(SERVER + '/api/',headers=auth_header)
# print(json.dumps(r.text))
#
# r = requests.get(SERVER + '/api/documents/1062/download/',headers=auth_header)
