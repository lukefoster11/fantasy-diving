import requests
from bs4 import BeautifulSoup

class Event:
    def __init__(self, title, entriesPath, date):
        self.title = title
        self.entriesPath = entriesPath
        self.date = date

class Meet:
    def __init__(self, title, path, date, hasResults):
        self.title = title
        self.path = path
        self.date = date
        self.hasResults = hasResults
    
    def getEvents(self):
        URL = "https://secure.meetcontrol.com/divemeets/system/" + self.path
        page = requests.get(URL)
        soup = BeautifulSoup(page.content, "html.parser")

        # narrow to important content
        content = soup.find(id="dm_content")
        table = content.find("table").find("table")
        trs = table.find_all("tr")

        # cut all `Divers Entered` content
        for idx, tr in enumerate(trs):
            if tr.text == "Divers Entered:":
                trs = trs[:idx]
                break
        
        # loop through events, saving event info to `events`
        events = []
        for tr in trs:
            # check if line is new date and save info
            if tr.text.find(", 202") != -1:
                date = tr.text.strip()
            # check if new line is event with entries and save info
            if tr.text.find("Entries") != -1:
                entriesPath = tr.find_all("a")[-1]['href']
                title = tr.text
                title = title[:title.find("Rule")].strip()
                events.append(Event(title, entriesPath, date))

        return events


def main():
    URL = "https://secure.meetcontrol.com/divemeets/system/index.php"
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, "html.parser")

    # narrow to important content
    content = soup.find(id="dm_content")

    # find info about current and upcoming meets
    divs = content.find_all("div")
    meets = divs[2]
    trs = meets.find_all("tr", {"bgcolor":["e9e9e9", "9999ff"]})

    # loop through meets, saving meet info to `meets`
    meets = []
    for tr in trs:
        links = tr.find_all("a")
        if links[-1].text == "Results":
            hasResults = True
            title = links[-2]
        else:
            hasResults = False
            title = links[-1]
        date = tr.find("td", align="right")

        meets.append(Meet(title.text, title['href'], date.text, hasResults))

    for meet in meets[:5]:
        print(meet.title)
        print(meet.date)
        print("-------------------")
        for event in meet.getEvents():
            print(event.title)
            print(event.entriesPath)
            print(event.date, end="\n\n")
        print("\n")


if __name__ == "__main__":
    main()