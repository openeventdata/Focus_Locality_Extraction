import codecs
import re, time
import urllib
from xml.etree import ElementTree
import wikipedia
from wikipedia.exceptions import PageError, DisambiguationError
from geopy.distance import great_circle
from nltk import word_tokenize

accepted = ["adm1st", "adm2nd", "adm3rd", "city", "country", "isle"]
names = {}
for line in open("allCountries.txt"):
    line = re.split(r'\t+', line)
    if line[6] in ["A", "P"]:  # Administrative Areas and Populated Places only
        if line[2] in names:
            have = False
            for item in names[line[2]]:  # Check for duplicates and a minimum of 1000km distance apart
                if great_circle((item[0], item[1]), (float(line[4]), float(line[5]))).kilometers < 1000:
                    have = True
            if not have:
                names[line[2]].append((float(line[4]), float(line[5])))
        else:
            names[line[2]] = [(float(line[4]), float(line[5]))]


f = codecs.open("./w.xml", "w", "utf-8")
f.write("<?xml version=\"1.0\" encoding=\"utf-8\"?>\n")
f.write("<!-- WikToR = Wikipedia Toponym Retrieval -->\n")
f.write("<wikiPages>\n")
pageCount = 1
resume = False
for location in {('Edinburgh', 'haha'): 1}:
    if pageCount > 5000:
        break
    if not resume:
        if location[0] == "Songshan":
            resume = True
            pageCount = 4704
            continue
        else:
            continue
    query = {'format': 'xml', 'title': location[0], 'maxRows': 100, 'username': "YOUR USERNAME", 'style': 'full', 'feature': "city"}
    response = urllib.urlopen("http://api.geonames.org/wikipediaSearch?" + urllib.urlencode(query))
    time.sleep(0.5)  # This should keep Geonames Free happy, maximum of 2000 requests per hour, so pause here briefly
    for entry in ElementTree.fromstring(response.read()):
        url = entry.find("./wikipediaUrl").text
        title = entry.find("./title").text
        lat = entry.find("./lat").text
        lon = entry.find("./lng").text
        feature = entry.find("./feature").text
        code = entry.find("./countryCode").text
        if not (title == location[0] or re.compile(location[0] + ",.*").match(title)):
            continue  # Accept whole names like "Oxford" or "Oxford, SOME COUNTRY" with a comma Wiki disambiguation
        if feature not in accepted:
            continue
        try:
            page = wikipedia.page(urllib.unquote(title))
        except PageError:
            continue
        except DisambiguationError:
            continue
        sections = re.split("\n?=+.*=+\n?", page.content)
        pCount = 0
        pText = ""
        finished = False
        for section in sections:
            if finished:
                break  # Reached 200 or more word tokens, thank you! Adjust if you need more!
            if location[0] not in section or section.strip().startswith("^"):
                continue  # Don't accept sections that don't contain the location name
            for paragraph in section.split("\n"):
                if len(paragraph.strip()) == 0:
                    continue
                tokens = word_tokenize(paragraph)
                pCount += len(tokens)
                pText += paragraph.strip() + " "
                if pCount > 200:
                    pText = pText.strip()
                    f.write("<page number=\"" + str(pageCount) + "\">\n")
                    f.write("<pageTitle>" + title + "</pageTitle>\n")
                    f.write("<toponymName>" + location[0] + "</toponymName>\n")
                    f.write("<text><![CDATA[" + pText + "]]>\n</text>\n")
                    indices = list(re.finditer(r"\b" + location[0] + r"\b", pText))
                    f.write("  <toponymIndices count=\"" + str(len(indices)) + "\">\n")
                    for index in indices:
                        f.write("    <toponym>\n")
                        f.write("      <start>" + str(index.start()) + "</start>\n")
                        f.write("      <end>" + str(index.end()) + "</end>\n")
                        f.write("    </toponym>\n")
                    f.write("  </toponymIndices>\n")
                    f.write("<url>" + url + "</url>\n")
                    f.write("<lat>" + str(lat) + "</lat>\n")
                    f.write("<lon>" + str(lon) + "</lon>\n")
                    f.write("<feature>" + str(feature) + "</feature>\n")
                    f.write("<country>" + str(code) + "</country>\n")
                    f.write("</page>\n")
                    print title, "-- page:", pageCount  # Progress "bar" This is not a fast process :-) 4+ hours?
                    pageCount += 1
                    finished = True
                    break
f.write("</wikiPages>")

#-------------------------HOW TO VERIFY CORRECTNESS OF YOUR WIKI CORPUS FILE-------------------------------------------

#For missing country codes, you may use the Geonames API to fill in any blanks automatically:
#http://api.geonames.org/countryCode?lat=LATITUDE&LONGITUDE=10.2&username=YOUR_USERNAME

tree = ElementTree.parse("./wiktor.xml")  # An error here means the XML file is likely malformed
count = 0
for node in tree.getroot():
    count += 1
    title = node.find("./pageTitle").text
    if len(title) == 0:
        raise RuntimeError("No page title for " + title)  # Missing page title
    targetName = node.find("toponymName").text
    if int(node.attrib['number']) != count:
        raise RuntimeError("Page numbering is wrong for number " + str(count))  # Catch a counting error
    if len(targetName) == 0:
        raise RuntimeError("Toponym name is missing for " + title)  # Empty name!!!
    if targetName not in title:
        raise RuntimeError("Mismatch target name is " + targetName + " title is " + title)  # Out of sync titles
    text = node.find("./text").text
    if len(word_tokenize(text)) < 200:
        raise RuntimeError("Only " + str(len(word_tokenize(text))) + " word tokens for " + title)  # Not enough context
    lat = float(node.find("./lat").text)
    lon = float(node.find("./lon").text)
    if 180.0 < lon < -180.0:
        raise RuntimeError("Invalid longitude value for " + title)  # Error in longitude
    if 90.0 < lat < -90.0:
        raise RuntimeError("Invalid latitude value for " + title)  # Error in latitude
    if "count" not in node.find("./toponymIndices").attrib:
        raise RuntimeError("No toponym count value for " + title)  # No count attribute
    for t in node.findall("./toponymIndices/toponym"):
        start = int(t.find("./start").text)
        end = int(t.find("./end").text)
        if text[start:end] != targetName:
            raise RuntimeError("The index is incorrect for " + title)  # Catch an index error
        if start > 0:
            if re.match("\w", text[start - 1]) is not None:
                raise RuntimeError("The boundary was violated for word " + title)  # Another index error type
        if end < len(text):
            if re.match("\w", text[end]) is not None:
                raise RuntimeError("The boundary was violated for word " + title)  # Another index error type
    url = node.find("./url").text
    if len(url) == 0:
        raise RuntimeError("URL missing for " + title)  # No url!!
    feature = node.find("./feature").text
    if feature not in accepted:
        raise RuntimeError("Invalid feature value for " + title)  # Error in feature code
    cCode = node.find("./country").text
    if len(cCode) != 2:
        raise RuntimeError("Check country code value for " + title)  # Error in country code
if count != 5000:
    raise RuntimeError("There aren't 5000 pages in this file!")  # Catch a count error

print "Finished error checking, if you didn't see any error messages, the file is OK."
