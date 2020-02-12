# -*- coding: UTF-8 -*-
#!/usr/bin/env python3

from bs4 import BeautifulSoup
import os, requests, time

class Scrapper(object):

    def __init__(self):

        # Scrapper Settings 
        self.nextChapterText = None
        self.acceptableTags = ["p", "strong", "br", "b", "em", "span", "a", "i"]
        self.mode = "Auto"
        self.soup = None

    def cookSoupFromURL(self, URL): #Soup or None
        try:
            while True:
                request = requests.get(URL)
                if request.status_code != 200:
                    request = requests.get(URL, headers={'User-Agent': 'Mozilla/5.0', 'Retry-After': '20'})

                if request.status_code == 200:
                    soup = BeautifulSoup(request.content, 'html.parser')
                    return soup
                else:
                    return None
        except Exception as e:
            print("Error in {0}: {1}".format("cookSoupFromURL", str(e)))
            return None

    def verifyChapterLinks(self, URL, nextChapterText): #Bool

        sameLinkCheck = []

        for x in range(3):
            try:
                soup = self.cookSoupFromURL(URL)
                if soup is not None:
                    nextChapterLink = self.getNextChapterLink(soup, nextChapterText)
                    if nextChapterLink is not None:
                        sameLinkCheck.append(nextChapterLink)
                        URL = nextChapterLink
                    else:
                        print("ERROR: verifyChapterLinks: Unable to retrieve next link in turn: " + soup.title)
                        return False
            except Exception as e:
                print("ERROR: verifyChapterLinks: " + str(e))
                return False

        sameLinks = all(link == sameLinkCheck[0] for link in sameLinkCheck)

        if not sameLinks:
            return True
        else:
            print("Current New Chapter Text redirects the program to the next page is also the same link in the next page.")
            print("This will cause a loop. Current New Chapter Text: {0}".format(nextChapterText))
            newNextChapterText = input("New Next Chapter Text (q=quit): ")

            if newNextChapterText.lower() == "q":
                return False
            else:
                print("Retrying... ")
                self.verifyChapterLinks(URL, newNextChapterText)

    def getNextChapterLink(self, soup, nextChapterText): #URL or None

        possibleChapters = []
        possibleRedirections = soup.find_all(lambda tag:tag.name=="a" and nextChapterText in tag.text)

        for tag in possibleRedirections:
            if tag.text.strip() == nextChapterText:
                possibleChapters.append(tag.get("href"))

        if len(possibleChapters) == 1:
            
            return possibleChapters[0]
        
        elif len(possibleChapters) > 1:

            if all(elem == possibleChapters[0] for elem in possibleChapters):
                return possibleChapters[0]
            else:
                if self.mode == "SemiAuto":
                    return self.selectLink(possibleChapters, soup.title)
                print("Different links fetched and current mode is not Semi Auto.")
                return None

        else:
            print("Unable to retrieve link from the Next Chapter Text given.")
            return None

    def selectLink(self, possibleChapters, soupTitle): #URL or None
        #Returns a manually selected link

        print("Different links fetched -- Please select or provide the next chapter link:")
        print("Current chapter title: " + soupTitle)

        for index, link in enumerate(possibleChapters):
            print(str(index+1) + ": " + str(link))

        while True:

            selection = input("Select link (q=quit): ")
            if isinstance(selection, int):
                if selection >= 0 and selection < len(possibleChapters):
                    return possibleChapters[selection - 1]
                else:
                    print("Invalid Selection. Please select number 0 - {0}.".format(str(len(possibleChapters))))
            elif isinstance(selection, str):
                    if selection.casefold() == "q":
                        return None
            else:
                return None

    def findStartOfParagraph(self, soup): #Index or None
        #tries to find the first paragraph by finding a series of continuations 

        firstParaIndex = None
        tagCount = 0
        tags = soup.find_all()

        for index, tag in enumerate(tags):
            if tagCount > 5:
                return firstParaIndex
            elif tag.name in self.acceptableTags:
                if firstParaIndex is None:
                    firstParaIndex = index
                tagCount += 1
            elif tag.name not in self.acceptableTags:
                firstParaIndex = None
                tagCount = 0
            else:
                print("There's {0} tags. Tried to find a p tag but retrieved nothing.".format(str(len(tags))))
                return None

    def findEndOfParagraph(self, soup, firstIndex): #Index or None

        tags = soup.find_all()
        for index, tag in enumerate(tags[firstIndex:]):
            if tag.name not in self.acceptableTags:
                return index + firstIndex

        if len(tags) is not 0:
            return soup.find_all()
        else:
            return None

    def getParagraphLocations(self, soup):
        firstIndex = self.findStartOfParagraph(soup)
        lastIndex = self.findEndOfParagraph(soup, firstIndex)
        return (firstIndex, lastIndex)

    def verifyParagraph(self, tags, checkText):

        start = False
        end = False

        for tag in tags[:10]:
            if checkText in tag.text:
                start = True
                break

        for tag in tags[len(tags)-10:]:
            if checkText in tag.text:
                end = True
                break
        
        if start == True and start is end:
            return True
        else:
            return False

    def generateTag(self, tag, text):
        newTag = BeautifulSoup("<dummy></dummy>", "html.parser").new_tag(tag)
        newTag.string = text
        if tag == "h2":
            newTag['style'] = "page-break-before: always;"
        return newTag

if __name__ == "__main__":
    print "hiya"