## known issues:
* superuser has no profile by default. Resolve by updating the user at `/users/{id}/`
* password change via DRF page currently broken
* document upload doesn't push to Box (deferred)

New requirement:
* set session length to 72 hours
* 2FA Email authentication for a new device or for 30(14?) days on old device
-- need to work on the mechanism for expiring the tokens.
* Dirty cache, new version in box (retire old files)
-- future feature. Right now, points to new file only
* entity lists need to be filtered by user types -- support downstream partner page
* prevent duplicate document requests from being created. -- return error

entity filter by type
filter projects for MFG/DSP/DSC

* data migration:
** test sharepoint download

* need to limit visible entities based on user type -- talk to adam more about This
* User categories based on partner type?
** Messages for individual users
** Messages from PVEL based on user type
* Scorecard downloads as documents inside portola.

Django magic links:
/maybe/
https://simpleisbetterthancomplex.com/tutorial/2016/08/24/how-to-create-one-time-link.html

Django templated email:
https://stackoverflow.com/questions/2809547/creating-email-templates-with-django

Box bearer token:
curl https://api.box.com/2.0/folders/0 -H \
"Authorization: Bearer QHO9NACwTxrucABWSuc4875drFXv5EoH"

Accept-Encoding header with a value of gzip, deflate,

Box-Notifications header with the value off.

Deprecated calls:

### Agreements
These are specific agreements that must be set in order to view certain sections
 of the site or to clear warnings (cookie)

current user:
/agreement/{id}
GET returns true if the user has agreed to the agreement identified by {id}

POST - sets agreement to True
DELETE - removes agreement

Admin User:
/agreement/
GET list all of the agreements and their text
POST - create a new agreement that may be used to test an agreement

### Authentication
Token auth from:
https://chrisbartos.com/articles/how-to-implement-token-authentication-with-django-rest-framework/

Expiring tokens:
https://medium.com/@yerkebulan199/django-rest-framework-drf-token-authentication-with-expires-in-a05c1d2b7e05
(not implemented yet MD 8/19)
/authentication/login
POST
```
{
    "user":"username",
    "password":"password"
}
```
sets authorization token

/authentication/logout

/authentication/token/set
/authentication/token/delete
### rfp (TODO)
downstram partner could send an RFP to all mfgs based on a checklist of recipients
2 doctypes: opriginal RFP document, and response documents.

RFP Updates may cause notifications to all responding entities
RFP Response may cause notification to the requesting entity.

/rfp/
POST - create new rfp

/rfp/list

/rfp/{id}/invite/{entity_id}

/rfp/recipients -- who did I send to?

/rfp/resposnses/
POST - new response ducument

/rfp/response/{id}/
PUT new document
PUT changes to response
```
{
  "id":99,
  "responding entity id":{},
  "responding entity name":"foo builders and sons",
  "parent project":{RFP ID},
  "module types proposed":[
    "poly","72 cell"
  ],
  "status":"active|withdrawn",
  "document":{id}  
}
```

/rfp/{id}
GET - metadata about the RFP

/rfp/{id}/document
POST - create new document attached to {id}
```
{
  "id":99,
  "Project contact_id":"username",
  "project contact name":"freddy wang",
  "project entity_id":{id},
  "project entity name":"foo power supplier",
  "project name":"300MW Georgia",
  "create date":"date",
  "capacity":"300MW",
  "status":"accepting|closed|",
  "submission deadline":"date`",
  "module types accepted": [
    "72 cell",
    "bifacial",
    "mono",
    "poly","1500v","400W"
  ],
  "invited enitites":[
    {
      "mfg_id":4
      "mfg_name":"yingli"  
    },
    {
      mfg_id:2,
      "mfg_name":"Jinko"
    }
  ]
  "document":{id},
  "notify type": "Email",
}

* Need to get the list of module types and how to store into here
```
### Template (TODO)
The template table holds all of the text and html blobs that will be presented to the user at various times.

email
sms
landing page
faq

# Notes

# djangodocker
Running Django with Docker step-by-step

This repository stores the changes over the posts about django in docker.

Each post trackes its changes in a different branch:

- [Django development environment with Docker — A step by step guide](https://blog.devartis.com/django-development-environment-with-docker-a-step-by-step-guide-ae234612fa61) - [00-start](https://github.com/devartis/djangodocker/tree/00-start)
- [Django development with Docker — A step by step guide](https://blog.devartis.com/django-development-with-docker-a-step-by-step-guide-525c0d08291) - [01-django-in-docker](https://github.com/devartis/djangodocker/tree/01-django-in-docker)
- [Django development with Docker —A completed development cycle](https://blog.devartis.com/django-development-with-docker-a-completed-development-cycle-7322ad8ba508) - [02-django-development](https://github.com/devartis/djangodocker/tree/02-django-development)
### Message (system only)
sends messages via email or sms

`/message/{id}/{recipient_id}/`
Notes about Users:
New users are not approved for any role:
pending user -- no permissions, registered and email is validated

Approved users:
downstream partner -- approved by PVEL
downstream client -- see reports we create for them, see all downstream partner reports, reports not available to downstream  
manufacturer -- User -- sees pending requests, cannot act on them
manufacturer -- Admin -- approves requests

Internal accounts created by PVEL:
PVEL Admin -- me adam etc can upload and update reports
