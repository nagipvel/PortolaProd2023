# Portola Installation note
Portola: PVEL Online Repository of Tests, Operations and Lab Assessments

## Running under Docker
1. Install Docker version 19.03.5, (build 633a0ea838)
1. Install docker-compose version 1.25.3, (build d4d1b42b)
1. in Portola git directory: `docker-compose up -d --build`
1. give it time to come up...
1. surf to http://localhost:8000/api/
1. enjoy!

## Installing from scratch:

Deploy00@PortolaDEV

Local Refresh:
source env.sh
echo "drop DATABASE portoladevdb;CREATE DATABASE portoladevdb;GRANT ALL PRIVILEGES ON DATABASE portoladevdb TO manager;\q" | sudo -u postgres psql postgres ; \
python3 manage.py migrate ; \
python3 manage.py loaddata fixtures/init.json ;\
python3 manage.py loaddata fixtures/auth_fixture.json ;\
python3 manage.py loaddata fixtures/fixture.json ; \
python3 manage.py runserver;

Azure Refresh: (DBAdmin00@PortolaDEV)
source azure_env.sh
echo "drop DATABASE portoladevdb;CREATE DATABASE portoladevdb;GRANT ALL PRIVILEGES ON DATABASE portoladevdb TO manager;\q" \ |
psql -h PortolaDevDB.postgres.database.azure.com -U portoladevdbadmin@PortolaDevDB postgres;
python3 manage.py migrate ; python3 manage.py loaddata fixtures/init.json ;\
python3 manage.py loaddata fixtures/auth_fixture.json ;\
python3 manage.py loaddata fixtures/fixture.json ; \

python3 manage.py runserver

Then run loader scripts

## Pushing Pacifica to Azure:
_this process is what I'm doing on jarvis, nvm does it better and I will probably update these instructions to reflect a less silly build environment_
```
git clone git@github.com:pvevolutionlabs/Pacifica.git
git init azure # (for first time)
cd Pacifica
sudo npm install
sudo npm run build
sudo mv build/* ../azure/
cd ../azure
git remote add azure https://portoladevdeploy@pacificadev.scm.azurewebsites.net:443/pacificadev.git
git add *
git commit -m'push local to azure'
git push azure master # (might need --force )
```

## Microsoft Notes:
Set up pacificadev according to:
https://docs.microsoft.com/en-us/azure/app-service/app-service-web-get-started-html

Added git deployment to the web app

## Requirements:
Python3 & pip3

Installation:

All base requirements are stored in Portola/requirements.txt

install via `pip3 install -r requirements/base.txt`

the rest is off the shelf django 2.2

Postgres setup (DEV):
```
CREATE DATABASE portoladevdb;
CREATE USER manager WITH PASSWORD 'supersecretpass';
GRANT ALL PRIVILEGES ON DATABASE portoladevdb TO manager;
```
source env.sh for DB Parameters

Test server launch:
```
$ python3 manage.py migrate
$ python3 manage.py runserver
```
Node for linux:
https://linuxize.com/post/how-to-install-node-js-on-ubuntu-18.04/
need to install nodejs and npm
curl -o- https://raw.githubusercontent.com/creationix/nvm/v0.34.0/install.sh | bash

Installing React to Azure using:





Installing Python to Azure using:
https://docs.microsoft.com/en-us/azure/app-service/containers/tutorial-python-postgresql-app

These settings ARE NOT LOCKED DOWN need to set security settings correctly before production

`az group create --name PortolaDevResourceGroup --location "West US 2"`
`az group create --name PortolaProdResourceGroup --location "West US 2"`
```
{
  "id": "/subscriptions/308e9c06-d90f-43ae-af52-557ede3534ce/resourceGroups/PortolaDevResourceGroup",
  "location": "westus2",
  "managedBy": null,
  "name": "PortolaDevResourceGroup",
  "properties": {
    "provisioningState": "Succeeded"
  },
  "tags": null,
  "type": null
}
```
now for the database: (Gen5 only)
`az postgres server create --resource-group PortolaDevResourceGroup --name PortolaDevDB --location "West US" --admin-user portoladevdbadmin --admin-password DBAdmin00@PortolaDEV --sku-name G_Gen5_1`

`az postgres server create --resource-group PortolaProdResourceGroup --name portolaproddb --location "West US" --admin-user portolaproddbadmin --admin-password DBAdmin00@PortolaPROD --sku-name G_Gen5_1`
DBAdmin00@PortolaPROD

```
{
  "administratorLogin": "portoladevdbadmin",
  "earliestRestoreDate": "2019-09-12T02:05:25.867000+00:00",
  "fullyQualifiedDomainName": "portoladevdb.postgres.database.azure.com",
  "id": "/subscriptions/308e9c06-d90f-43ae-af52-557ede3534ce/resourceGroups/PortolaDevResourceGroup/providers/Microsoft.DBforPostgreSQL/servers/portoladevdb",
  "location": "westus",
  "masterServerId": "",
  "name": "portoladevdb",
  "replicaCapacity": 5,
  "replicationRole": "None",
  "resourceGroup": "PortolaDevResourceGroup",
  "sku": {
    "capacity": 1,
    "family": "Gen5",
    "name": "B_Gen5_1",
    "size": null,
    "tier": "Basic"
  },
  "sslEnforcement": "Enabled",
  "storageProfile": {
    "backupRetentionDays": 7,
    "geoRedundantBackup": "Disabled",
    "storageAutoGrow": "Enabled",
    "storageAutogrow": null,
    "storageMb": 5120
  },
  "tags": null,
  "type": "Microsoft.DBforPostgreSQL/servers",
  "userVisibleState": "Ready",
  "version": "9.6"
}
```
firewall rules for postgresql
`az postgres server firewall-rule create --resource-group PortolaDevResourceGroup --server-name PortolaDevDB --start-ip-address=0.0.0.0 --end-ip-address=0.0.0.0 --name AllowAllAzureIPs`

`az postgres server firewall-rule create --resource-group PortolaProdResourceGroup --server-name portolaproddb --start-ip-address=0.0.0.0 --end-ip-address=0.0.0.0 --name AllowAllAzureIPs`
```
{
  "endIpAddress": "0.0.0.0",
  "id": "/subscriptions/308e9c06-d90f-43ae-af52-557ede3534ce/resourceGroups/PortolaDevResourceGroup/providers/Microsoft.DBforPostgreSQL/servers/portoladevdb/firewallRules/AllowAllAzureIPs",
  "name": "AllowAllAzureIPs",
  "resourceGroup": "PortolaDevResourceGroup",
  "startIpAddress": "0.0.0.0",
  "type": "Microsoft.DBforPostgreSQL/servers/firewallRules"
}
```
`az postgres server firewall-rule create --resource-group PortolaDevResourceGroup --server-name PortolaDevDB --start-ip-address=24.23.134.119 --end-ip-address=24.23.134.119 --name AllowJarvisClient`

`az postgres server firewall-rule create --resource-group PortolaProdResourceGroup --server-name portolaproddb --start-ip-address=24.23.134.119 --end-ip-address=24.23.134.119 --name AllowJarvisClient`
```
{
  "endIpAddress": "24.23.134.119",
  "id": "/subscriptions/308e9c06-d90f-43ae-af52-557ede3534ce/resourceGroups/PortolaDevResourceGroup/providers/Microsoft.DBforPostgreSQL/servers/portoladevdb/firewallRules/AllowJarvisClient",
  "name": "AllowJarvisClient",
  "resourceGroup": "PortolaDevResourceGroup",
  "startIpAddress": "24.23.134.119",
  "type": "Microsoft.DBforPostgreSQL/servers/firewallRules"
}
```
`az postgres server firewall-rule create --resource-group PortolaDevResourceGroup --server-name PortolaDevDB --start-ip-address=157.131.111.179 --end-ip-address=157.131.111.179 --name AllowBKLClient`
```
{157.131.111.179
  "endIpAddress": "157.131.106.204",
  "id": "/subscriptions/308e9c06-d90f-43ae-af52-557ede3534ce/resourceGroups/PortolaDevResourceGroup/providers/Microsoft.DBforPostgreSQL/servers/portoladevdb/firewallRules/AllowBKLClient",
  "name": "AllowBKLClient",
  "resourceGroup": "PortolaDevResourceGroup",
  "startIpAddress": "157.131.106.204",
  "type": "Microsoft.DBforPostgreSQL/servers/firewallRules"
}
```
Azure DB Init (run locally)
`psql -h PortolaDevDB.postgres.database.azure.com -U portoladevdbadmin@PortolaDevDB postgres`

`psql -h portolaproddb.postgres.database.azure.com -U portolaproddbadmin@portolaproddb postgres`

this is the env changes for local django to run against AzureDB (for tests)
```
export DBHOST="PortolaDevDB.postgres.database.azure.com"
export DBUSER="manager@PortolaDevDB"
export DBNAME="portoladevdb"
export DBPASS="supersecretpass"
```
And make sure to migrate DB on Azure:
`python3 manage.py migrate`
Configure deployment user
`az webapp deployment user set --user-name portoladevdeploy --password Deploy00@PortolaDEV`
```
{
  "id": null,
  "kind": null,
  "name": "web",
  "publishingPassword": null,
  "publishingPasswordHash": null,
  "publishingPasswordHashSalt": null,
  "publishingUserName": "portoladevdeploy",
  "scmUri": null,
  "type": "Microsoft.Web/publishingUsers/web"
}
```
Create App Service plan
`az appservice plan create --name PortolaDevAppServicePlan --resource-group PortolaDevResourceGroup --sku B1 --is-linux`
```

{
  "freeOfferExpirationTime": "2019-10-12T00:25:09.523333",
  "geoRegion": "West US 2",
  "hostingEnvironmentProfile": null,
  "hyperV": false,
  "id": "/subscriptions/308e9c06-d90f-43ae-af52-557ede3534ce/resourceGroups/PortolaDevResourceGroup/providers/Microsoft.Web/serverfarms/PortolaDevAppServicePlan",
  "isSpot": false,
  "isXenon": false,
  "kind": "linux",
  "location": "West US 2",
  "maximumElasticWorkerCount": 1,
  "maximumNumberOfWorkers": 3,
  "name": "PortolaDevAppServicePlan",
  "numberOfSites": 0,
  "perSiteScaling": false,
  "provisioningState": "Succeeded",
  "reserved": true,
  "resourceGroup": "PortolaDevResourceGroup",
  "sku": {
    "capabilities": null,
    "capacity": 1,
    "family": "B",
    "locations": null,
    "name": "B1",
    "size": "B1",
    "skuCapacity": null,
    "tier": "Basic"
  },
  "spotExpirationTime": null,
  "status": "Ready",
  "subscription": "308e9c06-d90f-43ae-af52-557ede3534ce",
  "tags": null,
  "targetWorkerCount": 0,
  "targetWorkerSizeId": 0,
  "type": "Microsoft.Web/serverfarms",
  "workerTierName": null
}
```
create a web app
`az webapp create --resource-group PortolaDevResourceGroup --plan PortolaDevAppServicePlan --name PortolaDEV --runtime "PYTHON|3.7" --deployment-local-git`
```
Local git is configured with url of 'https://portoladevdeploy@portoladev.scm.azurewebsites.net/PortolaDEV.git'
{
  "availabilityState": "Normal",
  "clientAffinityEnabled": true,
  "clientCertEnabled": false,
  "clientCertExclusionPaths": null,
  "cloningInfo": null,
  "containerSize": 0,
  "dailyMemoryTimeQuota": 0,
  "defaultHostName": "portoladev.azurewebsites.net",
  "deploymentLocalGitUrl": "https://portoladevdeploy@portoladev.scm.azurewebsites.net/PortolaDEV.git",
  "enabled": true,
  "enabledHostNames": [
    "portoladev.azurewebsites.net",
    "portoladev.scm.azurewebsites.net"
  ],
  "ftpPublishingUrl": "ftp://waws-prod-mwh-029.ftp.azurewebsites.windows.net/site/wwwroot",
  "geoDistributions": null,
  "hostNameSslStates": [
    {
      "hostType": "Standard",
      "ipBasedSslResult": null,
      "ipBasedSslState": "NotConfigured",
      "name": "portoladev.azurewebsites.net",
      "sslState": "Disabled",
      "thumbprint": null,
      "toUpdate": null,
      "toUpdateIpBasedSsl": null,
      "virtualIp": null
    },
    {
      "hostType": "Repository",
      "ipBasedSslResult": null,
      "ipBasedSslState": "NotConfigured",
      "name": "portoladev.scm.azurewebsites.net",
      "sslState": "Disabled",
      "thumbprint": null,
      "toUpdate": null,
      "toUpdateIpBasedSsl": null,
      "virtualIp": null
    }
  ],
  "hostNames": [
    "portoladev.azurewebsites.net"
  ],
  "hostNamesDisabled": false,
  "hostingEnvironmentProfile": null,
  "httpsOnly": false,
  "hyperV": false,
  "id": "/subscriptions/308e9c06-d90f-43ae-af52-557ede3534ce/resourceGroups/PortolaDevResourceGroup/providers/Microsoft.Web/sites/PortolaDEV",
  "identity": null,
  "inProgressOperationId": null,
  "isDefaultContainer": null,
  "isXenon": false,
  "kind": "app,linux",
  "lastModifiedTimeUtc": "2019-09-12T00:28:50.720000",
  "location": "West US 2",
  "maxNumberOfWorkers": null,
  "name": "PortolaDEV",
  "outboundIpAddresses": "13.77.182.13,13.77.161.10,52.183.26.12,52.175.235.45,13.77.178.124",
  "possibleOutboundIpAddresses": "13.77.182.13,13.77.161.10,52.183.26.12,52.175.235.45,13.77.178.124,52.183.34.217,13.66.206.87,13.77.172.226,52.183.34.132,13.77.180.8",
  "redundancyMode": "None",
  "repositorySiteName": "PortolaDEV",
  "reserved": true,
  "resourceGroup": "PortolaDevResourceGroup",
  "scmSiteAlsoStopped": false,
  "serverFarmId": "/subscriptions/308e9c06-d90f-43ae-af52-557ede3534ce/resourceGroups/PortolaDevResourceGroup/providers/Microsoft.Web/serverfarms/PortolaDevAppServicePlan",
  "siteConfig": null,
  "slotSwapStatus": null,
  "state": "Running",
  "suspendedTill": null,
  "tags": null,
  "targetSwapSlot": null,
  "trafficManagerHostNames": null,
  "type": "Microsoft.Web/sites",
  "usageState": "Normal"
}
```
`az webapp config appsettings set --name PortolaDEV --resource-group PortolaDevResourceGroup --settings DBHOST="portoladevdb.postgres.database.azure.com" DBUSER="manager@portoladevdb" DBPASS="supersecretpass" DBNAME="portoladevdb"`
```
[
  {
    "name": "DBHOST",
    "slotSetting": false,
    "value": "portoladevdb.postgres.database.azure.com"
  },
  {
    "name": "DBUSER",
    "slotSetting": false,
    "value": "manager@portoladevdb"
  },
  {
    "name": "DBPASS",
    "slotSetting": false,
    "value": "supersecretpass"
  },
  {
    "name": "DBNAME",
    "slotSetting": false,
    "value": "pollsdb"
  }
]
```
Set local git to know about remote:
`git remote add azure https://portoladevdeploy@portoladev.scm.azurewebsites.net/PortolaDEV.git`


Logging:
```
mark@Azure:~$ az webapp log config --name portoladev --resource-group PortolaDevResourceGroup --docker-container-logging filesystem
{
  "applicationLogs": {
    "azureBlobStorage": {
      "level": "Off",
      "retentionInDays": null,
      "sasUrl": null
    },
    "azureTableStorage": {
      "level": "Off",
      "sasUrl": null
    },
    "fileSystem": {
      "level": "Off"
    }
  },
  "detailedErrorMessages": {
    "enabled": false
  },
  "failedRequestsTracing": {
    "enabled": false
  },
  "httpLogs": {
    "azureBlobStorage": {
      "enabled": false,
      "retentionInDays": 3,
      "sasUrl": null
    },
    "fileSystem": {
      "enabled": true,
      "retentionInDays": 3,
      "retentionInMb": 100
    }
  },
  "id": "/subscriptions/308e9c06-d90f-43ae-af52-557ede3534ce/resourceGroups/PortolaDevResourceGroup/providers/Microsoft.Web/sites/portoladev/config/logs",
  "kind": null,
  "location": "West US 2",
  "name": "logs",
  "resourceGroup": "PortolaDevResourceGroup",
  "type": "Microsoft.Web/sites/config"
}
```
az webapp log tail --name portoladev --resource-group PortolaDevResourceGroup
