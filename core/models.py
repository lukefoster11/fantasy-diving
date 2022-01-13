from django.db import models
from django.db.models.query_utils import PathInfo
from datetime import date

# Create your models here.
class Meet(models.Model):
    title = models.CharField(max_length=200)
    path = models.CharField(max_length=100)
    startDate = models.DateField('Start Date', default=date.today)
    endDate = models.DateField('End Date', default=date.today)
    hasResults = models.BooleanField(default=False)

    def __str__(self):
        return self.title

class Event(models.Model):
    meet = models.ForeignKey(Meet, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    entriesPath = models.CharField(max_length=100)
    date = models.DateField('Event Date', default=date.today)

    def __str__(self):
        return self.meet.title + ": " + self.title
"""
class Entry(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    diver = models.CharField(max_length=50)
    dives = models.JSONField(default=list)
"""