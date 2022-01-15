from django.db import models
from django.db.models.query_utils import PathInfo
from django.contrib.postgres.fields import ArrayField
from datetime import date

# Create your models here.
class Meet(models.Model):
    meetid = models.IntegerField(default=0, unique=True)
    title = models.CharField(max_length=200)
    startDate = models.DateField('Start Date', default=date.today)
    endDate = models.DateField('End Date', default=date.today)
    hasResults = models.BooleanField(default=False)

    def __str__(self):
        return self.title

class Event(models.Model):
    meet = models.ForeignKey(Meet, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    date = models.DateField('Event Date', default=date.today)

    def __str__(self):
        return self.meet.title + ": " + self.title

class Entry(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    diver = models.CharField(max_length=50)
    dives = ArrayField(models.CharField(max_length=5))
    
    def __str__(self):
        return self.event.meet.title + ": " + self.event.title + ": " + self.diver
