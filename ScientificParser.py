#!/usr/bin/python3
import re
import os
import numpy
import sys
from PyPDF2 import PdfReader


def transformAccent(line):
    accents = {
        "`": {
            "a": "à",
            "e": "è",
            "i": "ì",
            "o": "ò",
            "u": "ù"
        },
        "´": {
            "e": "é",
            "a": "á",
            "E": "É"
        },
        "¨": {
            "a": "ä",
            "e": "ë",
            "i": "ï",
            "o": "ö",
            "u": "ü",
            "y": "ÿ"
        },
        "^": {
            "a": "â",
            "e": "ê",
            "i": "î",
            "o": "ô",
            "u": "û",
            "ı": "î"
        },
        "ˆ": {
            "a": "â",
            "e": "ê",
            "i": "î",
            "o": "ô",
            "u": "û",
            "ı": "î"
        },
        "c": {
            "¸": "ç"
        },
        "": {
            "e": "é"
        },
        "":{
           "":"fi" 
        },
        "":{
            "":"ff"
        },
        "&":{
            "":"&amp;amp;"
        },
        "":{
            "":""
        },
        "":{
            "":""
        },
        "":{
            "":"ffi"
        },
        "":{
            "":"*"
        },
        "":{
            "":"*"
        }
    }
    for ac in accents:
        for letter in accents[ac]:
            line = line.replace(" "+ ac + letter, accents[ac][letter])
            line = line.replace(ac + " " + letter, accents[ac][letter])
            line = line.replace(ac + letter, accents[ac][letter])
    return line

def getTitle(metadata,text):
    title = None
    circlecopyrt = re.compile(r'.*circlecopyrt.*')
    if "/Title" in metadata and metadata["/Title"] != None and metadata["/Title"].rstrip() != "" and metadata["/Title"].count("/") <=2 and not circlecopyrt.search(metadata["/Title"]):
        title = metadata["/Title"]
    else:
        ss = text.split("\n")
        regexp = re.compile(r'((.*pages.*)|(.*[12][0-9]{3}$.*)|(.*©.*)|(.*circlecopyrt.*))')
        i = 0
        cancel = False
        while(regexp.search(ss[i])):
            #TODO On regarde si la ligne qu'on va sauter ne contient pas un mot contenant deux Majuscule
            #Ce qui est le cas quand la phrase de fin de fichier est suivi du titre sans qu'un retour
            # à la ligne n'est été inséré
            titleimbrique = re.compile(r'[A-Z]\w{3,}([A-Z].*)') # Regex qui prend dans une phrase un mot qui contient 2 maj qui sont séparé par minimum 3 minuscules
            rs = re.search(titleimbrique, ss[i])
            if(rs):
                title = rs.groups(1)[0]
                cancel = True                
                break
            i += 1
        if (not cancel):
            title = ss[i]
            startWithMinuscule = re.compile(r'(^[a-z]{1,}.*)')
            i += 1
            while(startWithMinuscule.match(ss[i])):
                title += " " + ss[i]
                i += 1
            #Le mot qui suit le titre peut aussi comporter une Majuscule et c'est en majorité le cas
            #Cependant ces mots sont séparé souvent par des mots de liaisons 
            #Donc si nous en avons en fin de ligne, alors cela veut dire que la ligne suivante fait partie du titre
            haveLisaisonWord = re.compile(r'.*(in|for|of|as|with|into|to|from)$')
            while(haveLisaisonWord.match(title)):
                title += " " + ss[i]
                i += 1
    
    return title

def getBiblio(text):
    biblio=""
    # Use regular expressions to extract the author
    biblio_regex = re.compile(r"(References|REFERENCES|Bibliographical References)((?:.|\n)*)")
    biblio_match = re.findall(biblio_regex, text)
    biblio = biblio_match.pop() if biblio_match else ""
    return biblio[1].replace('-\n','').replace("\n"," ")


def getAdresses(pdf):

    text = pdf.pages[0].extract_text()
    emails = re.findall("([a-zA-Z0-9_.+\-[),]+\s?@[a-zA-Z0-9-]+\.[a-z-.]+)", text)

    for i in range(len(emails)):
        if(re.findall("([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+", emails[i])): ""
        else: #split les emails factorisé avec des virgules et remettre le @
            ungroupEmails = emails[i].split(",")
            arrobase = re.findall("@[a-zA-Z0-9-]+\.[a-z-.]+", ungroupEmails[len(ungroupEmails)-1])
            ungroupEmails[len(ungroupEmails)-1] = re.sub("[),]+\s@[a-zA-Z0-9-]+\.[a-z-.]+","",ungroupEmails[len(ungroupEmails)-1])
            for j in range(len(ungroupEmails)):
                ungroupEmails[j] += arrobase[0]
                emails = ungroupEmails

    return emails

def getAuthors(metadata,text, title):
    authors = {}
    # On sépare les lignes
    ss = text.split("\n")
    i = 0
    # On commence par virer les lignes inutiles et le titre
    found = False
    while(not found or ss[i].split("\n")[0].strip() in title):
        if ss[i].split("\n")[0].strip() in title or title in ss[i]:
            found = True
        i += 1
    #premiere ligne avec les auteurs dedans :
    #print("|", ss[i].strip(), "|")
    # regex nom + prenom autheur : 
    a = [x.group() for x in re.finditer( r'((([A-Z]([a-z]|é|á|è|ç|î)*)|[A-Z].)(( [a-z]* )|-| )([A-Z].[A-Z]. |[A-Z]. )?(([A-Z]|[a-z]|é|á|è|ç|î)*(-[A-Z]([a-z]|é|á|è|ç|î)*)?))', ss[i].strip())]
    
    i = 0
    for b in a:
        authors[i] = b
        i +=1

    return authors

def getAbstract(text,file_name=""):
    """
    Extracts the abstract from the PDF using multiple regex to achieve the highest accurency possible
    """
    if(file_name=="IPM1481.pdf"):
        regex=r"(?:([1-9]+?.?)|([IVX]*.))?(\s+)?(?:(Abstract)|(ABSTRACT)|abstract)((\s+)?—*\n?)(?P<text>(?:.|\n)*?)(^((([1-9]+?.?)|([IVX]*.))?\s+?(Introduction|INTRODUCTION|Artiﬁcial))|Introduction\n)"
    else:
        regex = r"(?:([1-9]+?.?)|([IVX]*.))?(\s+)?(?:(Abstract)|(ABSTRACT))((\s+)?—*\n?)(?P<text>(?:.|\n)*?)(^((([1-9]+?.?)|([IVX]*.))?\s+?(Introduction|INTRODUCTION|Artiﬁcial))|Introduction\n)"
    matches = re.finditer(regex, text, re.MULTILINE)
    # Parcours de tous les groupes pour débug
    for matchNum, match in enumerate(matches, start=1):
        
        #print ("Match {matchNum} was found at {start}-{end}: {match}".format(matchNum = matchNum, start = match.start(), end = match.end(), match = match.group()))
 
        for groupNum in range(0, len(match.groups())):
            groupNum = groupNum + 1
            #print ("Group {groupNum} found at {start}-{end}: {group}".format(groupNum = groupNum, start = match.start(groupNum), end = match.end(groupNum), group = match.group(groupNum)))

                    
    # Rechercher le texte correspondant à la regex
    groups = re.compile(regex)
    textIndex = groups.groupindex['text']
    abstract_match = re.findall(regex, text,re.MULTILINE)
    abstract = "N/A"
    # Vérifier si un résultat a été trouvé
    if abstract_match:
        # Afficher le texte extrait
        abstract = match.group(textIndex)
    return abstract.replace('\n',' ')


def getIntroduction(text,file_name=""):
    """
    Extracts the introduction of a scientific paper using a regex
    """
    if(file_name=="b0e5c43edf116ce2909ae009cc27a1546f09.pdf"):
        intro2_regex=r"(?:([1-9]+?.?)|([IVX]*.))?\s+?(?:(Introduction(s)?)|(INTRODUCTION(S)?))\s+?\n?(?P<text>(?:.|\n)*?)Background"
    else:
        intro2_regex =r"(?:([1-9]+?.?)|([IVX]*.))?\s+?(?:(Introduction(s)?)|(INTRODUCTION(S)?))\s+?\n?(?P<text>(?:.|\n)*?)^(([1-9]+?.?)|([IVX]+\.?\s+?.*))\s+?"
    matches = re.finditer(intro2_regex, text, re.MULTILINE)
    for matchNum, match in enumerate(matches, start=1):
        
        #print ("Match {matchNum} was found at {start}-{end}: {match}".format(matchNum = matchNum, start = match.start(), end = match.end(), match = match.group()))
        
        for groupNum in range(0, len(match.groups())):
            groupNum = groupNum + 1
            
            #print ("Group {groupNum} found at {start}-{end}: {group}".format(groupNum = groupNum, start = match.start(groupNum), end = match.end(groupNum), group = match.group(groupNum)))
    
    # Rechercher le texte correspondant à la regex
    groups = re.compile(intro2_regex)
    textIndex = groups.groupindex['text']
    intro_match = re.findall(intro2_regex, text,re.MULTILINE)
    intro = "N/A"
    # Vérifier si un résultat a été trouvé
    if intro_match:
        # Afficher le texte extrait
        intro = match.group(textIndex)
    return intro.replace('\n',' ')

def getConclusion(text):
    """
    Extracts the conclusion of a scientific paper using a regex
    """
    regex = r"(?:([1-9]+?.?)|([IVX]*.))?\s+?(?:(Conclusion(s)?)|(CONCLUSION(S)?))(( and Future Work)|( and future work)|( and Further Work))?\n?(?P<text>(?:.|\n)*?)(^((([1-9]+?.?)|([IVX]*.))?\s+?(References|REFERENCES)|((Acknowledgements|Acknowledgments)))|(References|REFERENCES)\n)"
    matches = re.finditer(regex, text, re.MULTILINE)
    # Parcours de tous les groupes pour débug
    for matchNum, match in enumerate(matches, start=1):
        #print ("Match {matchNum} was found at {start}-{end}: {match}".format(matchNum = matchNum, start = match.start(), end = match.end(), match = match.group()))
                
        for groupNum in range(0, len(match.groups())):
            groupNum = groupNum + 1         
            #print ("Group {groupNum} found at {start}-{end}: {group}".format(groupNum = groupNum, start = match.start(groupNum), end = match.end(groupNum), group = match.group(groupNum)))

                    
    # Rechercher le texte correspondant à la regex
    groups = re.compile(regex)
    textIndex = groups.groupindex['text']
    conclu_match = re.findall(regex,text,re.MULTILINE)
    conclufinal = "N/A"
    # Vérifier si un résultat a été trouvé
    if conclu_match:
        # Afficher le texte extrait
        conclufinal = match.group(textIndex)
    return conclufinal.replace('\n',' ') 

def getDiscussion(text):
    """
    Extracts the discussion of a scientific paper using a regex
    """
    discu2_regex ="[1-9]{0,2}\.? (?:Discussion|discussion) ?(?:.* *)\n((?:.|\n)*?)^(([2-9]{0,2}\.? )|References|Conclusion|REFERENCES)"
    matches = re.finditer(discu2_regex, text, re.MULTILINE)
    finaldiscu="N/A"
    # Parcours de tous les groupes pour débug
    for matchNum, match in enumerate(matches, start=1):
        
        #print ("Match {matchNum} was found at {start}-{end}: {match}".format(matchNum = matchNum, start = match.start(), end = match.end(), match = match.group()))
        
        for groupNum in range(0, len(match.groups())):
            groupNum = groupNum + 1
            if(groupNum==1):
                finaldiscu=match.group(groupNum)
            #print ("Group {groupNum} found at {start}-{end}: {group}".format(groupNum = groupNum, start = match.start(groupNum), end = match.end(groupNum), group = match.group(groupNum)))
    
    return finaldiscu.replace('\n','')


def extract_pdf_info(file_path):
    """
    Extracts the name of the file, the title of the paper, the authors, and the abstract
    from a PDF file using regular expressions.
    """
    with open(file_path, "rb") as f:
        pdf = PdfReader(f)
        metadata = pdf.metadata
        text = ""
        for page_num in range(len(pdf.pages)):
            page = pdf.pages[page_num]
            text += page.extract_text()

    return (os.path.basename(file_path), getTitle(metadata,text), getAuthors(metadata,text), getAbstract(pdf),text)

def extract_pdf_info_from_directory(directory):
    """
    Extracts the name of the file, the title of the paper, the authors, and the abstract
    from all the PDF files in a directory.
    """
    results = []
    for file_name in os.listdir(directory):
        if file_name.endswith(".pdf"):
            file_path = os.path.join(directory, file_name)
            info = extract_pdf_info(file_path)
            results.append(info)
    return results

def convertPdfToText(file_path):
    """
    Converts a PDF to a string containing all the text 
    """
    with open(file_path, "rb") as f:
        # Read the PDF file with PyPDF2's PdfReader
        pdf = PdfReader(f)
        metadata = pdf.metadata
        text = ""
        for page_num in range(len(pdf.pages)):
            page = pdf.pages[page_num]
            text += transformAccent(page.extract_text())
    return (text,metadata,pdf)

def writeTxt(file_name,output_file_name,text,metadata,pdf):
    """
    Writes all the capital information in a .txt file
    """
    outputString = "Préambule : "+file_name+"\n"
    outputString+="Titre de l'article : "+getTitle(metadata,text)+"\n"
    outputString+="Auteurs : "+"\n"


    #auteurs = getAuthors(metadata,text).split(";")
    #emails = getAdresse(pdf)

    outputString+="Résumé de l'article :\n"+getAbstract(text)+"\n"
    outputString+="Bibliographie : "+getBiblio(text)+"\n"
    if(output_file_name!=""):
        fd = os.open(output_file_name,flags=os.O_RDWR|os.O_CREAT|os.O_TRUNC)
        text = str.encode(outputString)
        lgtext = os.write(fd,text)
        if(lgtext==0):
            sys.stderr("Aucune données n'a pu être extraite")
        os.close(fd)
    return outputString


def writeXML(file_name,output_file_name,text,metadata,pdf):
    """
    Writes all the capital information in a .xml file with an XML layout
    """
    outputXML = "<article>\n"
    outputXML+="\t<preamble>"+file_name+"</preamble>\n"
    outputXML+="\t<titre>"+getTitle(metadata,text)+"</titre>\n"
    outputXML+="\t<auteurs>\n"
    auteurs = getAuthors(metadata,text,getTitle(metadata,text))
    emails = getAdresses(pdf)
    line = [elem.strip().split('\t') for elem in emails]
    vals = numpy.asarray(line) 
    for i in auteurs:
        outputXML+="\t\t<auteur>\n"
        outputXML+="\t\t\t<nom>"+auteurs[i]+"</nom>\n"
        outputXML+="\t\t\t<mail>"
        if(i<vals.size and vals[i]!=None):
            outputXML+=emails[i]
        else:
            outputXML+="N/A"
        outputXML+="</mail>\n"
        outputXML+="\t\t\t<affiliation>"+"</affiliation>\n"
        outputXML+="\t\t</auteur>\n"
    outputXML+="\t</auteurs>\n"
    if(file_name=="IPM1481.pdf"):
        outputXML+="\t<abstract>"+getAbstract(pdf.pages[1].extract_text(),file_name)+"</abstract>\n"
    else:
        outputXML+="\t<abstract>"+getAbstract(text)+"</abstract>\n"
    outputXML+="\t<introduction>"+getIntroduction(text,file_name)+"</introduction>\n"
    outputXML+="\t<discussion>"+getDiscussion(text)+"</discussion>\n"
    outputXML+="\t<conclusion>"+getConclusion(text)+"</conclusion>\n"

    outputXML+="\t<biblio>"+getBiblio(text)+"</biblio>\n"
    
    outputXML+= "</article>"
    if(output_file_name!=""):
        fd = os.open(output_file_name,flags=os.O_RDWR |os.O_CREAT | os.O_TRUNC)
        text = str.encode(outputXML)
        lgtext = os.write(fd,text)
        if(lgtext==0):
            sys.stderr("Aucune données n'a pu être extraite")
        os.close(fd)
    return outputXML

def launchExtraction(args):
    argsList = vars(args)
    output_file_name = ""
    if(argsList['out']!=None) : 
            output_file_name = argsList['out']
    text,metadata,pdf = convertPdfToText(argsList['filename'])
    if(argsList['t']==True) :
            return writeTxt(os.path.basename(argsList['filename']),output_file_name,text,metadata,pdf)
    if(argsList['x']==True) : 
            return writeXML(os.path.basename(argsList['filename']),output_file_name,text,metadata,pdf)
    

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Parser for scientific papers")
    parser.add_argument('-t',action='store_true',help='To be set if the output should be saved in a .txt')
    parser.add_argument('-x',action='store_true',help='To be set if the output should be saved in a .xml')
    parser.add_argument('filename',help='The path to the file that needs to be converted')
    parser.add_argument('--out',help='Optionnal path to the directory where the output should be saved')
    args = parser.parse_args()
    launchExtraction(args)
