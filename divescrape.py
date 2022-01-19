import requests
import datetime
from bs4 import BeautifulSoup

class Dive:
    def __init__(self, number, height, description=None, dd=None):
        self.number = number
        self.height = height
        self.description = description
        self.dd = dd

class Entry:
    def __init__(self, diver, dives, event):
        self.diver = diver
        self.dives = dives
        self.event = event

class Event:
    def __init__(self, title, entriesPath, date, meet):
        self.title = title
        self.entriesPath = entriesPath
        self.date = date
        self.meet = meet

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
                        divers.append(link.text)
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
            nDives = endIdxs[0] - startIdxs[0] - 1
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

class Meet:
    def __init__(self, id, title, startDate, endDate, hasResults):
        self.id = id
        self.title = title
        self.startDate = startDate
        self.endDate = endDate
        self.hasResults = hasResults
    
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
            hasResults = True
            title = links[-2]
        else:
            hasResults = False
            title = links[-1]
        date = row.find("td", align="right")
        date = date.text
        date = date.replace(",", "").split()

        startDate = datetime.date(int(date[-1]), datetime.datetime.strptime(date[0], "%b").month, int(date[1]))
        endDate = datetime.date(int(date[-1]), datetime.datetime.strptime(date[3], "%b").month, int(date[4]))

        id = int(title['href'][-4:])

        meets.append(Meet(id, title.text, startDate, endDate, hasResults))

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
    """
    meet = getMeets()[2]
    event = meet.getEvents()[0]
    entries = event.getEntries()
    for entry in entries:
        print(entry.diver, end=": ")
        for dive in entry.dives:
            print(dive.number, end=" - ")
            print(dive.height, end=", ")
        print("")
    """
    return

if __name__ == "__main__":
    main()