from __future__ import unicode_literals
from django.contrib.auth.models import User
from django.db import models
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from datetime import datetime


class Users(models.Model):
    user = models.ForeignKey(User)
    full_name = models.TextField()
    email = models.TextField(unique=True)
    mobile_number = models.TextField(unique=True)
    role = models.TextField()
    gender = models.TextField(null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    password = models.TextField()


class Token(models.Model):
    token = models.CharField(max_length=50, null=True, blank=True)
    user = models.ForeignKey(Users)
    role = models.CharField(max_length=50, null=True, blank=True)


def upload_location(instance, filename):
    return "%s/%s" % ("celebrity", filename)


class CelebrityDetails(models.Model):
    image_path = models.FileField(upload_to=upload_location, storage=FileSystemStorage(location=settings.MEDIA_ROOT),
                                  null=True, blank=True)
    video_url = models.TextField(null=True, blank=True)
    title = models.TextField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    language = models.TextField(default="all", null=True, blank=True)
    page = models.TextField()
    source = models.TextField(null=True, blank=True)
    source_link = models.TextField(null=True, blank=True)


class CelebritySchedules(models.Model):
    event = models.TextField()
    at = models.DateTimeField()
    language = models.TextField(default="all", null=True, blank=True)


class PublicSuggestions(models.Model):
    user = models.ForeignKey(Users)
    suggestion = models.TextField()
    publish = models.BooleanField(default=False)
    at = models.DateTimeField(default=datetime.now())


class SocialMedias(models.Model):
    social = models.TextField()
    social_id = models.TextField()

class BookingPrice(models.Model):
    price = models.BigIntegerField(null=True, blank=True)
    startdate= models.DateField(null=True, blank=True)
    enddate = models.DateField(null=True, blank=True)
    status = models.BooleanField(default=False)

class BookingCottage(models.Model):
    client_id = models.TextField()
    startdate = models.DateField(null=True, blank=True)
    enddate = models.DateField(null=True, blank=True)
    status = models.TextField(default='available')
    name = models.TextField(null=True, blank=True)
    mobilenumber = models.TextField(null=True, blank=True)
    email = models.TextField(null=True, blank=True)
    gstno = models.TextField(null=True, blank=True)
    companyname = models.TextField(null=True, blank=True)
    companyaddress = models.TextField(null=True, blank=True)
    roomprice = models.IntegerField(null=True, blank=True)
    gst = models.IntegerField(null=True, blank=True)
    ccavenue = models.IntegerField(null=True, blank=True)
    totalprice = models.IntegerField(null=True, blank=True)
    paymentstatus = models.TextField(default='pending')
    nights = models.IntegerField(null=True, blank=True)


class Purohits(models.Model):
    p_id=models.TextField(unique=True)
    purohit_name=models.TextField(null=True,blank=True)
    purohit_mobile_number=models.TextField(unique=True)
    address=models.CharField(max_length=50, null=True, blank=True)
    is_active=models.BooleanField(default=True)
    user = models.ForeignKey(User)


class Materials(models.Model):
    m_id=models.TextField(unique=True)
    material_name=models.CharField(max_length=50,unique=True)
    category=models.CharField(max_length=50,null=True, blank=True)


class Function_halls(models.Model):
    name=models.CharField(max_length=50)
    address=models.TextField(null=True,blank=True)


class EventRequests(models.Model):
    event_id=models.CharField(max_length=50,unique=True)
    client_mobile_number=models.TextField()
    client_name=models.TextField(null=True,blank=True)
    event_name=models.TextField()
    event_start_date=models.CharField(max_length=50,blank=True, null=True)
    event_end_date=models.CharField(max_length=50,blank=True,null=True)
    event_place=models.TextField(null=True,blank=True)
    status=models.CharField(max_length=50, default='PENDING')


class AssignThingsToEvent(models.Model):
    event_id=models.CharField(max_length=50)
    client_number=models.TextField()
    p_id = models.TextField(null=True,blank=True)
    purohit_name = models.TextField(null=True, blank=True)
    purohit_mobile_number = models.TextField(null=True,blank=True)
    m_id = models.TextField(null=True,blank=True)
    material_name = models.CharField(max_length=50, null=True, blank=True)


class Category(models.Model):
    type=models.CharField(max_length=50)


class Event_names(models.Model):
    name=models.CharField(max_length=50)
    type=models.CharField(max_length=50)