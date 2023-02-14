import re
import os
from PyPDF2 import PdfReader

def extract_pdf_info(file_path):
    """
    Extracts the name of the file, the title of the paper, the authors, and the abstract
    from a PDF file using regular expressions.
    """
    with open(file_path, "rb") as f:
        # Read the PDF file with PyPDF2's PdfReader
        pdf = PdfReader(f)
        text = ""
        for page_num in range(len(pdf.pages)):
            page = pdf.pages[page_num]
            text += page.extract_text()

        # Use regular expressions to extract the title, authors, and abstract
        title_regex = re.compile(r"Title:\s*(.*)")
        authors_regex = re.compile(r"Author\(s\):\s*(.*)")
        abstract_regex = re.compile(r"Abstract((?:.|\n)*?)\n[1-9I]\.?\s+(?:INTRODUCTION|Introduction)")
        title_match = re.search(title_regex, text)
        title = title_match.group(1).strip() if title_match else ""
        authors_match = re.search(authors_regex, text)
        authors = authors_match.group(1).strip() if authors_match else ""
        abstract_match = re.findall(abstract_regex, text)
        abstract = abstract_match.pop() if abstract_match else ""

    return (os.path.basename(file_path), title, authors, abstract,text)

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

directory = '../Corpus_2022/Corpus_2021/'
results = extract_pdf_info_from_directory(directory)

for i in range(len(results)):
    #print("text :"+results[i][4])
    print("Nom du fichier :",results[i][0],"\nLe titre de l'article :", results[i][1],"\nLes auteurs :", results[i][2],"\nLe résumé :", results[i][3],end="\n----------------------------------\n")
