from django.shortcuts import get_object_or_404, render, get_list_or_404
from django.http import HttpResponse
from django.db.utils import IntegrityError
from datetime import date
from .models import Meet, Event, Entry
import divescrape


# Create your views here.
def overview(request):
    meets = divescrape.getMeets()
    for meet in meets:
        try:
            Meet(meetid = meet.id, title = meet.title, startDate = meet.startDate, 
                endDate = meet.endDate, hasResults = meet.hasResults).save()
            print(f"{meet.title} added successfully")
        except IntegrityError:
            # TODO: update existing meets
            print("meet already exists")
    
    # TODO: remove cancelled meets

    current_meets = Meet.objects.filter(startDate__lte=date.today()).filter(endDate__gte=date.today())
    upcoming_meets = Meet.objects.filter(startDate__gt=date.today())
    context = {'current_meets': current_meets, 'upcoming_meets': upcoming_meets}
    return render(request, 'core/overview.html', context)

def events(request, meet_id):
    # Get meet info from db
    meet = get_object_or_404(Meet, pk=meet_id)
    dsmeet = divescrape.Meet(meet.meetid, meet.title, meet.startDate, meet.endDate, meet.hasResults)
    dsevents = dsmeet.getEvents()

    # Generate events for meet, and add/update them to db
    for event in dsevents:
        exists = Event.objects.filter(meet=meet).filter(title=event.title)
        if not exists:
            Event(meet = meet, title = event.title, date = event.date, entriesPath = event.entriesPath).save()
            print(f"{event.title} added successfully")
        else:
            # TODO: update existing events
            print("event already exists")    

    # TODO: check for events removed from meet      

    return render(request, 'core/events.html', {'meet': meet})

# TODO: fix for hasResults=True events
def entries(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    meet = event.meet
    dsmeet = divescrape.Meet(meet.meetid, meet.title, meet.startDate, meet.endDate, meet.hasResults)
    dsevent = divescrape.Event(event.title, event.entriesPath, event.date, dsmeet)
    dsentries = dsevent.getEntries()

    for entry in dsentries:
        exists = Entry.objects.filter(event=event).filter(diver=entry.diver)
        if not exists:
            Entry(event = event, diver = entry.diver, dives = entry.dives).save()
            print(f"{entry.diver}'s entry added successfully")
        else:
            # TODO: update existing events
            print("entry already exists")
    
    # TODO: check for divers removed from event
    
    return render(request, 'core/entries.html', {'event': event})