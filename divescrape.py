from tkinter.ttk import Separator
import requests
import datetime
import re
import math
from bs4 import BeautifulSoup

class Dive:
    def __init__(self, number, height, description=None, dd=None, score=None):
        self.number = number
        self.height = height
        self.description = description
        self.dd = dd
        self.score = score

class Entry:
    def __init__(self, diver, dives, event):
        self.diver = diver
        self.dives = dives
        self.event = event
    
    def updateDives(self, scorePath):
        URL = "https://secure.meetcontrol.com/divemeets/system/" + scorePath
        page = requests.get(URL)
        soup = BeautifulSoup(page.content, "html.parser")

        dives = []
        content = soup.find(id="dm_content").find("table").find_all("tr", bgcolor="dddddd")
        for row in content:
            tds = row.find_all("td")
            if tds[1].find("br"):
                number = tds[1].get_text(strip=True, separator='\n').splitlines()[1]
                height = tds[2].get_text(strip=True, separator='\n').splitlines()[1][:-1]
                height = math.floor(float(height))         
            else:
                number = tds[1].text
                # TODO: perhaps need to fix later? We'll see
                height = math.floor(float(tds[2].text[:-1]))
            score = float(tds[-2].text)
            dives.append(Dive(number, height, score=score))
        
        self.dives = dives

        return

class Event:
    def __init__(self, title, entriesPath, date, meet, hasResults=False):
        self.title = title
        self.entriesPath = entriesPath
        self.date = date
        self.meet = meet
        self.hasResults = hasResults

    def getEntries(self):
        entries = []

        if self.entriesPath != "None":
            URL = "https://secure.meetcontrol.com/divemeets/system/" + self.entriesPath
            page = requests.get(URL)
            soup = BeautifulSoup(page.content, "html.parser")

            # narrow to important content
            content = soup.find(id="dm_content")
            table = content.find("table").find("table")

            # find divers
            links = table.find_all("a")
            divers = []
            for link in links:
                try:
                    if link['href'].find("profile.php") != -1:
                        name = link.text.split(",")
                        name = name[1].strip() + " " + name[0].strip()
                        divers.append(name)
                except KeyError:
                    pass
            
            # find dive lists
            dives = []
            rows = table.find_all("tr")
            startIdxs = []
            endIdxs = []
            for idx,row in enumerate(rows):
                if row.text.find("Order") != -1:
                    startIdxs.append(idx)
                elif row.text.find("DD Total:") != -1:
                    endIdxs.append(idx)
            try:
                nDives = endIdxs[0] - startIdxs[0] - 1
            except IndexError:
                self.hasResults = True
                return
            for i in range(len(divers)):
                diveList = []
                for j in range(nDives):
                    diveNumber = rows[startIdxs[i]+1:endIdxs[i]][j].find_all("td")[1].text.strip()
                    diveHeight = rows[startIdxs[i]+1:endIdxs[i]][j].find_all("td")[2].text.strip()[:-1]
                    diveList.append(Dive(diveNumber, diveHeight))
                dives.append(diveList)

            for i in range(len(divers)):
                entries.append(Entry(divers[i], dives[i], self))

        return entries

    def getResults(self):
        URL = "https://secure.meetcontrol.com/divemeets/system/meetresultsext.php?meetnum=" + str(self.meet.id)
        page = requests.get(URL)
        soup = BeautifulSoup(page.content, "html.parser")
        found = False

        results = []

        content = soup.find(id="dm_content").find("table").find_all("tr")
        for row in content:
            td = row.find("td")
            link = td.find("a")
            try:
                if link.text == self.title:
                    URL = "https://secure.meetcontrol.com/divemeets/system/" + link['href']
                    found = True
            except AttributeError:
                pass
        
        if not found:
            return

        # continue if link to event results was found
        page = requests.get(URL)
        soup = BeautifulSoup(page.content, "html.parser")
        found = False

        content = soup.find(id="dm_content").find("table").find_all("tr")
        for row in content:
            link = row.find("a")
            if link:
                if link['href'].find("profile.php") != -1:
                    name = re.sub(' +', ' ',link.text.strip())
                    scorePath = row.find_all("td")[-2].find("a")['href']
                    entry = Entry(name, [], self)
                    entry.updateDives(scorePath)
                    results.append(entry)
                           
        return results


class Meet:
    def __init__(self, id, title, startDate, endDate):
        self.id = id
        self.title = title
        self.startDate = startDate
        self.endDate = endDate
    
    def getEvents(self):
        URL = "https://secure.meetcontrol.com/divemeets/system/meetinfoext.php?meetnum=" + str(self.id)
        page = requests.get(URL)
        soup = BeautifulSoup(page.content, "html.parser")

        # narrow to important content
        content = soup.find(id="dm_content")
        table = content.find("table").find("table")
        rows = table.find_all("tr")

        # cut all `Divers Entered` content
        for idx, row in enumerate(rows):
            if row.text == "Divers Entered:":
                rows = rows[:idx]
                break
        
        # loop through events, saving event info to `events`
        events = []
        date = self.startDate
        for row in rows:
            # check if line is new date and save info
            if row.text.find(", 202") != -1:
                date = row.text.strip()
                date = date.replace(",", "").split()
                date = datetime.date(int(date[-1]), datetime.datetime.strptime(date[1], "%b").month, int(date[2]))

            # check if new line is event with entries and save info
            if row.text.find("Rule") != -1:
                if row.text.find("Entries") != -1:
                    entriesPath = row.find_all("a")[-1]['href']
                else:
                    entriesPath = "None"
                title = row.text
                title = title[:title.find("Rule")].strip()
                events.append(Event(title, entriesPath, date, self))

        return events


def getMeets():
    URL = "https://secure.meetcontrol.com/divemeets/system/index.php"
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, "html.parser")

    # narrow to important content
    content = soup.find(id="dm_content")

    # find info about current and upcoming meets
    divs = content.find_all("div")
    meets = divs[2]
    rows = meets.find_all("tr", {"bgcolor":["e9e9e9", "9999ff"]})

    # loop through meets, saving meet info to `meets`
    meets = []
    for row in rows:
        links = row.find_all("a")
        if links[-1].text == "Results":
            title = links[-2]
        else:
            title = links[-1]
        date = row.find("td", align="right")
        date = date.text
        date = date.replace(",", "").split()

        startDate = datetime.date(int(date[-1]), datetime.datetime.strptime(date[0], "%b").month, int(date[1]))
        endDate = datetime.date(int(date[-1]), datetime.datetime.strptime(date[3], "%b").month, int(date[4]))

        id = int(title['href'][-4:])

        meets.append(Meet(id, title.text, startDate, endDate))

    return meets


def getDives():
    URL = "https://secure.meetcontrol.com/divemeets/system/divelist.php"
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, "html.parser")

    # narrow contents to rows of info
    rows = soup.find("table").find_all("tr")[4:-1]

    dives = []
    for row in rows:
        tds = row.find_all("td")
        number = tds[0].text
        height = int(tds[1].text[:-1])
        description = tds[2].text
        dd = float(tds[3].text)
        dives.append(Dive(number, height, description, dd))

    return dives

def main():

    
    
    meet = getMeets()[3]
    event = meet.getEvents()[4]
    results = event.getResults()
    for result in results:
        print(result.diver)
    
    return

if __name__ == "__main__":
    main()