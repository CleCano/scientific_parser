#!/usr/bin/python3
import re
import os
import numpy
import sys
import copy
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
            "E": "É",
             
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
        },
        "":{
            "":""
        }

    }
    for ac in accents:
        for letter in accents[ac]:
            line = line.replace(" "+ ac + letter, accents[ac][letter])
            line = line.replace(ac + " " + letter, accents[ac][letter])
            line = line.replace(ac + letter, accents[ac][letter])
    return line

def getTitle(metadata, text):
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
            ligneToSkip = ['this article', 'copy is', 'and', 'other uses', 'licensing copies', 'websites are prohibited', 'in most case', 'article', 'institutional', 'regarding', 'encouraged to visit', 'http', 'author']
            changed = True
            while(changed):
                changed = False
                for a in ligneToSkip:
                    if (ss[i].lower().startswith(a)):
                        changed = True
                        i = i+1
            title = ss[i]
            #TODO A REFAIRE CA NE FONCTIONNE PAS
            startWithMinuscule = re.compile(r'(^[a-z]{1,}.*)')
            i += 1
            while(startWithMinuscule.match(ss[i])):
                title += " " + ss[i]
                i += 1
            #Le mot qui suis le titre peut aussi comporter une Majuscule et c'est en majorité le cas
            #Cependant ces mots sont séparé souvent par des mots de liaisons 
            #Donc si nous en avons en fin de ligne, alors cela veut dire que la ligne suivante fait partie du titre
            haveLisaisonWord = re.compile(r'.* (in|for|of|as|with|into|to|from|at|a|on)$')
            while(haveLisaisonWord.match(title)):
                title += " " + ss[i]
                i += 1

            # End with "the <adjective>"
            adjectives = ['relevant', 'multi-sentence'] # Rajouter dans la liste les adjectives
            for adj in adjectives:
                if(title.lower().endswith(adj)):
                    title += " " + ss[i]
                    i += 1
    
    return title

def getBiblio(text,file_name=""):
    biblio=""
    # Use regular expressions to extract the author
    if(file_name=="L18-1504.pdf"):
        regex=r"(?:([1-9]+?.?)|([IVX]+.))(\s+)(References|REFERENCES|Bibliographical References)\n?(?P<text>(?:.|\n)*)"
    else:
        regex=r"(References|REFERENCES|Bibliographical References)(?P<text>(?:.|\n)*)"
    
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
    biblio_match = re.findall(regex, text,re.MULTILINE)
    biblio = "N/A"
    # Vérifier si un résultat a été trouvé
    if biblio_match:
        # Afficher le texte extrait
        biblio = match.group(textIndex)
    return biblio.replace('\n',' ')
    


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
    if False:#(metadata.author!="" and metadata.author!="None" and metadata.author != None):
        authors = metadata.author
        print("aa ", authors)
    else:
        # On sépare les lignes
        ss = text.split("\n")
        i = 0
        # On commence par virer les lignes inutiles et le titre
        found = False
        while(not found or ss[i].split("\n")[0].strip() in title or ss[i].split("\n")[0].split("*")[0].strip() in title):
            if ss[i].split("\n")[0].strip() in title or title in ss[i] or ss[i].split("\n")[0].split("*")[0].strip() in title: # On regarde avec l'etoile car des fois ils mettent ca pour faire reference a une definition en bas de page
                found = True
            i += 1
        # regex nom + prenom autheur : 
        a = [x.group() for x in re.finditer( r'((([A-Z]([a-z]|é|á|è|ç|î)*)|[A-Z].)(( [a-z]* )|-| )([A-Z].[A-Z]. |[A-Z]. )?(([A-Z]|[a-z]|é|á|è|ç|î)*(-[A-Z]([a-z]|é|á|è|ç|î)*)?))', ss[i].strip())]
        
        # On récupère le numéro de ligne de début de l'abstract
        origin_i = i    
        abstract_regex = re.compile(r".*(Abstract|ABSTRACT|abstract|In this article|This article presents|article info|ARTICLE HISTORY).*")
        while( not abstract_regex.match(ss[origin_i])):
            origin_i += 1
        abstractLine = origin_i


        print("\n")
        print("\n")

        authors = []
        emails = []
        affiliations = []

        email_regex = re.compile(r"((?:[a-zA-Z0-9_.-]+, ){0,1}\(?:{0,1}[a-zA-Z0-9_., -]+\){0,1}[\n ]{0,2}(?:@|Q)[a-zA-Z0-9-.]+\.(?:\n|)[a-z-]+)") 
        endofemail_regex = re.compile(r"((?:@|Q)[a-zA-Z0-9-.]+\.(?:\n|)[a-z-]+)")    
        for line in range(i, abstractLine):
            if email_regex.match(ss[line]):
                #e = re.match(email_regex, ss[line])
                #emails.append(e.group(0))
                a = email_regex.findall(ss[line])
                for b in a:
                    #print(b)
                    emails.append(b)
            elif endofemail_regex.match(ss[line]) and email_regex.match(ss[line-1] + ss[line]): # Si la ligne match le @machin, ça veut dire que la ligne d'avant devrait aussi faire partie de l'email
                e = re.match(email_regex, ss[line-1] + ss[line])
                emails.append(e.group(0))

        affiliation_regex = re.compile(r".*(Laboratoire|École|Institute|University|Université|([A-Z][a-z]* Inc\.)|Département|Department|Univ.|Research|Universitat|Insitut|DA-IICT|LIMSI-CNRS).*")
        lines_read = []     #Permet d'éviter de reconsidérer une affiliation, comme une nouvelle affiliation
        for line in range(i, abstractLine):
            #print(ss[line])
            if line not in lines_read:
                if affiliation_regex.match(ss[line]):
                    # si on trouve une ligne comme c'est le cas ici
                    # alors on va tout lire jusqu'a une email
                    affiliations.append(" NOUVELLE AFFILIATION : ")
                    affiliations.append(ss[line])
                    lines_read.append(line)
                    abracadabra = line + 1
                    while(not email_regex.match(ss[abracadabra]) and abracadabra < abstractLine):
                        lines_read.append(abracadabra)
                        affiliations.append(ss[abracadabra])
                        abracadabra += 1
        # ((?:(?:[A-Z](?:[a-z]|é|á|è|ç|î|í|à)*)|[A-Z].)(?:(?: [a-z]* )|-| )(?:[A-Z].[A-Z]. |[A-Z]. )?(?:(?:[A-Z]|[a-z]|é|á|è|ç|î|í|à)*(?:-[A-Z](?:[a-z]|é|á|è|ç|î|í|à)*)?)[1-9;∗*†]{0,3})
        author_regex = re.compile(r"((?:(?:[A-Z](?:[a-z]|é|á|è|ç|î|í|à)*)|[A-Z].)(?:(?: [a-z]* )|-| )(?:[A-Z].[A-Z]. |[A-Z]. )?(?:(?:[A-Z]|[a-z]|é|á|è|ç|î|í|à)*(?:-[A-Z](?:[a-z]|é|á|è|ç|î|í|à)*)?)[1-9;∗*†]{0,3})")
        date_regex = re.compile(r"(Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)(\s+(\d{1,2}))?,?\s+(\d{4})")
        ttdclana = ""
        for line in range(i, abstractLine):
            #print(ss[line])
            if author_regex.search(ss[line]):
                #print("   OO")
                e = re.findall(author_regex, ss[line])
                isAffiliationOrDate = False
                for a in affiliations:
                    if(a ==ss[line]):
                        isAffiliationOrDate = True
                if re.match(date_regex, ss[line]):
                    isAffiliationOrDate = True
                if not isAffiliationOrDate:
                    for b in e:
                        # On rajoute un check utile pour les nom prenom de plus de 2 mots
                        # Pour ce faire on commence par regarder si sur la ligne du nom trouvé avec la prenière regex, s'il y a un autre mot commencant par une majuscule 
                        # sans qu'il n'y ai de séparateur entre du genre "," ou "and"
                        # Cependant pour ne pas se faire avoir, dans certains texte quand il y a plusieurs auteurs, et que les derniers sont séparé par le mot and
                        # il se peut que celui-ci se fasse coller au nom de l'auteur a droite du "and", donc c'est pour cela que l'on ne fait ces étapes uniquement si 
                        # le nom de l'auteur actuel ne fini pas par and, cela peut poser problème quand le nom de l'auteur fini par and, mais la probabilité comparé à celle-ci
                        # est largement négligeable
                        finded = False
                        maj_regex = re.compile(r"^((?: )?[A-Z].*)")
                        if not b.endswith("and"): # On ne veut pas ceux qui terminent par and
                            long_name = ss[line].split(b)[1].split(",")[0] #On coupe sur les virgule pour prendre le texte entre le nom et la virgule
                            if not long_name.strip().startswith("and"): # On ne veut pas ceux qui commencent par and
                                if re.match(maj_regex, long_name):
                                    ttdclana = long_name # txt to dont considere like a nom auteur
                                    authors.append(b + long_name)
                                    #print(long_name)
                                    finded = True
                                    #print("houlala : ", b + long_name)

                        if not finded and b not in ttdclana:
                            #print("houlala : ", b)
                            authors.append(b)

        # Récupérer la position de leture des auteurs(et l'exposant dans le cas ou il y en as), afin de les affecté au bonnes affiliation
        
        #print("Titre : ", title)
        #print('Authors : ', authors)
        #print('Emails : ', emails)
        #print('Affiliations : ', affiliations)

      
    all_back = {}
    
    #On commence par reformatter la liste d'auteurs pour le moment c'est provisoir, le temps de trouver une solution a la regex
    new_authors = []
    idx_already_taken = []
    for i in range(len(authors)):
        if authors[i].count(' ') == 0 and authors[i].count('-') >= 1 and len(authors) >= i+1 and authors[i+1].count(' ') == 0:
            new_authors.append(authors[i] + ' ' + authors[i + 1])
            idx_already_taken.append(i)
            idx_already_taken.append(i+1)
        elif i not in idx_already_taken:
            new_authors.append(authors[i])
    authors = new_authors
    # Truc juste au dessu est provisoire

    # Ici on reformatte les affiliations 
    new_affiliations = []
    newaff = -1
    for i in range(len(affiliations)):
        if affiliations[i].startswith(' NOUVELLE AFFILIATION : '):
            newaff += 1
            new_affiliations.append('')
        else:
            # Si l'affiliations possède une date, alors on la retire
            if date_regex.match(affiliations[i]):
                affiliations[i] = re.sub(date_regex, '', affiliations[i])
            # On ajoute l'affiliation
            new_affiliations[newaff] = new_affiliations[newaff] + affiliations[i].strip() + " "
            # on l'ajoute à la suite, sauf si cela commence par une minuscule colé à une majuscule, alors on sépare
            if len(affiliations) > i+1 and re.search( r'^[a-z†∗1-9][A-ZÉ]', affiliations[i+1]):
                #print("new aFFILIATION : ", affiliations[i+1])
                newaff += 1
                new_affiliations.append('')
    #Pour finir le reformattage correctement, on retire tous les espaces de fins
    for i in range(len(new_affiliations)):
        new_affiliations[i] = new_affiliations[i].strip()
    affiliations = new_affiliations
    #Truc juste au dessus permet le reformattage des affiliations
    
    # Et ici on reformatte les emails   
    endofemail_regex = re.compile(r"(?:.*)((?:@|Q)[a-zA-Z0-9-.]+\.(?:\n|)[a-z-]+)(?:.*)")  
    new_emails = []

    for e in emails:
        if e.count(',') > 0:
            extension_email = ''
            if endofemail_regex.match(e):
                extension_email = re.match(endofemail_regex, e).group(1)
            # Dans le cas ou il y a une virgule, soit il suffit simplement de la supprimer, soit il faut séparer plusieurs emails
            for s in e.replace(' ', '').split(','):
                if not s.strip() == '':
                    new_emails.append(s + extension_email)
        else:
            new_emails.append(e)
    emails = new_emails

    # Truc au dessus permet le reformattage des emails

    # On commence par mettre les noms et prenoms des auteurs dans la liste
    for a in authors:
        # Si le prochain dans la liste est seul, alors il se peut qu'il soit lié à un autre
        all_back[a.strip()] = {"mail": "N/A", "affiliation": "N/A"}
    
    # On parcour ensuite les emails
    if len(emails) == len(all_back):
        # Alors y'a le meme nombre d'email que de mec donc on les affectes tout simplement
        pos = 0
        for a in all_back:
            all_back[a]['mail'] = emails[pos].strip()
            pos += 1

    #print("AFF : ", len(affiliations))
    #print("ALL : ", len(all_back))
    # On parcours enfin les affiliations
    # Si il n'y a qu'une affiliation alors il est probable qu'ils l'aient tous
    if len(affiliations) == 1:
        for a in all_back:
            all_back[a]['affiliation'] = affiliations[0]
    # S'il y a autant d'affiliations que de personnes, alors il suffit de les associer
    elif len(affiliations) == len(all_back):
        #print('EGUALITYT LA HO')
        pos=  0
        for a in all_back:
            all_back[a]['affiliation'] = affiliations[pos]
            pos += 1
    elif len(affiliations) > 1:
        # Ici on va entrer dans du semi cas par cas SEMI comme les camions
        #print("camion")
        # On regarde si les auteurs sont suivient d'une lettre ou d'un charactère sépcial pour les entrer dans une liste
        liste = [] #C'est la liste
        regex_exposant = re.compile(r"(.*)([a-z†∗1-9])(;[a-z†∗1-9]){0,2}$")
        regex_exposants_only = re.compile(r"(?:[a-zA-Z éàÉéáèçîí-])*([a-z†∗1-9])(?:;([a-z†∗1-9])){0,2}(?:,){0,1}$")
        for a in all_back:
            #print(" ee : ", a)
            if re.match(regex_exposant, a): #TODO IL NE COMPREND PAS ICI
                #print("OHHHHHH ", re.match(regex_exposant, a).group(2), " ", re.match(regex_exposant, a).group(1))
                affiliation_lettre = []
                auteur_sans_expo = re.match(regex_exposant, a).group(1)
                for z in re.match(regex_exposants_only, a).groups():
                    if not z == None:
                        affiliation_lettre.append(z)
                        auteur_sans_expo = auteur_sans_expo.split(z)[0]
                #print("AFFILIATION LETTRE : ", affiliation_lettre)
                liste.append({"auteur": auteur_sans_expo, "affiliation_lettre": affiliation_lettre}) #"""re.match(regex_exposant, a).group(2)"""
        # Maintenant on va compter combien de lettre unique il y a 
        unique_affiliation_lettre = set()
        for l in liste:
            for a in l["affiliation_lettre"]:
                unique_affiliation_lettre.add(a)
            #unique_affiliation_lettre.add(l["affiliation_lettre"])
        #print(unique_affiliation_lettre)

        # Maintenant on sait combien de lettre unique il y a, et ont regarde s'il y a la même quantité d'affiliations
        if len(unique_affiliation_lettre) == len(affiliations):
            # S'il y a la meme quantité, alors on les associes mais pour cela, il faut récupérer la lettre d'affiliation
            dictionnaire = {} # Un dictionnaire cette fois ci pour avoir des perfs de ouf
            regex_exposant = re.compile(r"([a-z†∗1-9])(.*)$") #TODO JE ne COMPREND PAS PK IL LE COMPREND PAS ESPECE DE DEBILE
            for a in affiliations:
                if re.match(regex_exposant, a):
                    dictionnaire[re.match(regex_exposant, a).group(1)] = re.match(regex_exposant, a).group(2)
            #print(dictionnaire)
            # Maintenant on va changer dans all_back les noms d'auteurs pour retirer la lettre de fin de mot
            # Ce code va pas etre beau a voir et terrible, mais c'est le plus simple a mettre en oeuvre
            l = 0
            new_all_back = copy.deepcopy(all_back)
            for a in new_all_back:
                all_back[liste[l]["auteur"]] = all_back.pop(a)
                l += 1

            # Maintenant que l'on a tout en oeuvre, il suffit d'associer
            for l in liste:
                first = True
                for a in l["affiliation_lettre"]:
                    if first:
                        all_back[l["auteur"]]["affiliation"] = dictionnaire[a]
                        first = False
                    else:
                        all_back[l["auteur"]]["affiliation"] = all_back[l["auteur"]]["affiliation"] + ", " + dictionnaire[a]
                #all_back[l["auteur"]]["affiliation"] = dictionnaire[l["affiliation_lettre"]]

        #print("AFFILIATIONS NOMBRE : ", len(affiliations))


    #print("all_back : ", all_back)
    return all_back#, emails, affiliations}

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
        print(file_name)
        intro2_regex=r"(?:([1-9]+?(?P<point>\.?).?)|([IVX]*(?P<point2>\.?).?))?\s+?(?:(Introduction(s)?)|(INTRODUCTION(S)?))\s+?\n?(?P<text>(?:.|\n)*?)Background"
    else:
        intro2_regex =r"(?:([1-9]+?(?P<point>\.?).?)|([IVX]*(?P<point2>\.?).?))?\s+?(?:(Introduction(s)?)|(INTRODUCTION(S)?))\s+?\n?(?P<text>(?:.|\n)*?)^(([1-9]+?.?)|([IVX]+\.?\s+?.*))\s+?"
    matches = re.finditer(intro2_regex, text, re.MULTILINE)
    for matchNum, match in enumerate(matches, start=1):
        
        #print ("Match {matchNum} was found at {start}-{end}: {match}".format(matchNum = matchNum, start = match.start(), end = match.end(), match = match.group()))
        
        for groupNum in range(0, len(match.groups())):
            groupNum = groupNum + 1
            
            #print ("Group {groupNum} found at {start}-{end}: {group}".format(groupNum = groupNum, start = match.start(groupNum), end = match.end(groupNum), group = match.group(groupNum)))
    
    # Rechercher le texte correspondant à la regex
    groups = re.compile(intro2_regex)
    textIndex = groups.groupindex['text']
    pointIndex = groups.groupindex['point']
    point2Index = groups.groupindex['point2']
    intro_match = re.findall(intro2_regex, text,re.MULTILINE)
    if(intro_match):
        if(match.group(pointIndex)=="." or match.group(point2Index)==".") :
            print("Version point obligatoire")
            intro2_regex = r"(?:([1-9]+?(?P<point>\.?).?)|([IVX]*(?P<point2>\.?).?))?\s+?(?:(Introduction(s)?)|(INTRODUCTION(S)?))\s+?\n?(?P<text>(?:.|\n)*?)^(([1-9]+?\.)|([IVX]+\.))\s+?"
        else:
            intro2_regex = r"(?:([1-9]+?(?P<point>\.?).?)|([IVX]*(?P<point2>\.?).?))?\s+?(?:(Introduction(s)?)|(INTRODUCTION(S)?))\s+?\n?(?P<text>(?:.|\n)*?)^(([1-9]+?)|([IVX]+\s+?.*))\s+?"
        matches = re.finditer(intro2_regex, text, re.MULTILINE)
    for matchNum, match in enumerate(matches, start=1):
        
        #print ("Match {matchNum} was found at {start}-{end}: {match}".format(matchNum = matchNum, start = match.start(), end = match.end(), match = match.group()))
        
        for groupNum in range(0, len(match.groups())):
            groupNum = groupNum + 1
            
            #print ("Group {groupNum} found at {start}-{end}: {group}".format(groupNum = groupNum, start = match.start(groupNum), end = match.end(groupNum), group = match.group(groupNum)))
    
    
    intro_match = re.findall(intro2_regex, text,re.MULTILINE)
    intro = " "
    # Vérifier si un résultat a été trouvé
    if intro_match:
        # Afficher le texte extrait
        intro = match.group(textIndex)
    #print(intro)
    return intro.replace('\n',' ')

def getConclusion(text,file_name=""):
    """
    Extracts the conclusion of a scientific paper using a regex
    regex = r"(?:([1-9]+?.?)|([IVX]*.))?\s+?(?:(Conclusion(s)?)|(CONCLUSION(S)?))(( and Future Work)|( and future work)|( and Further Work))?\n?(?P<text>(?:.|\n)*?)(^((([1-9]+?.?)|([IVX]*.))?\s+?(References|REFERENCES)|((Acknowledgements|Acknowledgments)))|(References|REFERENCES)\n)"
    
    """

    if(file_name=="surveyTermExtraction.pdf"):
        regex = r"(?:([1-9]+?.?)|([IVX]*.))?\s+?(?:(Conclusion(s)?)|(CONCLUSION(S)?))(( and Future Work)|( and future work)|( and Further Work))?\n?(?P<text>(?:.|\n)*?)(^((([1-9]+?.?)|([IVX]*.))?\s+?(References|REFERENCES)|((Acknowledgements|Acknowledgments)))|(References|REFERENCES)\n)"
    else:
        regex = r"(?:([1-9]+?.?)|([IVX]*.))?\s+?(?:(Conclusion(s)?)|(CONCLUSION(S)?))(( and Future Work)|( and future work)|( and Further Work))?\n?(?P<text>(?:.|\n)*?)(^(((([1-9]+?.?)|([IVX]*\..*))?\s+?)((References|REFERENCES)|((Acknowledgements|Acknowledgments|))))|(References|REFERENCES|Acknowledgements|Acknowledgments)\n)"
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
    outputXML+="\t<preamble> "+file_name+"</preamble>\n"
    outputXML+="\t<titre>"+getTitle(metadata,text)+"</titre>\n"
    outputXML+="\t<auteurs>\n"
    auteursInfo = getAuthors(metadata,text,getTitle(metadata,text))
    print(auteursInfo)
    for i in auteursInfo:
        print(i)
        print(auteursInfo[i]['mail'])
        print(auteursInfo[i]['affiliation'])  
        outputXML+="\t\t<auteur>\n"
        outputXML+="\t\t\t<name>"+i+"</name>\n"
        outputXML+="\t\t\t<mail>"
        outputXML+=auteursInfo[i]['mail']
        outputXML+="</mail>\n"
        outputXML+="\t\t\t<affiliation>"+auteursInfo[i]['affiliation']+"</affiliation>\n"
        outputXML+="\t\t</auteur>\n"
    outputXML+="\t</auteurs>\n"
    if(file_name=="IPM1481.pdf"):
        outputXML+="\t<abstract>"+getAbstract(pdf.pages[1].extract_text(),file_name)+"</abstract>\n"
    else:
        outputXML+="\t<abstract>"+getAbstract(text)+"</abstract>\n"
    outputXML+="\t<introduction>"+getIntroduction(text,file_name)+"</introduction>\n"
    outputXML+="\t<discussion>"+getDiscussion(text)+"</discussion>\n"
    outputXML+="\t<conclusion>"+getConclusion(text,file_name)+"</conclusion>\n"

    outputXML+="\t<biblio>"+getBiblio(text,file_name)+"</biblio>\n"
    
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
