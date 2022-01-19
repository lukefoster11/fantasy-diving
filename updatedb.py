from turtle import update
import divescrape
from fantasydiving.wsgi import *
from core.models import Dive

def updateDives():
    dives = divescrape.getDives()
    for dive in dives:
        exists = Dive.objects.filter(number=dive.number).filter(height=dive.height)
        if not exists:
            Dive(number=dive.number, height=dive.height, description=dive.description, dd=dive.dd).save()
            print(f"{dive.number}, {dive.height}M added successfully")
        else:
            # TODO: update existing events
            print("dive already in database")

def main():
    #updateDives()
    return

if __name__ == "__main__":
    main()