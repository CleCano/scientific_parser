from pdfminer.high_level import extract_text

text = extract_text("example.pdf")
print(text)
