from django.db import models
from django.db.models.query_utils import PathInfo

# Create your models here.
class Meet(models.Model):
    title = models.CharField(max_length=200)
    path = models.CharField(max_length=100)
    startDate = models.DateField
    endDate = models.DateField
    hasResults = models.BooleanField

class Event(models.Model):
    meet = models.ForeignKey(Meet, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    entriesPath = models.CharField(max_length=100)
    date = models.DateField

class Entry(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    diver = models.CharField(max_length=50)
    dives = models.JSONField
