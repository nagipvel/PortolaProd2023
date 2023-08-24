from django.core.mail import EmailMultiAlternatives
from django.core.mail import EmailMessage
from django.template.loader import get_template
from django.template import Context
from portola.models import *
from datetime import datetime, timedelta
from django.conf import settings
from django.utils.timezone import make_aware

SUBJECTS ={
'account_create':"Welcome to the PVEL Portal!",
'confirm_account':"Verify your identity",
'new_document':"A new PVEL report is available",
'new_document_disclosed':"New report avalable",
'new_general':"Weekly Digest: New PVEL test reports",
'request_expired':"Your PVEL report request",
'request_pending':"PVEL report request",
'request_response':"New PVEL report request",
'reset_password':"Reset your password",
}

class Notification:
    # Using the NotificationQueue as a log
    def __init__(self):
        pass

    def throttled_email(self, **kwargs):
        # Never want to send the same subject email to the same user
        # within 15 minutes(?) should be in settings.
        resend_window = datetime.today() - timedelta(minutes=15)
        if kwargs.get('resend'):
            subject = kwargs['original_msg'].subject
            user = kwargs['original_msg'].recipient

        elif kwargs.get('template'):
            user = User.objects.get(username = kwargs['username'])
            subject = SUBJECTS.get(kwargs['template'])
        # Check the queue for a duplicate message;
        try:
            duplicate = NotificationQueue.objects.get(
                queued_date__gte = resend_window,
                recipient = user,
                subject = subject
            )
        except NotificationQueue.DoesNotExist:
            self.email_user(**kwargs)

    def email_entity(self, entity, template, items=None):
        # get all the users in the entity
        for user in userlist:
            self.email_user(username, template, items)
        pass

    def email_enveryone(self):
        # Highly dangerous
        pass

    def email_followers(self, kwargs):
        pass

    # def email_user(self, username, template, items=None, magic_link=None):
    def email_user(self, **kwargs):
        # Really need to log errors so that we can identify invalid email addresses
        # as we try to send to them.

        if kwargs.get('resend'):
            #do the needful
            note = kwargs.get('original_msg')
            subject = note.subject
            user = note.recipient
            text_content = note.text_body
            html_content = note.html_body

        else:
            plaintext = get_template(kwargs['template'] + '.txt')
            htmly     = get_template(kwargs['template'] + '.html')

            user = User.objects.get(username = kwargs['username'])
            msg_data = { 'first_name': user.first_name }
            # Sender needs to build full url for magic_links
            msg_data['magic_link'] = kwargs.get('magic_link',None)
            msg_data['items'] = kwargs.get('items',None)
            msg_data['MFR'] = kwargs.get('MFR',None)
            msg_data['user_name'] = user.username
            text_content = plaintext.render(msg_data)
            html_content = htmly.render(msg_data)
            subject = SUBJECTS[kwargs['template']]

        msg = EmailMultiAlternatives(subject,
            text_content, 'portal@pvel.com', [user.username])
        msg.attach_alternative(html_content, "text/html")
        # Need to trap errors better here
        msg.send(fail_silently=False)

        sent_message = NotificationQueue.objects.create(
            transport = 'EMAIL',
            recipient = user,
            subject = subject,
            text_body = text_content,
            html_body = html_content,
            # queued_date is automatic
            sent = True # KLUGE: Eror handling should allow for queuing
        )

    def send(self):
        # still only doing email:
        self.email.send(fail_silently=False)
