from pdf2image import convert_from_path
from PIL import Image
import re
import pytesseract
from dateutil import parser
# Set the tesseract executable path (adjust this path as per your installation)
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Path to the PDF file
pdf_path = 'D:\OLD APPS\Test\Repository\PMS reports.1\Mews - WHM\\April 24\\April 24\\040124.pdf'

# Convert PDF to images
pages = convert_from_path(pdf_path, 300)
datePosition = 0

# Extract text from each page
extracted_text = ""
for page in pages:
    text = pytesseract.image_to_string(page)
    extracted_text += text + "\n"
    pattern =r'\d{2}[A-Za-z]{3}\d{2}|\b(?:\d{1,2}[-/]\d{1,2}[-/]\d{2,4}|[A-Za-z]{3,}\s\d{1,2},?\s\d{2,4}|\d{1,2}\s[A-Za-z]{3,}\s\d{4}|[A-Za-z]{3,}\d{2}\d{2})\b|\d{1,2}-[A-Za-z]{3}-\d{4}|\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) \d{1,2}/\d{2}\b'
    date_pattern = re.compile(pattern)
    date_match = date_pattern.findall(extracted_text)
    
# print(date_match)
date_string = date_match[datePosition]
date_obj = parser.parse(date_string)
formatted_date:str = date_obj.strftime('%Y-%m-%d')
date = formatted_date
# Print the extracted text
print(date)
