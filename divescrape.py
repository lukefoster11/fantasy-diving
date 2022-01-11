import requests
from bs4 import BeautifulSoup

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
        self.entries = None

    def updateEntries(self):
        entries = []

        if self.entriesPath:
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
                dList = []
                for j in range(nDives):
                    dList.append(rows[startIdxs[i]+1:endIdxs[i]][j].find_all("td")[1].text.strip())
                dives.append(dList)

            for i in range(len(divers)):
                entries.append(Entry(divers[i], dives[i], self))

        self.entries = entries
        return

class Meet:
    def __init__(self, title, path, date, hasResults):
        self.title = title
        self.path = path
        self.date = date
        self.hasResults = hasResults
        self.events = None
    
    def updateEvents(self):
        URL = "https://secure.meetcontrol.com/divemeets/system/" + self.path
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
        for row in rows:
            # check if line is new date and save info
            if row.text.find(", 202") != -1:
                date = row.text.strip()
            # check if new line is event with entries and save info
            if row.text.find("Rule") != -1:
                if row.text.find("Entries") != -1:
                    entriesPath = row.find_all("a")[-1]['href']
                else:
                    entriesPath = None
                title = row.text
                title = title[:title.find("Rule")].strip()
                events.append(Event(title, entriesPath, date, self))

        self.events = events
        return


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

        meets.append(Meet(title.text, title['href'], date.text, hasResults))

    return meets

def main():
    """
    meets = getMeets()
    meet = meets[0]
    meet.updateEvents()
    for event in meet.events:
        event.updateEntries()
    print(meet.title)
    print(meet.date)
    print("-"*50)
    for event in meet.events: 
        print(event.title)
        for entry in event.entries:
            print(entry.diver)
            print(entry.dives)
        print("")
    """


if __name__ == "__main__":
    main()