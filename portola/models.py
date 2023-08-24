from django.db import models
from django.conf import settings
#from .models import File
from portola import boxClient
from django.db.models.signals import pre_save
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.utils import timezone
# Skunkworks
import pandas as pd
import numpy as np
import pvlib
from pvlib.pvsystem import PVSystem
from pvlib.location import Location
from pvlib.modelchain import ModelChain
from datetime import datetime

BOX_FOLDER = '72911007945' #current test folder
REQUEST_EXPIRATION = 30 # days
CO_ENTITY_TYPES =[
    ['DEV','Developer (Developer, EPC, Installer, O+M Provider)'],
    ['INV','Investor (Investor, Finance Institution)'],
    ['MFG','Manufacturer'],
    ['OWN','Owner (IPP, Public Utility Company)'],
    ['EPC','Engineering, Procurement and Construction (EPC) Company'],
    ['IE','Independent Engineer (Owner\'s Engineer, Technical Advisor)'],
    ['IPP','Independent Power Producer'],
    ['SUP','Supplier'],
]
DOCUMENT_VISIBILITY = [
    ['GENERAL','General'],
    ['BY REQUEST','By Request'],
    ['UNAVAILABLE','Undisclosed'],
    ['PENDING','Pending Authorization'],
    ['VDP','VDP']
]
DOCUMENT_TYPE =[
    # ['REPORT','Report'],
    # ['RAW','Raw'],
    # ['PAN','PAN File'],
    ['MIAM','Module IAM Report'],
    # ['PANRPT', 'PAN Report'],
    # ['FER','field exposure rpt'],
    # ['FINREL','final reliability'],
    # ['interim1 reliability','interim1 reliability'],
    # ['interim2','interim2' ],
    # ['LID','LID'],
    ['INTAKE','Intake'],
    ['FWR','Factory Witness Report'],
    # ['financials(VDP)','financials(VDP)'],
    ['IFT','Inverter Field Testing - Other'],
    ['IPQPF','Inverter PQP Final'],
    ['IPQPILT','Inverter PQP Interim'],
    ['MFT','Module Field Testing - Other'],
    ['MINTAKE','Module Intake'],
    ['MLID','Module LID'],
    ['MDML','Module Mechanical Load (Static, Dynamic, Other)'],
    ['MNOCT','Module NOCT'],
    ['MPANF','Module PAN File'],
    ['MPANR','Module PAN Report'],
    ['MPID','Module PID Testing'],
    ['MPQPF','Module PQP Final'],
    ['MPQPFE','Module PQP Field Exposure'],
    ['MPQPI1','Module PQP Interim 1'],
    ['MPQPI2','Module PQP Interim 2'],
    ['MPQPI3','Module PQP Interim 3'],
    ['MISC','Miscellaneous'],
    ['MCEY','Module Comparative Energy Yield'],
    ['RIE','Racking Installation Efficiency'],
    ['BDSI','Backsheet Durability Sequence Interim'],
    ['BDS','Backsheet Durability Sequence Final'],
    ['ER','Engineering Report'],
    ['RTR','Racking or Tracker Report'],
    ['ESPQPI','Energy Storage PQP Interim'],
    ['ESPQPF','Energy Storage PQP Final'],
    # ['ESFW','Energy Storage Factory Witness'],
    # ['IFW','Inverter Factory Witness'],
    ['MPQPFEI','Module PQP Interim Field Exposure'],
    ['MLETID','Module LeTID '],
]

ENTITY_TYPES =[
    ['PARTNER','Downstream Partner'],
    ['CLIENT','Downstream Client'],
    ['MANUFACTURER','Manufacturer'],
    ['PVEL','PVEL'],
]
PRODUCT_TYPES=[
    ['modules','Modules'],
    ['racking','Racking'],
    ['inverter','Inverter'],
    ['optimizer','Optimizer'],
    ['Power Electronics','Power Electronics'],
    ['ess','Energy Storage System'],
]
PROJECT_CHOICES = [
    ['DS','Data Services (Includes SSD participants)'],
    ['ENGSC','Eng Services/ Strategic Consulting'],
    ['FAT','Factory Acceptance Testing'],
    ['GOVGRNT','Government Grants'],
    ['IFT','Inverter Field Testing (customer site)'],
    ['IMISC','Inverter Other (Includes RSD, AFCI)'],
    ['IPQP','Inverter PQP'],
    ['MFT','Module Field Testing (customer site)'],
    ['MHTMI','Module HTMI'],
    ['MMISC','Module Other'],
    ['MFPID','Module Flash, PAN, IAM, DML'],
    ['MPQP','Module PQP'],
    ['PVUSA','PV-USA (Includes Tracker/CEY)'],
    ['REFC','Ref Cells'],
    ['SMISC','Storage Other'],
    ['SPQP','Storage PQP'],
    ['SBURN','Storage - Burn'],
    ['PEO','Power Electronics Other']
]

PROJECT_STATUS = [
    ['ACTIVE','ACTIVE'],
    ['INACTIVE','INACTIVE'],
]

REQUEST_STATUS = [
    ['ACTIVE','ACTIVE'],
    ['APPROVED','APPROVED'],
    ['REFUSED','REFUSED'],
    ['EXPIRED','EXPIRED'],
]
TAG_TYPES =[
    ['Tracker Type','Tracker Type'],
    ['Racking Type','Racking Type'],
    ['Power Bin','Power Bin'],
    ['Mounting Type','Mounting Type'],
    ['Misc','Misc'],
    ['Max Voltage','Max Voltage'],
    ['Inverter Type','Inverter Type'],
    ['Cell Type','Cell Type'],
    ['Cell Count','Cell Count'],
    ['Cell Chemistry','Cell Chemistry'],
    ['Battery Type','Battery Type'],
    ['Battery Testing','Battery Testing'],
]
TEMPLATE_FORMATS =[['text','text'],['html','html']]
TRANSPORT_TYPES = [['EMAIL','EMAIL']]

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)

# these are for us to write and for users to accept
class Agreement(models.Model):
    # these have a couple of uses:
    #  Agree to terms
    #  Agree to view?
    # agreement date
    text = models.TextField(max_length=500, blank=True)

class Company(models.Model):
    name = models.CharField(max_length=100, blank=False, null=False)
    website = models.CharField(max_length=255, blank=True, default='')
    country = models.CharField(max_length=100, blank=True, default='')
    bio = models.TextField(max_length=500, blank=True)

    class Meta:
        ordering = ('name',)

    def __str__(self):
        # return str(self.name)
        return "{}".format(self.name)

class Document(models.Model):
    file = models.FileField(blank=False, null=False)
    name = models.CharField(max_length=100, blank=False, null=False)
    created = models.DateTimeField(auto_now_add=True)
    title = models.CharField(db_index=True, max_length=100, blank=False, null=False)
    entity = models.ForeignKey('Entity',
        blank=False, null=False, on_delete=models.CASCADE)
    bom = models.CharField(max_length=32, blank=True, null=True)
    type = models.CharField(db_index=True, choices=DOCUMENT_TYPE, default='REPORT', max_length=32)
    # TODO: Replace document_project with document_set
    project = models.ForeignKey('Project',
        related_name='document_project',
        blank=False, null=False, on_delete=models.CASCADE)
    issued_date = models.DateField(db_index=True, default=timezone.now)
    technology_tags = models.ManyToManyField('TechnologyTag',related_name='documents')
    product_type = models.CharField(db_index=True, choices=PRODUCT_TYPES, default='MODULES', max_length=32)
    permitted_entities = models.ManyToManyField('Entity',related_name='permitted_entities', blank=True)
    # owner = models.ForeignKey('auth.User', related_name='documents', on_delete=models.CASCADE)
    box_id = models.CharField(max_length=30, blank=True, default='')
    disclosure = models.CharField(db_index=True, choices=DOCUMENT_VISIBILITY, default='PENDING', max_length=100)
    disclosure_date = models.DateField(blank=True, null=True)
    factory_witness_date = models.DateField(blank=True, null=True)

    class Meta:
        ordering = ['-issued_date',]

    def __str__(self):
        # return self.file.name
        return "{}".format(self.file.name)

    # @staticmethod
    # def pre_save(sender, instance, **kwargs):
    #     myClient = boxClient.boxClient()
    #     print(instance.file)
    #     instance.box_id = myClient.uploadFile(BOX_FOLDER,instance.file)

    # def save(self, *args, **kwargs):
        # this is where we need to make sure that we get the file up
        # to box
        # https://www.django-rest-framework.org/api-guide/parsers/#fileuploadparser
        #KLUGE: Shouldn't need to save twice
        # super(Document, self).save(*args, **kwargs)


# def document_presave(sender, **kwargs):
#     print(**kwargs)
#
# pre_save.connect(Document.pre_save, sender=Document)
# #
# @receiver(pre_save, sender=Document)
# def my_callback(sender, instance, *args, **kwargs):

class Entity(models.Model):
    # many users to each entity
    created_by = models.ForeignKey('auth.User', blank=True, null=True, on_delete=models.CASCADE)
    company = models.ForeignKey('company', blank=False, null=False, on_delete=models.CASCADE)
    display_name = models.CharField(max_length=100, blank=False, null=False)
    legal_name = models.CharField(db_index=True, max_length=100, blank=False, unique=True)
    type = models.CharField(db_index=True, choices=ENTITY_TYPES, default='PARTNER', max_length=100)
    website = models.CharField(max_length=255, blank=True, default='')
    country = models.CharField(max_length=100, blank=True, default='')
    followers = models.ManyToManyField('auth.User',related_name='entities_following')
    company_type = models.CharField(choices=CO_ENTITY_TYPES, default="MFG", max_length=100)
    public = models.BooleanField(default=True, blank=False, null=False)
    # any other contact info?

    class Meta:
        ordering = ('legal_name',)

    def __str__(self):
        # return self.legal_name
        return "{}".format(self.legal_name)

class Faq(models.Model):
    last_updated = models.DateTimeField(auto_now_add=True)
    last_updated_by = models.ForeignKey('auth.User', related_name='faq_updated_by', on_delete=models.CASCADE)
    created_by = models.ForeignKey('auth.User', related_name='faq_created_by', on_delete=models.CASCADE)
    subject =  models.CharField(max_length=100, blank=True, default='')
    body = models.TextField()
    section = models.CharField(max_length=100, blank=True, default='')
    type = models.CharField(choices=ENTITY_TYPES, default='PVEL', max_length=100)

    class Meta:
        ordering =('subject',)

    def __str__(self):
        # return self.subject
        return "{}".format(self.subject)

class Follow(models.Model):
    # arbitrary in design, in practice, Project or MFG only
    # All users in an entity should see follow relationship TODO
    # Reports need to display differently if I'm following it
    # On document list need to reflect "followed = True"
    create_date = models.DateTimeField(db_index=True, )
    follower = models.ForeignKey('auth.User', related_name='following', on_delete=models.CASCADE)

    class Meta:
        ordering = ('create_date',)

    def __str__(self):
        # return self.create_date
        return "{}".format(self.create_date)

class NewsFeed(models.Model):
    last_updated = models.DateTimeField(auto_now_add=True)
    last_updated_by = models.ForeignKey('auth.User', related_name='newsfeed_updated_by', on_delete=models.CASCADE)
    created_by = models.ForeignKey('auth.User', related_name='newsfeed_created_by', on_delete=models.CASCADE)
    subject =  models.CharField(max_length=100, blank=True, default='')
    body = models.TextField()
    type = models.CharField(choices=ENTITY_TYPES, default='PVEL', max_length=100)

    class Meta:
        ordering =('subject',)

    def __str__(self):
        # return self.subject
        return "{}".format(self.subject)

class NotificationQueue(models.Model):
    # KLUGE:
    # Repurposing this queue to be a log and a way to check "if sent since"
    transport = models.CharField(choices=TRANSPORT_TYPES, default='EMAIL', max_length=8)
    recipient = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    subject = models.CharField(db_index=True, max_length=255, blank=True, default='')
    text_body = models.TextField(blank=True, default='')
    html_body = models.TextField(blank=True, default='')
    queued_date = models.DateTimeField(auto_now_add=True)
    sent = models.BooleanField(default=False)

    class Meta:
        ordering =('queued_date',)

    def __str__(self):
        return "{}".format(self.subject)

class Project(models.Model):
    document_approver = models.ForeignKey('auth.User', related_name='document_approver', blank=False, null=False, on_delete=models.CASCADE)
    number = models.CharField(db_index=True, max_length=16, blank=False, null=False)
    status = models.CharField(db_index=True, choices=PROJECT_STATUS, default='ACTIVE', max_length=100)
    salesforce_id = models.CharField(max_length=10, blank=True, null=True)
    name = models.CharField(max_length=32, blank=True, null=True)
    contract_signature = models.DateField(null=True, blank=False)
    # TODO: This is not a real database field. It's calculated by the serializer. REMOVEME
    last_document_date = models.DateField(null=True, blank=False)
    customer = models.ForeignKey('Entity',
        # related_name='entity',
        on_delete=models.CASCADE, blank=False, null=False)
    primary_contact = models.ForeignKey('auth.User',
        # related_name='primary_contact',
        on_delete=models.CASCADE, blank=False, null=False)
    # additional_contacts = multi
    pvel_manager = models.ForeignKey('auth.User', related_name='pvel_manager', on_delete=models.CASCADE, blank=False, null=False)
    type = models.CharField(db_index=True, choices=PROJECT_CHOICES, default='MPQP', max_length=100)
    # documents = models.ManyToManyField('Documents',related_name='projects')
    followers = models.ManyToManyField('auth.User',related_name='projects_following')

    class Meta:
        ordering = ('number',)

    def __str__(self):
        # return self.number
        return "{}".format(self.number)

# class Subscription(models.Model):
#     # used to match template for send in email.py
#     template = models.CharField(max_length=30, blank=False, null=False)
#     # for the eventual dashboard that allows for users to subscribe/unsubscribe
#     entity_type = models.CharField(db_index=True, choices=ENTITY_TYPES, default='PARTNER', max_length=100)
#     # for the eventual dashboard that allows for users to subscribe/unsubscribe
#     description = models.CharField(max_length=500, blank=True, null=True)
#
#     class Meta:
#         ordering = ('user',)
#
#     def __str__(self):
#         return "{}".format(self.template)

class Profile(models.Model):
    # I want to use the built in staff and superusers for control
    user = models.OneToOneField('auth.User', blank=False, null=False, on_delete=models.CASCADE)
    entity = models.ForeignKey('Entity',
        # related_name='profile_entity',
        blank=False, null=False, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True) #this may go away
    location = models.CharField(max_length=30, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    box_user = models.CharField(max_length=30, blank=True)
    # subscriptions = models.ManyToManyField('Subscription', blank=True)
    #agreements = models.ForeignKey('Agreement', related_name='profile', on_delete=models.CASCADE)

    class Meta:
        ordering = ('user',)

    def __str__(self):
        return "{}".format(self.user)

class PVModel(models.Model):
    # Skunkworks :)
    created_by = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    latitude = models.DecimalField(max_digits=5, decimal_places=2)
    longitude = models.DecimalField(max_digits=5, decimal_places=2)
    surface_tilt = models.DecimalField(max_digits=5, decimal_places=2)
    surface_azimuth = models.DecimalField(max_digits=5, decimal_places=2)
    # module_parameters
    # inverter_parameters

    def runmodel(self):
        sandia_modules = pvlib.pvsystem.retrieve_sam('SandiaMod')
        cec_inverters = pvlib.pvsystem.retrieve_sam('cecinverter')
        sandia_module = sandia_modules['Canadian_Solar_CS5P_220M___2009_']
        cec_inverter = cec_inverters['ABB__MICRO_0_25_I_OUTD_US_208_208V__CEC_2014_']
        location = Location(latitude=self.latitude, longitude=self.longitude)

        system = PVSystem(
            surface_tilt= self.surface_tilt,
            surface_azimuth = self.surface_azimuth,
            module_parameters=sandia_module,
            inverter_parameters=cec_inverter,
            )
        mc = ModelChain(system,location)
        return mc

# Lifted from https://simpleisbetterthancomplex.com/tutorial/2016/07/22/how-to-extend-django-user-model.html#onetoone
# @receiver(post_save, sender=User)
# def create_user_profile(sender, instance, created, **kwargs):
#     if created:
#         Profile.objects.create(user=instance)
#
# @receiver(post_save, sender=User)
# def save_user_profile(sender, instance, **kwargs):
#     instance.profile.save()
def _request_expiration():
    return timezone.now() + timezone.timedelta(days=REQUEST_EXPIRATION)

class Request(models.Model):
    # two types of reports: User to mfg (Can *I* see this by request report)
    # From PVEL (Cane *WE* make this report generally available)
    requestor = models.ForeignKey('auth.User', related_name='requests', on_delete=models.CASCADE,blank=False, null=False)
    created = models.DateTimeField(auto_now_add=True)
    resolved = models.DateField(null=True, blank=True)
    expires = models.DateField(db_index=True, default=_request_expiration, blank=False, null=False) # default expiry 90, tickle after 14 days
    last_updated = models.DateTimeField(auto_now_add=True)
    status = models.CharField(db_index=True, choices=REQUEST_STATUS, default='ACTIVE', max_length=100)
    document = models.ForeignKey('Document', related_name='requests', on_delete=models.CASCADE, blank=False, null=False)
    requestor_comment = models.TextField(null=True, blank=True)
    approver_comment = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return "{}".format(self.document)

class TechnologyTag(models.Model):
    title = models.CharField(db_index=True, max_length=64, blank=False)
    type = models.CharField(db_index=True, choices=TAG_TYPES, default='Power Bin', max_length=32)

    class Meta:
        ordering = ('type','title',)

    def __str__(self):
        return "{0} - {1}".format(self.type, self.title)
