import re
import os
import sys
from PyPDF2 import PdfReader

def getTitle(metadata,text):
    if(metadata.title!="" and metadata.title!="None"):
        title = metadata.title
    else:
        # Use regular expressions to extract the title
        title_regex = re.compile(r"Title:\s*(.*)")
        title_match = re.search(title_regex, text)
        title = title_match.group(1).strip() if title_match else ""
    
    return title

def getAuthors(metadata,text):
    if(metadata.author!="" and metadata.author!="None"):
        authors = metadata.author
    else:
        # Use regular expressions to extract the author
        authors_regex = re.compile(r"Author\(s\):\s*(.*)")
        authors_match = re.search(authors_regex, text)
        authors = authors_match.group(1).strip() if authors_match else ""
    
    return authors

def getAbstract(pdf):

    text = pdf.pages[0].extract_text()

    abstract_regex = re.compile(r"(Abstract ?.?\.? ?)|(In this article|This article presents)((?:.|\n)*?)\n[1-9I]\.?\s+") # Abstract\.? ?((?:.|\n)*?)\n[1-9A-Z]\.?\s+(?:INTRODUCTION|Introduction)
    abstract_match = re.findall(abstract_regex, text)
    abstract = abstract_match.pop() if abstract_match else ""
    finalAbstract=""
    for i in abstract:
        finalAbstract+=i
    return finalAbstract.replace('-\n','')

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
            text += page.extract_text()
    return (text,metadata,pdf)

def writeTxt(file_name,output_file_name,text,metadata,pdf):
    """
    Writes all the capital information in a .txt file
    """
    outputString = "Nom du fichier : "+file_name+"\n"
    outputString+="Titre de l'article : "+getTitle(metadata,text)+"\n"
    outputString+="Auteurs : "+"\n"
    print(getAbstract(pdf))
    #outputString+="Résumé de l'article :\n"+getAbstract(pdf)+"\n"
    outputString+="Bibliographie : "
    if(output_file_name!=""):
        fd = os.open(output_file_name,flags=os.O_RDWR)
        text = str.encode(outputString)
        lgText = os.write(fd,text)
        if(lgText==0):
            sys.stderr("Aucune données n'a pu être extraite")
        os.close(fd)
    return outputString
def writeXML(file_name,output_file_name,text,metadata,pdf):
    """
    Writes all the capital information in a .xml file with an XML layout
    """


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

    parser = argparse.ArgumentParser(description="Parseur d'articles scientifiques")
    parser.add_argument('-t',action='store_true',help='To be set if the output should be saved in a .txt')
    parser.add_argument('-x',action='store_true',help='To be set if the output should be saved in a .xml')
    parser.add_argument('filename',help='The path to the file that needs to be converted')
    parser.add_argument('--out',help='Optionnal path to the directory where the output should be saved')
    args = parser.parse_args()
    launchExtraction(args)
