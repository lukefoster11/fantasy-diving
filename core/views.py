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
                endDate = meet.endDate).save()
            print(f"{meet.title} added successfully")
        except IntegrityError:
            # Update existing meets
            print(f"{meet.title} already exists, updating...")
            dbmeet = Meet.objects.get(meetid=meet.id)
            dbmeet.title = meet.title
            dbmeet.startDate = meet.startDate
            dbmeet.endDate = meet.endDate
            dbmeet.save()
    
    # TODO: Remove cancelled meets

    current_meets = Meet.objects.filter(startDate__lte=date.today()).filter(endDate__gte=date.today()).order_by('startDate', 'title')
    upcoming_meets = Meet.objects.filter(startDate__gt=date.today()).order_by('startDate', 'title')
    context = {'current_meets': current_meets, 'upcoming_meets': upcoming_meets}
    return render(request, 'core/overview.html', context)

def events(request, meet_id):
    # Get meet info from db
    meet = get_object_or_404(Meet, pk=meet_id)
    dsmeet = divescrape.Meet(meet.meetid, meet.title, meet.startDate, meet.endDate)
    dsevents = dsmeet.getEvents()

    # Generate events for meet, and add/update them to db
    for event in dsevents:
        # Fetch event from database
        exists = Event.objects.filter(meet=meet).filter(title=event.title)
        if exists:
            # Update existing events
            print(f"{exists[0].title} already exists, updating")
            exists[0].date = event.date
            exists[0].entriesPath = event.entriesPath
            exists[0].save()
        else:
            Event(meet = meet, title = event.title, date = event.date, entriesPath = event.entriesPath).save()
            print(f"{event.title} added successfully")

    # TODO: check for events removed from meet      

    return render(request, 'core/events.html', {'meet': meet})

def entries(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    meet = event.meet
    dsmeet = divescrape.Meet(meet.meetid, meet.title, meet.startDate, meet.endDate)
    dsevent = divescrape.Event(event.title, event.entriesPath, event.date, dsmeet)

    update_results = False
    
    if not event.hasResults:
        dsentries = dsevent.getEntries()
        update_results = dsevent.hasResults
        event.save()

        # TODO: look for unofficial results (if meet has started, stop allowing fantasy entries)
        if not update_results:

            for entry in dsentries:
                exists = Entry.objects.filter(event=event).filter(diver=entry.diver)
                if not exists:
                    # create entry in database
                    dbentry = Entry(event = event, diver = entry.diver)
                    dbentry.save()

                    # assign dive relationship
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
    
        else:
            results = dsevent.getResults()
            for entry in results:
                exists = Entry.objects.filter(event=event).filter(diver=entry.diver)
                if not exists:
                    # create entry in database
                    dbentry = Entry(event=event, diver=entry.diver)
                    dbentry.save()
                
                else:
                    # TODO: update existing entries
                    print("entry already exists")

                dbentry = Entry.objects.filter(event=event).get(diver=entry.diver)
                dbdives = DiveInstance.objects.filter(entry=dbentry)
                for dive in entry.dives:
                    dbdive = Dive.objects.filter(number=dive.number).get(height=dive.height)
                    exists = DiveInstance.objects.filter(entry=dbentry).filter(dive=dbdive)
                    if exists:
                        exists[0].score = dive.score
                        exists[0].save()
                    else:
                        DiveInstance(entry=dbentry, dive=dbdive, score=dive.score).save()

                if dbentry.totalScore == 0:
                    for dive in entry.dives:
                        dbentry.totalScore += dive.score
                dbentry.save()
                
                # Delete any extra DiveInstances if a dive was maybe changed
                for dbdive in dbdives:
                    match = False
                    for dive in entry.dives:
                        if dbdive.dive.number == dive.number and dbdive.dive.height == dive.height:
                            match = True
                    if not match:
                        dbdive.delete()
            
            fantasyEntries = FantasyEntry.objects.filter(event=event)
            for fantasyEntry in fantasyEntries:
                if fantasyEntry.totalScore == 0:
                    for dive in fantasyEntry.dives.all():
                        fantasyEntry.totalScore += dive.score
                fantasyEntry.save()
            
            event.hasResults = True
            event.save()
        
    return render(request, 'core/results.html', {'event': event})


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