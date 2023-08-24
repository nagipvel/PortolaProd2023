# Portola
Portola: PVEL Online Repository of Tests, Operations and Lab Assessments

this is the first steps towards prototyping a portal for PVEL data

The API calls documented here are for design reference only. Python source is
authoritative at the moment.


## CRUD API
Create
Read
Update
Delete

## HTTP methods
DELETE
GET
PATCH
POST
PUT

## Parameters

### Pagination (global)
All lists can be controlled via pagination parameters.
example: `?limit=100&offset=400`

`limit` controls the number of entries returned
`offset` controls how deep into the list to begin the page

```
{
    "count": 482,
    "next": "http://localhost:8000/api/entities/?limit=10&offset=30",
    "previous": "http://localhost:8000/api/entities/?limit=10&offset=10",
    "results": [
```

### Filters (documented per endpoint)
each endpoint with data filters is documented with the calls. Generally the field to be filtered will support an exact match or an `icontains` (case insensitive substring) match.

Examples:
`/api/entities/?legal_name__icontains={str}` perform case insensitve substring match on `legal_name` for `{str}`

`/api/entities/?legal_name={str}` perform exact match on `legal_name` for `{str}`

## API description
Here we will describe the calls and the return values for each call.

### Authentication
`/signin/`

POST body
```
 {
  username: "USER",
  password: "PASSWORD"
}
 ```
### Company
Endpoint `/companies/`

Companies are used to group entities. It is possible for multiple entities to be a part of the same legal entity.

POST creates new company
PUT make changes to company
DELETE allowed on detail view

Detail View:
```
GET /api/companies/1/
{
    "name": "PVEL",
    "url": "http://localhost:8000/api/companies/1/",
    "website": "www.pvel.com",
    "country": "USA",
    "bio": "We make data that matters"
}
```
### Document
endpoint for all document transactions.
`/documents/`
GET - Returns heading metadata for all _available_ documents
POST - create a new document and upload file (admin only)
`/documents/{id}`
GET Returns metadata for document identified by {id}
PUT update metadata or update file

`/documents/new`
For Manufacturer users, returns the number of new documents issued in the last
DAYS_NEW days (default 30)
```
{
    "new_count": 7
}
```
For all other users, returns the top 5 newest reports available generally or by request.
```
[
    {
        "entity_display_name": "Jinko Solar",
        "issued_date": "2020-03-10",
        "title": "Jinko_R113-11C-1_PAN.PAN"
    },
    { ... }
]
```
`/documents/{id}/disclose/` (looks like there's bug with this)
changes disclosure state on document object.
    ['GENERAL','General'],
    ['BY REQUEST','By Request'],
    ['UNAVAILABLE','Undisclosed'],
    ['PENDING','Pending Authorization'],
    ['VDP','VDP']

`/documents/{id}/download/`
GET - Returns file for document identified by {id} if the requesting user has proper Permissions

401 error on no permission or not logged in

`/documents/{id}/docrequest/`
POST - create a new request for current document for the current user.
optional:
```
{
  "requestor_comment":"Hey, I want to use these for a project"
}
```
`TODO /documents/list/entity/{entity_id}`
GET - returns all documents owned by an entity identified by {entity_id}

`TODO /documents/{id}/revoke/`
POST - revoke all permissions on a report (other than my own permissions)
(changes availability to UNAVAILABLE)

```
{
    "count": 870,
    "next": "http://localhost:8000/api/documents/?limit=10&offset=10",
    "previous": null,
    "results": [
        {
            "id": 1,
            "url": "http://localhost:8000/api/documents/1/",
            "file": "http://localhost:8000/api/documents/1/download/",
            "title": "Seraphim_R10015291A-1.pdf",
            "entity": "http://localhost:8000/api/entities/308/",
            "issued_date": "2016-10-14",
            "project": "http://localhost:8000/api/projects/1/",
            "project_info": [
                {
                    "number": "10015291",
                    "type_text": "Module PQP"
                }
            ],
            "technology_tags": [
                "60 cell",
                "72 cell",
                "multi cells",
                "1000V",
                "260W",
                "300W"
            ],
            "permitted_entities": [],
            "product_type": "MODULES",
            "type": "REPORT",
            "type_text": "Report",
            "box_id": "",
            "requests": [],
            "disclosure": "GENERAL",
            "disclosure_text": "General"
        },
        {...}
        ]
}
```

Filters:
`?entity__type={str}`
`?entity__legal_name={str}`
`?entity__legal_name__icontains={str}`
`?project__number={str}`
`?project__status=[ACTIVE|INACTIVE]`
`?title={str}`
`?title__icontains={str}` case INSENSITIVE substring search
`?type=[Doctypes]` Check filters for doctypes

issued_date has date range filters:
`?issued_min=2018-01-01`
`?issued_max=2018-12-31`
of course, chain them for a full range: `?issued_min=2018-01-01&issued_max=2018-12-31`

Tags are special. they use the `in` filter to allow for more sphisticated queries.
`?tags__title__in=1000V`
will filter down to all ducuments with the 1000V tag. comma separated lists are OR:
`?tags__title__in=300W,260W`

Complex filters allow for use of AND:
`(tags__title__in=1000V)&(tags__title__in=280W,300W)` would filter doc with 1000V AND either 280W OR 300W

Complex filters need urlencoding:
`?filters=%28tags__title__in%253D1000V%29%26%28tags__title__in%253D260W%29`

### Entity
legal entity for grouping people under

`/entities/`
POST - create new entity (admin only)
GET - list of visible entities (visibility controlled by current user type)

`/entities/{id}/`
GET - entity info
PATCH - make change to existing entity (admin only)

```
GET /api/entities/
{
    "count": 482,
    "next": "http://localhost:8000/api/entities/?limit=10&offset=10",
    "previous": null,
    "results": [
        {
            "id": 1,
            "url": "http://localhost:8000/api/entities/1/",
            "company": "http://localhost:8000/api/companies/4/",
            "legal_name": "38 Degrees North DEV",
            "display_name": "38 Degrees North",
            "type": "PARTNER",
            "company_type": "DEV",
            "followers": [],
            "type_text": "Downstream Partner",
            "company_type_text": "Developer (Developer, EPC, Installer, O+M Provider)",
            "website": "https://www.38degreesn.com/",
            "country": "USA"
        },
        {...}
      ]
}
```
`/entities/{id}/follow/`
POST - empty post adds current user to "followers"

`/entities/{id}/unfollow/`
POST - empty post removes current user from "followers"

Filters:
`/api/entities/?type=[]`
`legal_name={str}`
`legal_name__icontains={str}`
Types:
`['PARTNER','CLIENT','MANUFACTURER','PVEL']`

### FAQ
FAQs are filtered based on current user entity type. On creation, FAQ `type` is set for Downstream Partners, Downstream Clients, Manufacturers, or PVEL. FAQs marked as PVEL type are visible to all users. Body data should be edited and stored using markdown.

`/faq/`
GET - retrieve questions from faq table
POST - create new FAQ question and answer (admin only)

`/faq/{faq_id}/`
GET - retrieve full faq from table
DELETE - remove FAQ entry (admin only)
PATCH - Update faq entry (admin only)

### Log
activity log (admin only)

### NewsFeed
Newsfeed items are filtered based on current user entity type. On creation, `type` is set for Downstream Partners, Downstream Clients, Manufacturers, or PVEL. Items marked as PVEL type are visible to all users. Body data should be edited and stored using markdown.

`/newsfeed/`
GET - retrieve current items from newsfeed table
POST - create new newsfeed item (admin only)

`/newsfeed/{id}/`
GET - retrieve full newsfeed item from table
DELETE - remove newsfeed item (admin only)
PATCH - Update newsfeed item (admin only)

Note: need to get design for what is "new" and whether we should have active/inactive states for newsfeed items.

### Profile
Endpoint for debugging only. Should use `/users/` to make changes to user profile.

### Project
projects contain documents

`/projects/`
POST - create new project (admin only)

GET return list of _available_ projects

`/project/{id}/`
PATCH - make change to a project (admin only)
GET - full details of project identified by {id} (TODO check visibility of projects)

Project number is generated in Salesforce
```
{
  "id": 1,
  "project number":"56757667"
  "project type":"Inverter PQP|Module PQP"
  "owner": userID
  "status":"active|inactive"
}
```

### PV Model
(future)

### Requests
this is where the user will get the list of  permission requests
CLU:
/requests/
GET - returns list of requests assigned to the current logged in user
```

```
/requests/{id}

`/requests/new`

returns the newest 5 requests created by the current user.
```
[
    {
        "status": "ACTIVE",
        "issued_date": "2020-03-10",
        "title": "Jinko_R113-11C-1_PAN.PAN"
    },
    { ... }
]
```
/request/document_id/group allow?

My requests: (request again)

Approved:
`user foo request to view document bar approved on date`

Pending:
`user foo requested access to document bar on date approve or deny?`

Rejected:
` user foo request to access document bar on request date has been denied as of denial date`

Recalled:(optional)
state for user to recall a report request

```
{
  "id":99,
  "requestor_id": 99,
  "document_id": 99,  
  "request_date": datetime,
  "status": "rejected",
  "reason": "spite"
  "status": "deprecated"
}
```
open question: do we display

for Manufacturers, when a report request is APPROVED, there will be a notification sent to the requesting user. The notification API will NOT be exposed.

for Manufacturers, when a report request is DECLINED, there will be a notification sent to the requesting user.

### Technology Tags
Maintenance endpont for managing technology tags attached to documents.

Filters:
`/api/tags/?title={str}` exact match
`/api/tags/?title__in={str}` comma separated list of tags

### User
`/users/`
GET - return list of users (admin only)
POST - create new user  (admin only)

`/users/{id}/`
GET -  retrieve all available info for the id provided
PATCH - update specified fields of user record:
```
{
    "first_name": "Jeffrey",
    "last_name": "Lebowski",
    "profile": {
        "bio": "I am the man for my time and place",
        "location": "Los Angeles",
        "birth_date": "1969-06-09"
    }
}
```
PUT - `/users/{id}/set_password`:
```
{
    "old_password": "UnoSquare",
    "new_password": "P@ssw0rd"
}
```
you will get  a 400 if the old doesn't match and:
```
{
   'old_password': ['Wrong password.']
}
```
on success:
```
{
   'status': 'password set'
}
```
be sure to refresh the session token after changing the password.

`TODO /user/{id}/activate/{key}`
POST activation {key} to activate new user


### Whoami
GET - returns the user and profile information for the currently logged in user.
```
GET /api/whoami/
{
    "count": 1,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1,
            "email": "mark.davis@pvel.com",
            "is_active": true,
            "is_staff": true,
            "is_superuser": true,
            "date_joined": "2019-11-22T22:41:03.823597Z",
            "url": "http://localhost:8000/api/users/1/",
            "username": "mdavis",
            "entities_following": [],
            "projects_following": [],
            "first_name": "",
            "last_name": "",
            "profile": null
        }
    ]
}
```
