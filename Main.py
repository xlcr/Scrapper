#!/usr/bin/env python3

from Scrapper import Scrapper
import os

#move to Scrapper? maybe
def serveSoup(soups, filename):

    print "Writing to " + filename
    filepath = "Documents\\" + filename
    if os.path.exists(filepath):
        os.remove(filepath)

    with open(filepath, 'a') as f:
        f.write("<html>")
        for tag in soups:
            if tag.name not in ["strong", "b", "em", "span", "a", "i"]:
                f.write(str(tag))
        f.write("</html>")

#The starting page, url removed
pageURL = ""
nextChapterText = "Next Chapter"
previousChapterText = "Previous Chapter"
filename = "Ward.rtf"
numberOfChapters = 3 

# Settings for verifying if webnovels are OK
hasProperFormat = True
checkSerializable = False
chapterEdgePattern = nextChapterText

scrapper = Scrapper()
paragraphs = []

# Verify if Serializable first 

if checkSerializable:
    if not scrapper.verifyChapterLinks(pageURL, nextChapterText):
        print "This may not be serializable."
        exit()

while True:

    soup = scrapper.cookSoupFromURL(pageURL)
    print("Processing: " + soup.title.text)
    firstPara, lastPara = scrapper.getParagraphLocations(soup)

    selectedSoups = soup.find_all()[firstPara:lastPara]
    paragraphs.append(scrapper.generateTag("h2", str(soup.title.text)))

    if hasProperFormat:
        verification = scrapper.verifyParagraph(selectedSoups, chapterEdgePattern)
        if not verification:
            paragraphs.append(scrapper.generateTag("i", "This chapter may not be accurate."))
            print("Paragraph Warning.")
        else:
            print("Format is OK.")

    
    paragraphs.extend(selectedSoups)
    pageURL = scrapper.getNextChapterLink(soup, nextChapterText)

    if pageURL is None:
        print("Doesn't seem like there's anything more now. Bye!")
        break  

serveSoup(paragraphs, filename)





