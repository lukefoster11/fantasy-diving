from django.contrib import admin
from .models import Dive, FantasyEntry, Meet, Event, Entry, DiveInstance

# Register your models here.
admin.site.register(Meet)
admin.site.register(Event)
admin.site.register(Entry)
admin.site.register(DiveInstance)
admin.site.register(FantasyEntry)