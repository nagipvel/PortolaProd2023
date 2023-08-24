
from django.db import migrations, models
# from django.contrib.auth.admin import User
from django.contrib.auth.models import User

USERS = [
    ['mdavis','mark.davis@pvel.com','P@ssw0rd','Mark','Davis'],
    ['rlopez','rene.lopez@unosquare.com','P@ssw0rd','Rene','Lopez'],
    ['drdreff@gmail.com','drdreff@gmail.com','P@ssw0rd','Mark','Davis (test user)'],
    ['adam.gushansky@pvel.com','Adam.Gushansky@pvel.com','P@ssw0rd','Adam','Gushansky'],
    ['alisan.varney@pvel.com','Alisan.Varney@pvel.com','P@ssw0rd','Alisan','Varney'],
    ['emily.teamo@pvel.com','emily.teamo@pvel.com','P@ssw0rd','Emily','te Amo'],
    ['jeff.cleland@pvel.com','Jeff.Cleland@pvel.com','P@ssw0rd','Jeff','Cleland'],
    ['priyanka.mogre@pvel.com','priyanka.mogre@pvel.com','P@ssw0rd','Priyanka','Mogre'],
    ['ryan.desharnais@pvel.com','ryan.desharnais@pvel.com','P@ssw0rd','Ryan','Desharnais'],
    ['tara.doyle@pvel.com','tara.doyle@pvel.com','P@ssw0rd','Tara','Doyle'],
]
COMPANY = [1,'PVEL','www.pvel.com','USA','We make data that matters']
ENTITY = [1,'PVEL','PVEL','www.pvel.com','USA',1]

TAGS =[
    # ['single axis tracker','Tracker Type'],
    # ['double axis tracker','Tracker Type'],
    ['flat racking product','Racking Type'],
    ['250W','Power Bin'],
    ['255W','Power Bin'],
    ['260W','Power Bin'],
    ['265W','Power Bin'],
    ['270W','Power Bin'],
    ['275W','Power Bin'],
    ['280W','Power Bin'],
    ['285W','Power Bin'],
    ['290W','Power Bin'],
    ['295W','Power Bin'],
    ['300W','Power Bin'],
    ['305W','Power Bin'],
    ['310W','Power Bin'],
    ['315W','Power Bin'],
    ['320W','Power Bin'],
    ['325W','Power Bin'],
    ['330W','Power Bin'],
    ['335W','Power Bin'],
    ['340W','Power Bin'],
    ['345W','Power Bin'],
    ['350W','Power Bin'],
    ['355W','Power Bin'],
    ['360W','Power Bin'],
    ['365W','Power Bin'],
    ['370W','Power Bin'],
    ['375W','Power Bin'],
    ['380W','Power Bin'],
    ['385W','Power Bin'],
    ['390W','Power Bin'],
    ['395W','Power Bin'],
    ['400W','Power Bin'],
    ['405W','Power Bin'],
    ['410W','Power Bin'],
    ['415W','Power Bin'],
    ['420W','Power Bin'],
    ['425W','Power Bin'],
    ['430W','Power Bin'],
    ['435W','Power Bin'],
    ['440W','Power Bin'],
    ['445W','Power Bin'],
    ['450W','Power Bin'],
    ['rooftop mounting system','Mounting Type'],
    # ['ground mount racking','Mounting Type'],
    ['fixed tilt racking product','Mounting Type'],
    # ['tracker racking product','Mounting Type'],
    ['bifacial','Misc'],
    ['glass-glass','Misc'],
    ['Transparent Backsheet','Misc'],
    ['half cut cell','Misc'],
    ['residential','Misc'],
    ['158.75 mm wafer edge length','Misc'],
    ['Shingled','Misc'],
    ['commercial rooftop mounting system','Misc'],
    ['600V','Max Voltage'],
    ['1000V','Max Voltage'],
    ['1500V','Max Voltage'],
    ['micro inverter','Inverter Type'],
    ['string inverter','Inverter Type'],
    ['3-phase string inverter','Inverter Type'],
    ['utility inverter','Inverter Type'],
    ['mono cells','Cell Type'],
    ['multi cells','Cell Type'],
    ['Bifacial cells','Cell Type'],
    ['Mono PERC','Cell Type'],
    ['Poly PERC','Cell Type'],
    # ['M4','Cell Type'],
    ['M6','Cell Type'],
    # ['M12','Cell Type'],
    ['60 cell','Cell Count'],
    ['66 cell','Cell Count'],
    ['72 cell','Cell Count'],
    ['120 cell','Cell Count'],
    ['144 cell','Cell Count'],
    ['96 cell','Cell Count'],
    ['128 cell','Cell Count'],
    ['non-crysalline-Si cells','Cell Chemistry'],
    ['HIT','Cell Chemistry'],
    ['n-type','Cell Chemistry'],
    # ['MBB','Cell Chemistry'],
    ['CdTe','Cell Chemistry'],
    ['CIS','Cell Chemistry'],
    ['a-Si cell','Cell Chemistry'],
    # ['lithium ion battery','Battery Type'],
    # ['lithium other battery','Battery Type'],
    # ['flow','Battery Type'],
    # ['lead acid battery','Battery Type'],
    # ['other','Battery Type'],
    # ['battery cell testing','Battery Testing'],
    # ['battery module testing','Battery Testing'],
    # ['battery pack testing','Battery Testing'],
    # ['battery system testing','Battery Testing'],
]

def addUsers(apps, schema_editor):
    Company = apps.get_model("portola", "Company")
    Entity = apps.get_model("portola", "Entity")

    myCompany = Company()
    myCompany.name = COMPANY[1]
    myCompany.website = COMPANY[2]
    myCompany.country = COMPANY[3]
    myCompany.bio = COMPANY[4]
    myCompany.save()

    myEntity = Entity()
    myEntity.legal_name = ENTITY[1]
    myEntity.type = ENTITY[2]
    myEntity.website = ENTITY[3]
    myEntity.country = ENTITY[4]
    myEntity.company = myCompany
    myEntity.save()

    for row in USERS:
        superuser = User.objects.create_user(row[0],row[1],row[2])
        superuser.first_name = row[3]
        superuser.last_name = row[4]
        superuser.is_active = True
        superuser.is_superuser = True
        superuser.is_staff = True
        superuser.save()



def addTags(apps, schema_editor):
    myTag = apps.get_model("portola", "TechnologyTag")
    for row in TAGS:
        # tag = myTag.objects.create(title=row[0],type=row[1])
        tag = myTag()
        tag.title = row[0]
        tag.type = row[1]
        tag.save()

class Migration(migrations.Migration):

    dependencies = [
        ('portola', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(addUsers),
        migrations.RunPython(addTags),
    ]
