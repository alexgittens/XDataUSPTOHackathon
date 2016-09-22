import lxml.etree as etree
import numpy as np
import pandas as pd
from os import listdir
import gzip
import gc
import re

def extractGrantInfo(flist):
    """Takes a list of filenames (.xml.gz) and returns a dataframe populated with the grant information they contain"""
    parser = etree.XMLParser(remove_blank_text=True)
    
    skippedCount = 0
    patentApplicationDocNumbers = []
    applicationDates = []
    applicationTypes = []
    publishedPatentDocNumbers = []
    patentPublicationDates = []
    ipcrTypes = []
    inventionTitles = []
    abstracts = []
    examinerCitationsList = []
    applicantCitationsList = []
    originalFileNames = []
    originalLineNumbers = []
    
    for (filenum, fname) in enumerate(flist):
        with gzip.open(fname, 'rb') as fin:
            print("on file {0} of {1}, have {2} patents so far".format(filenum+1, len(flist), len(patentApplicationDocNumbers)))
            for (lineNumber, line) in enumerate(fin):
                try:
                    root = etree.fromstring(line, parser)
                except etree.XMLSyntaxError:
                    skippedCount = skippedCount + 1
                    continue
                
                try:
                    ipcrSection = root.find("us-bibliographic-data-grant/classifications-ipcr/classification-ipcr/section")
                    ipcrClass = root.find("us-bibliographic-data-grant/classifications-ipcr/classification-ipcr/class")
                    ipcrSubclass = root.find("us-bibliographic-data-grant/classifications-ipcr/classification-ipcr/subclass")
                    ipcrType = (ipcrSection.text + ipcrClass.text + ipcrSubclass.text)
                except AttributeError:
                    ipcrType = 'Missing'
                
                try:
                    applicationType = root.find("us-bibliographic-data-grant/application-reference").attrib.get("appl-type")
                except AttributeError:
                    applicationType = "Missing"
                    print("Missing application type")
            
                # get basic data
                applicationDate = root.find("us-bibliographic-data-grant/application-reference/document-id/date").text
                patentPublicationDate = root.find("us-bibliographic-data-grant/publication-reference/document-id/date").text
                publishedPatentDocNumber = root.find("us-bibliographic-data-grant/publication-reference/document-id/doc-number").text
                patentApplicationDocNumber = root.find("us-bibliographic-data-grant/application-reference/document-id/doc-number").text
                kind = root.find("us-bibliographic-data-grant/publication-reference/document-id/kind").text
                
                applicationType = root.find("us-bibliographic-data-grant/application-reference").attrib.get("appl-type")
                inventionTitle = root.find("us-bibliographic-data-grant/invention-title").text
                numberOfClaims = root.find("us-bibliographic-data-grant/number-of-claims").text
                
                # give entries without abstracts empty abstracts
                abstract = ""
                if root.find("abstract") is not None:
                    abstract = etree.tostring(root.find("abstract"), encoding='UTF-8', method="text").decode('UTF-8')
                
                referencesCited = root.find("us-bibliographic-data-grant/references-cited")
                
                examinerCitations = []
                applicantCitations = []
                if referencesCited is not None:
                    # remove non-patent citations
                    referencesCited = referencesCited.getchildren()
                    referencesCited = [citation for citation in referencesCited if citation.find("patcit") is not None]
                    for citation in referencesCited:
                        citationCountry = citation.find("patcit/document-id/country").text
                        if (citationCountry != "US"):
                            continue
                        citationDocNum = citation.find("patcit/document-id/doc-number").text
                        citationType = etree.tostring(citation.find("category"), method="text")
                        if citationType == b'cited by examiner':
                            examinerCitations.append(citationDocNum)
                        else:
                            applicantCitations.append(citationDocNum)
                
                #add the information to the DataFrame
                patentApplicationDocNumbers.append(patentApplicationDocNumber)
                applicationDates.append(applicationDate)
                applicationTypes.append(applicationType)
                publishedPatentDocNumbers.append(publishedPatentDocNumber)
                patentPublicationDates.append(patentPublicationDate)
                ipcrTypes.append(ipcrType)
                inventionTitles.append(inventionTitle)
                abstracts.append(abstract)
                examinerCitationsList.append(examinerCitations)
                applicantCitationsList.append(applicantCitations)
                originalFileNames.append(fname)
                originalLineNumbers.append(lineNumber)

    df = pd.DataFrame.from_dict({'patentApplicationDocNumber': patentApplicationDocNumbers,
                            'applicationDate': applicationDates,
                            'applicationType': applicationTypes,
                            'publishedPatentDocNumber': publishedPatentDocNumbers,
                            'ipcrType': ipcrTypes,
                            'inventionTitle' : inventionTitles,
                            'abstract': abstracts,
                            'examinerCitations': examinerCitationsList,
                            'applicantCitations': applicantCitationsList,
                            'originalFileName': originalFileNames,
                            'originalLineNumber': originalLineNumbers})
    
    print("Skipped {0} records due to parsing errors".format(skippedCount))
    return df

basedir = "/Users/gittens/Downloads/uspto-grants/bibliographic_data"
numchunks = 8
# ignore the pgb* files, because those have an entirely different format
filelist = [basedir + "/" + fname for fname in listdir(basedir) if not re.match('^pgb', fname)]
chunksOfFiles = np.array_split(filelist, numchunks)

for (chunkNum, chunk) in enumerate(chunksOfFiles):
    df = extractGrantInfo(chunk)
    df.to_pickle("chunk{0}.pickle".format(chunkNum))
    gc.collect()

df = pd.read_pickle("chunk0.pickle")
for chunkNum in range(1, len(chunkOfFiles)):
    df = df.append(pd.read_pickle("chunk{0}.pickle".format(chunkNum)))
    gc.collect()
df.reset_index(inplace=True,drop=True)
df.to_pickle("uspto_grant_all_bibliographic_data.pickle")
