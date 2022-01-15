from django.contrib import admin
from .models import Meet, Event, Entry

# Register your models here.
admin.site.register(Meet)
admin.site.register(Event)
admin.site.register(Entry)