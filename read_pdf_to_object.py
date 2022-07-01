from PyPDF2 import PdfReader

reader = PdfReader(r"data\Reuters_PolNews_France.pdf")
number_of_pages = len(reader.pages)
page = reader.pages[2]
text = page.extract_text()

print(text)

