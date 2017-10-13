import codecs
import json
import os
import urllib
import xml.etree.ElementTree as et
import subprocess
import time
from geopy.distance import great_circle
import numpy
import matplotlib.pyplot as plt
# from yahoo import yahoo_resolve


def calculate_area(info):
    """
    Calculate the area of a simple rectangle (bounding box)
    :param info - the XML string containing data
    :return: area of box
    """
    bbox = info.find("./bbox")
    if bbox is not None:
        n = bbox.find("./north").text
        s = bbox.find("./south").text
        e = bbox.find("./east").text
        w = bbox.find("./west").text
        ns = great_circle((float(n), 0.0), (float(s), 0.0)).kilometers
        ew = great_circle((0.0, float(w)), (0.0, float(e))).kilometers
        return ns * ew
    else:
        return 1


def prepare_lgl(path_to_xml, path_to_output, directory):
    """
    Save the contents of the LGL corpus to file to create a gold corpus.
    :param directory: where to save the text files for each document in corpus
    :param path_to_xml: file containing the Local Global Lexicon annotation
    :param path_to_output: where to save the output
    :return: N/A
    """
    tree = et.parse(path_to_xml)
    root = tree.getroot()
    f = codecs.open(path_to_output, "w", "utf-8")
    c = 0
    for child in root:
        text = child.find('text').text
        gold_tops = []
        toponyms = child.findall('./toponyms/toponym')
        for top in toponyms:
            tag = top.find("gaztag")
            phrase = top.find("phrase")
            if tag is None:
                continue   # Do not include toponyms with NO coordinates, we filter these out (~17% of the dataset)
            start = top.find("start")
            end = top.find("end")
            query = {'geonameId': tag.attrib['geonameid'], 'username': "milangritta"}
            response = urllib.urlopen("http://api.geonames.org/get?" + urllib.urlencode(query))
            time.sleep(1)
            info = et.fromstring(response.read())
            area = calculate_area(info)
            print c
            name = tag.find("name")
            lat = tag.find("lat")
            lon = tag.find("lon")
            gold_tops.append(name.text + ",," + phrase.text + ",," + lat.text + ",," +
                             lon.text + ",," + start.text + ",," + end.text + ",," + str(area))
        for t in gold_tops:
            f.write(t + "||")
        f.write("\n")
        f = codecs.open("./" + directory + "/" + str(c), 'w', "utf-8")  # Files saved by numbers
        f.write(text)
        f.close()
        c += 1
    f.close()


def prepare_wiki(path_to_xml, path_to_output, directory):
    """
    Save the contents of the Wiki corpus to file to create a gold corpus.
    :param directory: where to save the text files for each document in corpus
    :param path_to_xml: file containing the Wikipedia Corpus annotation
    :param path_to_output: where to save the output
    :return: N/A
    """
    tree = et.parse(path_to_xml)
    root = tree.getroot()
    f = codecs.open(path_to_output, "w", "utf-8")
    c = 0
    for child in root:
        text = child.find('text').text
        gold_tops = []
        toponyms = child.findall('./toponymIndices/toponym')
        phrase = child.find("./toponymName")
        name = child.find("./pageTitle")
        lat = child.find("./lat")
        lon = child.find("./lon")
        for top in toponyms:
            start = top.find("./start")
            end = top.find("./end")
            gold_tops.append(name.text + ",," + phrase.text + ",," + lat.text + ",," +
                             lon.text + ",," + start.text + ",," + end.text)
        for t in gold_tops:
            f.write(t + "||")
        f.write("\n")
        f = codecs.open("./" + directory + "/" + str(c), 'w', "utf-8")  # Files saved by numbers
        f.write(text)
        f.close()
        c += 1
    f.close()


def run_clavin(path):
    """
    Opens a process and runs CLAVIN on the file specified by PATH. Java is run (CLAVIN) and the output is returned.
    THIS IS A VERY SLOW PROCESS, COMMAND LINE RUN MUCH FASTER!!!
    :param path: to the text file to be processed
    :return: A list of toponyms - format: [geoname,,matched name,,lat,,long,,start index,,end index]
    """
    out = []
    sp = subprocess.Popen("MAVEN_OPTS=\"-Xmx4g\" mvn exec:java -Dexec.mainClass=\"com.bericotech.clavin.WorkflowDemo\" "
                          " -Dexec.args=\"" + path + "\" -f /Users/milangritta/Downloads/DATA/parsers/CLAVIN/pom.xml",
                          shell=True, stdout=subprocess.PIPE)
    for line in iter(sp.stdout.readline, ''):
        if not line.startswith("[INFO]"):
            out.append(line.strip("\n").decode('utf-8'))
    return out


def evaluate_parser(directory, function, out_file):
    """
    This method runs a parser and saves the output to a file for later analysis.
    :param out_file: where to save the output
    :param function: the parser function to be applied to each text file in the directory
    :param directory: where the input text files are located (one article/document per file).
    :return: N/A
    """
    save = codecs.open(out_file, "w", "utf-8")
    for f in range(0, 5000):
        out = function(os.getcwd() + directory + str(f))
        # time.sleep(0.5)
        print f
        for line in out:
            save.write(line + "||")
        save.write("\n")
    save.close()


def calculate_scores(predicted, gold, inspect=False, topocluster=False, approach=''):
    """
    Given the predictions and the gold annotations, calculate precision, recall, F Score and accuracy.
    :param topocluster: Topocluster geoparser produces NON-STANDARD output so has to be treated differently
    :param inspect: If True, the differences between gold and predicted files will be printed
    :param predicted: path to the file with parser predictions
    :param gold: path to the file with gold annotations
    :return: a list of errors per toponym i.e how far away is each correctly identified toponym from
    the gold location. This is used to measure the accuracy of the geocoding part
    """
    
    f = open('lgl_'+approach+'.txt' ,'w')
    
    tp, fp, fn = 0.0, 0.0, 0.0
    accuracy = {}
    wiki = True if "wiki" in predicted else False
    predictions_file = codecs.open(predicted)
    gold = codecs.open(gold)
    toponym_index = -1
    num = 0
    for predicted, gold in zip(predictions_file, gold):
        num +=1
        predicted_tops = predicted.split("||")[:-1]
        gold_tops = gold.split("||")[:-1]
        for gold_top in gold_tops[:]:
            toponym_index += 1
            gold_top_items = gold_top.split(",,")
            for predicted_top in predicted_tops[:]:
                predicted_top_items = predicted_top.split(",,")
                mean_g = (int(gold_top_items[4]) + int(gold_top_items[5])) / 2.0
                mean_p = (int(predicted_top_items[4]) + int(predicted_top_items[5])) / 2.0
                #  If the toponym position (its mean) is no more than 9 characters from gold AND the two
                #  strings are equal then it's a match. For reasons to do with UTF-8 encoding and decoding,
                #  the toponym indices may, in a few instances, be off by a few positions when using Web APIs.
                match = False  # A flag to establish whether this is a matching prediction
                if topocluster:  # Only match for the toponym name in this instance
                    if predicted_top_items[1].lower() == gold_top_items[1].lower():
                        match = True
                elif abs(mean_g - mean_p) < 10 and predicted_top_items[1].lower() == gold_top_items[1].lower():
                    match = True   # Change the number above to 0 for EXACT matches, 10 for INEXACT matches
                if match:
                    tp += 1
                    predicted_tops.remove(predicted_top)
                    gold_tops.remove(gold_top)
                    predicted_coord = (float(predicted_top_items[2]), float(predicted_top_items[3]))
                    gold_coord = (float(gold_top_items[2]), float(gold_top_items[3]))
                    accuracy[toponym_index] = numpy.log(1 + great_circle(predicted_coord, gold_coord).kilometers)
                    #print  gold_top
                    f.write(str(num) + ': ' + str(accuracy[toponym_index]) + ', ' + predicted_top + ', '+ gold_top + '\n')
                    f.flush()
                    
                    break
        if not wiki:
            fp += len(predicted_tops)
        fn += len(gold_tops)
        if inspect:
            if len(predicted_tops) > 0 or 0 < len(gold_tops):
                print "Predicted:", " - ".join(predicted_tops)
                print "Gold Tops:", " - ".join(gold_tops)
    f_score = (tp, fp, fn)
    output = {"f_score": f_score, "accuracy": accuracy}
    
    f.close()
    return output


def merge_files(directory, max_index, prefix, output_file):
    """
    Read the whole directory file by file and concatenate the text into a new file.
    :param output_file: Where to save the output
    :param directory: where to find the files i.e. which directory to merge
    :param max_index: how many files in the directory
    :param prefix: what is the prefix of the file for example "file" followed by an index
    :return: N/A
    """
    out = codecs.open(output_file, 'w', "utf-8")
    for index in range(0, max_index):
        out.write(codecs.open(directory + "/" + prefix + str(index), encoding="utf-8").read() + "\n")
    out.close()


# noinspection PyPep8Naming
def print_stats(accuracy, scores=None, plot=False):
    """
    Take the list of errors and calculate the accuracy of the geocoding step, optionally plot as well.
    :param scores: A tuple (true_positive, false_positive, false_negative) to calculate the F Score
    :param accuracy: A list of geocoding errors per toponym i.e. how far off in km from true coordinates
    :param plot: whether to plot the accuracy line by toponym
    :return: N/A
    """
    MAX_ERROR = 20039  # Furthest distance between two points on Earth, i.e the circumference / 2
    if scores is not None:
        precision = scores[0] / (scores[0] + scores[1])
        print "Precision: ", precision
        recall = scores[0] / (scores[0] + scores[2])
        print "Recall:    ", recall
        f_score = 2 * precision * recall / (precision + recall)
        print "F-Score:   ", f_score
        
        accGeotag = scores[0] / (scores[0]+ scores[1]+scores[2])
        print "accGeotag:     :", accGeotag
        
    print "Median: ", numpy.median(sorted(accuracy))
    print "Mean: ", numpy.mean(accuracy)
    print "Size: ", len(accuracy)
    k = numpy.log(161)  # This is the k in accuracy@k metric (see my Survey Paper for details)
    print "Accuracy to 161 km: ", sum([1.0 for dist in accuracy if dist < k]) / len(accuracy)
    print "AUC = ", numpy.trapz(accuracy) / (numpy.log(MAX_ERROR) * (len(accuracy) - 1))  # Using trapezoidal rule.
    # The above computes the actual errors committed divided by the worst case scenario, i.e every error = MAX_ERROR
    if plot:
        # fig, ax1 = plt.subplots()
        # ax1.plot(accuracy, 'r+')
        # ax2 = ax1.twinx()
        # ax2.plot(accuracy1, 'b^')
        plt.plot(accuracy)
        plt.title('Distribution of Geocoding Errors. Number of toponyms: ' + str(len(accuracy)))
        plt.ylabel('Error Distance in ln(KM)')
        plt.xlabel('Geocoding Error Per Toponym')
        x1,x2,y1,y2 = plt.axis()
        plt.axis((x1, len(accuracy), y1, 10))
        plt.show()


def format_edinburgh(xml):
    """
    Take the raw output of the Edinburgh parser and extract the properly formatted toponyms for later analysis.
    :param xml: the xml as a STRING to be parsed
    :return: a list of toponyms in format: [PLACEHOLDER STRING,,matched name,,lat,,long,,start index,,end index]
    """
    if len(xml) == 0:  # sometimes no xml string is returned due to no entities found in parsing the output
        return []
    root = et.fromstring(xml)
    toponyms, targets = [], []
    for ent in root.findall("./standoff/ents[@source='ner-rb']/ent[@type='location']"):
        name = ent.find("./parts/part")
        lat = ent.attrib['lat'] if 'lat' in ent.attrib else "0.0"    # Any locations which remain NIL (0.0) must
        lon = ent.attrib['long'] if 'long' in ent.attrib else "0.0"  # be removed before evaluation for fairness
        targets.append((name.text, name.attrib, lat, lon))           # This happens only in around 2-4% of cases
    for target in targets:
        index, start, end = 0, 0, 0
        for word in root.findall("./text/p/s/w"):
            if word.attrib['id'] == target[1]['sw']:
                start = index
            index += len(word.text)
            if word.attrib['id'] == target[1]['ew']:
                end = index
            if word.attrib['pws'] != "no":
                index += 1
        if start == 0 and end == 0:
            print xml, targets
        toponyms.append(
            "No Gaz" + ",," + target[0] + ",," + target[2] + ",," + target[3] + ",," + str(start) + ",," + str(end))
    return toponyms


def run_edinburgh(path):
    """
    Opens a process and runs the Edinburgh Parser on the file specified by PATH and the output is returned.
    :param path: to the text file to be processed - THIS IS A VERY SLOW PROCESS, COMMAND LINE RUN MUCH FASTER!!!
    :return: A list of toponyms - format: [PLACEHOLDER STRING,,matched name,,lat,,long,,start index,,end index]
    """
    sp = subprocess.Popen("cat " + path + " | /Users/milangritta/Downloads/DATA/parsers/Edinburgh/scripts/run " +
                          "-t plain -g geonames -top", shell=True, stdout=subprocess.PIPE)
    return format_edinburgh(sp.stdout.read())


def run_geotext(q):
    """
    Run the query through the GeoTxt API service.
    :param q: Text to analyse. If the query length is more than 3900, the query is submitted in chunks
    :return: a list of toponyms - format: [PLACEHOLDER STRING,,matched name,,lat,,long,,start index,,end index]
    """
    base_url = 'http://geotxt.org/v2/api/geotxt.json?m=stanfords&'
    out = []  # list of tuples as output
    for start in range(0, len(q), 3000):
        query_chunk = q[start: start + 3000]
        response = urllib.urlopen(base_url + urllib.urlencode({'q': query_chunk}))  # contact servers
        if response.code != 200:
            print "Error Response Code =", response.code, " query length=", len(query_chunk)
            print response.info()
            return []
        res = json.loads(response.read())
        for m in res['features']:
            if m['geometry'] is not None:
                lat = m['geometry']['coordinates'][1]
                lon = m['geometry']['coordinates'][0]
                for pos in m['properties']['positions']:
                    name = m['properties']['name']
                    out.append(m['properties']['toponym'] + ",," + name + ",," + str(lat) +
                               ",," + str(lon) + ",," + str(pos + start) + ",," + str(len(name) + pos + start))
    return out


def all_results(corpus):
    """
    Print the statistics for all parsers for all metrics for paper write-up.
    :param corpus: the name of the corpus to evaluate
    :return: N/A
    """
    gold = calculate_scores(predicted="./data/" + corpus + "_gold.txt", gold="./data/" + corpus + "_gold.txt" , approach = 'gold')
    clavin = calculate_scores(predicted="./data/" + corpus + "_clavin.txt", gold="./data/" + corpus + "_gold.txt" , approach = 'clavin')
    edinburgh = calculate_scores(predicted="./data/" + corpus + "_edin.txt", gold="./data/" + corpus + "_gold.txt", approach ='edinburgh')
    yahoo = calculate_scores(predicted="./data/" + corpus + "_yahoo.txt", gold="./data/" + corpus + "_gold.txt", approach = 'yahoo')
    geo = calculate_scores(predicted="./data/" + corpus + "_geo.txt", gold="./data/" + corpus + "_gold.txt", approach = 'geo')
    mordecai_Original = calculate_scores(predicted="./data/" + corpus + "_mordecai_Original.txt", gold="./data/" + corpus + "_gold.txt", approach = 'mordecai_Original')
    mordecai_Modified = calculate_scores(predicted="./data/" + corpus + "_mordecai_Modified.txt", gold="./data/" + corpus + "_gold.txt", approach = 'mordecai_Modified')
    cliff = calculate_scores(predicted="./data/" + corpus + "_cliff.txt", gold="./data/" + corpus + "_gold.txt", approach = 'cliff')
    topo = calculate_scores(predicted="./data/" + corpus + "_topo.txt", gold="./data/" + corpus + "_gold.txt", topocluster=True, approach = 'topo')
    
    gl_keys = set(gold['accuracy'].keys())
    tc_keys = set(topo['accuracy'].keys())
    cl_keys = set(clavin['accuracy'].keys())
    ed_keys = set(edinburgh['accuracy'].keys())
    ya_keys = set(yahoo['accuracy'].keys())
    ge_keys = set(geo['accuracy'].keys())
    mordecai_Original_keys = set(mordecai_Original['accuracy'].keys())
    mordecai_Modified_keys = set(mordecai_Modified['accuracy'].keys())
    cliff_keys = set(cliff['accuracy'].keys())
    
    common_toponyms = cl_keys.intersection(ed_keys).intersection(ya_keys).intersection(ge_keys).intersection(tc_keys).intersection(mordecai_Original_keys).intersection(mordecai_Modified_keys).intersection(cliff_keys).intersection(gl_keys)
    print "Common toponyms count is", len(common_toponyms), "for a fair comparison on identical samples."
    for parser, name in zip([gold, clavin, edinburgh, yahoo, geo, topo, mordecai_Original, mordecai_Modified, cliff], ["Gold", "Clavin", "Edinburgh", "Yahoo", "GeoTxt", "Topocluster", "mordecai_Original", "mordecai_Modified", "cliff"]):
        acc = []
        for key in common_toponyms:
            acc.append(parser['accuracy'][key])
        print "Stats for", name
        print_stats(accuracy=parser['accuracy'].values(), scores=parser['f_score'])
        print '-' * 50
        print_stats(accuracy=acc)
        print '-' * 50


# EXAMPLE USAGE OF FUNCTIONS:
# prepare_lgl(path_to_xml='./lgl.xml', path_to_output='./data/lgl_gold.txt', directory="./lgl/")
# prepare_wiki(path_to_xml='./WikToR.xml', path_to_output='./data/wiki_gold.txt', directory="wiki")
# evaluate_parser(directory="/wiki/", function=run_clavin, out_file='./data/wiki_clavin.txt')
#data = calculate_scores(predicted="./data/lgl_edin.txt", gold="./data/lgl_gold.txt", topocluster=True)
#print_stats(accuracy=sorted(data['accuracy'].values()), scores=data['f_score'], plot=True)
##merge_files(directory="./wiki_topo", max_index=5000, prefix="", output_file="./data/wiki_topo.txt")
#accuracy = numpy.log([x + 1 for x in sorted(data['accuracy'].values())])
#print_stats(accuracy=accuracy, plot=True)
all_results(corpus="lgl")
