from django.core.management.base import BaseCommand, CommandError
from portola.models import *
from django.contrib.auth.models import User
from datetime import datetime, timedelta, date
from portola.email import Notification

class Command(BaseCommand):
    help = 'performs email tending'
    MONTH = 30
    WEEK = 7

    DOCUMENT_DICT = dict(DOCUMENT_TYPE)
    PROJECT_DICT = dict(PROJECT_CHOICES)
    ENTITY_TYPES = dict(CO_ENTITY_TYPES)

    last_month = datetime.today() - timedelta(days=MONTH)
    last_week = datetime.today() - timedelta(days=WEEK)
    yesterday = datetime.today() - timedelta(days=1)

    epoch = date(2020,5,3) # first sunday of May 2020

    def handle(self, *args, **options):
        self.new_document() # new_document (daily)
        self.request_expired() # request_expired
        self.request_response() # request_response
        self.new_disclosure() # new_document_disclosed (daily)
        if (epoch - date.today()).days % 7 == 0: # do the sunday night stuff
            self.request_pending() # request pending (weekly)
            self.new_general() # new_general (weekly, sunday night)

    def fix_tags(self, tags):
        taglist = []
        for tag in tags:
            taglist.append(tag.title)
        sep = ", "
        return sep.join(taglist)

    def request_expired(self):
        """
        marks requests exipred, sends an email
        One email, one row per request marked expired.
        """
        for user in User.objects.all():
            # find all the requests for this user
            requests_qs = Request.objects.filter(requestor = user)
            requests_qs = requests_qs.filter(status = "ACTIVE")
            requests_qs = requests_qs.filter(created__lte = self.last_month)
            email_rows = []
            for request in requests_qs:
                # these are all my active requests that are more than 30 days_old
                request.status = 'EXPIRED'
                request.save()
                document = request.document
                email_rows.append({
                    'entity': document.entity.display_name,
                    'title': document.title,
                    'project_number':document.project.number,
                    'document_type': self.DOCUMENT_DICT[document.type],
                    'issued_date':document.issued_date,
                    'tags': self.fix_tags(document.technology_tags.all()),
                })

            if email_rows:
                note = Notification()
                note.email_user(username=user.username,
                    template='request_expired',
                    items=email_rows)

    def request_response(self):
        """
        sends emails when requests are resolved in the last day
        """
        for user in User.objects.all():
            # find all the requests for this user
            requests_qs = Request.objects.filter(requestor = user)
            requests_qs = requests_qs.exclude(status = "ACTIVE")
            requests_qs = requests_qs.filter(resolved__gte = self.yesterday)
            email_rows = []
            for request in requests_qs:
                document = request.document
                email_rows.append({
                    'entity': document.entity.display_name,
                    'status': request.status,
                    'comment': request.approver_comment,
                    'title': document.title,
                    'date': request.created,
                    'type': self.DOCUMENT_DICT[document.type],
                    # 'issued_date':document.issued_date,
                    'tags': self.fix_tags(document.technology_tags.all()),
                })

            if email_rows:
                note = Notification()
                note.email_user(username=user.username,
                    template='request_response',
                    items=email_rows)

    def new_disclosure(self):
        """
        checks companies you're following for new documents
        """
        # for every user:
        for user in User.objects.all():
            # for every user:
            email_rows = []
            for entity in user.entities_following.all():
                # Show me the documents that entity owns
                documents = entity.document_set.all()
                documents = documents.exclude(disclosure = 'PENDING')
                # this logic might be wrong.
                documents = documents.filter(disclosure_date__gte = self.yesterday)
                for document in documents:
                    email_rows.append({
                        'entity': document.entity.display_name,
                        'title': document.title,
                        'project_number':document.project.number,
                        'document_type': self.DOCUMENT_DICT[document.type],
                        'issued_date':document.issued_date,
                        'tags': self.fix_tags(document.technology_tags.all()),
                    })
            if email_rows:
                note = Notification()
                note.email_user(username=user.username,
                    template='new_document_disclosed',
                    items=email_rows)

    def new_general(self):
        """
        checks for new GENERAL documents disclosed in the last week.
        """
        # for every DSP or DSC:
        documents = Document.objects.filter(disclosure = 'GENERAL')
        documents = documents.filter(disclosure_date__gte = self.last_week)

        for entity in Entity.objects.filter(type__in= ['PARTNER','CLIENT']):
            # for every user:
            for profile in entity.profile_set.all():
                email_rows = []
                for document in documents:
                    email_rows.append({
                        'entity': document.entity.display_name,
                        'title': document.title,
                        'project_number':document.project.number,
                        'document_type': self.DOCUMENT_DICT[document.type],
                        'issued_date':document.issued_date,
                        'tags': self.fix_tags(document.technology_tags.all()),
                    })
                if email_rows:
                    note = Notification()
                    note.email_user(username=profile.user.username,
                        template='new_general',
                        items=email_rows)

    def request_pending(self):
        """
        lets the mfr know there is a pending request waiting for their action
        """
        # for every company:
        for entity in Entity.objects.all():
            # for every user:
            for profile in entity.profile_set.all():
                # Show me the projects they own
                # Projects you manage have documents pending disclosure:
                email_rows = []
                for project in profile.user.project_set.all():
                    documents = project.document_project.filter(disclosure = 'BY REQUEST') # ??
                    for document in documents:
                        for request in document.requests.all():
                            if request.status == "ACTIVE":
                                print(request)
                                # days_old = datetime.today().date() - document.issued_date
                                email_rows.append({
                                    'date': request.created,
                                    'title': document.title,
                                    'entity': request.requestor.profile.entity.display_name,
                                    'cotype': self.ENTITY_TYPES[request.requestor.profile.entity.company_type],
                                    'comment': request.requestor_comment,
                                    'type':self.DOCUMENT_DICT[request.document.type]
                                })
                if email_rows:
                    print(email_rows)
                    note = Notification()
                    note.email_user(username=profile.user.username,
                        template='request_pending',
                        items=email_rows)

    def new_document(self):
        """
        This one sends email for all reports sitting in "PENDING" status
        One email, one row per document waiting for action.
        """
        # for every company:
        for entity in Entity.objects.all():
            # for every user:
            for profile in entity.profile_set.all():
                # Show me the projects they own
                # Projects you manage have documents pending disclosure:
                email_rows = []
                for project in profile.user.project_set.all():
                    documents = project.document_project.filter(disclosure = 'PENDING')
                    # this would limit to new within the last seven days
                    # documents = documents.filter(issued_date__lte = self.last_week)
                    for document in documents:
                        days_old = datetime.today().date() - document.created
                        email_rows.append({
                        'number':document.id,
                        'title':document.title,
                        'project_number':project.number,
                        'project_type_text':self.PROJECT_DICT[project.type],
                        'issued_date':document.issued_date,
                        'document_type':self.DOCUMENT_DICT[document.type],
                        })
                        # print(profile.user)
                        # print(document.title)
                if email_rows:
                    note = Notification()
                    note.email_user(username=profile.user.username,
                        template='new_document',
                        items=email_rows)
                    # documents = Document.objects.filter(disclosure = 'PENDING').filter()
                    # print(documents)
                    # print(project.document_set.all())
