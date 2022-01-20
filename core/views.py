from django.shortcuts import get_object_or_404, render, get_list_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.db.utils import IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from datetime import date
from .models import FantasyEntry, Meet, Event, Entry, Dive, DiveInstance
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

    current_meets = Meet.objects.filter(startDate__lte=date.today()).filter(endDate__gte=date.today()).order_by('startDate')
    upcoming_meets = Meet.objects.filter(startDate__gt=date.today()).order_by('startDate')
    context = {'current_meets': current_meets, 'upcoming_meets': upcoming_meets}
    return render(request, 'core/overview.html', context)

def events(request, meet_id):
    # Get meet info from db
    meet = get_object_or_404(Meet, pk=meet_id)
    dsmeet = divescrape.Meet(meet.meetid, meet.title, meet.startDate, meet.endDate, meet.hasResults)
    dsevents = dsmeet.getEvents()

    # Generate events for meet, and add/update them to db
    for event in dsevents:
        try:
            # fetch event from database
            Event.objects.filter(meet=meet).get(title=event.title)
            # TODO: update existing events
            print("event already exists")
        except ObjectDoesNotExist:
            Event(meet = meet, title = event.title, date = event.date, entriesPath = event.entriesPath).save()
            print(f"{event.title} added successfully")

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
            # create entry in database
            dbentry = Entry(event = event, diver = entry.diver)
            dbentry.save()

            # assign dive many-to-many relationship
            for dive in entry.dives:
                if dive.height == '7.5':
                    dive.height = '7'
                dbdive = Dive.objects.filter(number=dive.number).get(height=dive.height)
                DiveInstance(entry=dbentry, dive=dbdive).save()

            print(f"{entry.diver}'s entry added successfully")
        else:
            # TODO: update existing entries
            print("entry already exists")
    
    # TODO: check for divers removed from event
    
    return render(request, 'core/entries.html', {'event': event})

def createEntry(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    selected_dives = request.POST.getlist('diveInstance')
    # TODO: check if user already has FantasyEntry
    # TODO: check if choices align with competition rules (6 dives, etc.)
    fantasyEntry = FantasyEntry(event=event)
    fantasyEntry.save()
    for dive in selected_dives:
        diveInstance = DiveInstance.objects.get(pk=dive)
        fantasyEntry.dives.add(diveInstance)

    # TODO: HttpResponseRedirect?
    return redirect('core:overview')