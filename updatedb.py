from fantasydiving.wsgi import *
import divescrape
from core.models import Meet, Event, Entry
from django.db.utils import IntegrityError

def addMeet(meet):
    Meet(meetid = meet.id, title = meet.title, startDate = meet.startDate, 
        endDate = meet.endDate, hasResults = meet.hasResults).save()
    return

def addEvent(event):
    meet = Meet.objects.filter(meetid=event.meet.id)[0]
    Event(meet = meet, title = event.title, date = event.date).save()
    return

def main():
    meets = divescrape.getMeets()
    for meet in meets:
        try:
            addMeet(meet)
        except IntegrityError:
            # TODO: update existing meets
            print("meet already exists")
        
        for event in meet.getEvents():    
            exists = Event.objects.filter(meet = Meet.objects.filter(meetid=event.meet.id)[0]).filter(title=event.title)
            if not exists:
                addEvent(event)
            else:
                # TODO: update existing events
                print("event already exists")
            
    
    return


if __name__ == '__main__':
    main()