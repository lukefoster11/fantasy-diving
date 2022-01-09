import requests
from bs4 import BeautifulSoup

class Event:
    def __init__(self, title, path, date, hasResults):
        self.title = title
        self.path = path
        self.date = date
        self.hasResults = hasResults
    
    def getInfo(self):
        URL = "https://secure.meetcontrol.com/divemeets/system/" + self.path
        page = requests.get(URL)
        soup = BeautifulSoup(page.content, "html.parser")

        #narrow to important content
        content = soup.find(id="dm_content")
        table = content.find("table").find("table")

        return table


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

    # loop through events, saving event info to `events`
    events = []
    for tr in trs:
        links = tr.find_all("a")
        if links[-1].text == "Results":
            hasResults = True
            title = links[-2]
        else:
            hasResults = False
            title = links[-1]
        date = tr.find("td", align="right")

        events.append(Event(title.text, title['href'], date.text, hasResults))

    print(events[0].getInfo())


if __name__ == "__main__":
    main()