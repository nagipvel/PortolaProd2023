# this script will load in the fictional company required for external testing

from datetime import datetime
import requests
import json
# this script will load companies into a Portola instance
# Uses data/CompanyAccounts.xlsx to populate fields into a company
# DEBUG = True
DEBUG = False

class PortolaClient:

    __base_headers = {
        'Accept':'application/json',
        'Content Type':'application/json; charset=utf8',
        'User-Agent':'PVEL Test Client'
    }

    users = {}
    auth_header ={}

    def __init__(self, host: str = 'localhost', port: str = ''):
        self.__host: str = host
        if self.__host == 'localhost':
            self.__port = '8000'
            self.__proto: str = 'http'
        else:
            self.__port = port
            self.__proto: str = 'https'

    @property
    def base_url(self) -> str:
        return '{0}://{1}:{2}'.format(self.__proto,self.__host,self.__port)

    def login(self, username:str, password:str) -> bool:
        SERVER = self.base_url
        r = requests.post(SERVER + '/api/signin/', data={'username':username,'password':password})
        token = json.loads(r.text)['token']
        self.auth_header = {'Authorization':'Token '+token}

    def tendemail(self, payload) -> dict:
        data = {'username':payload}
        r = requests.post(self.base_url + '/api/tendemail/',
        data = data,
        headers=self.auth_header)
        return r.json()


if DEBUG:
    client = PortolaClient(host='localhost')
    PASSWORD = 'P@ssw0rd'
else:
    client = PortolaClient(host='portolaprod.azurewebsites.net')
    PASSWORD = '8ie3hzwxMD*'

client.login('mdavis',PASSWORD)
client.tendemail(datetime.today())
