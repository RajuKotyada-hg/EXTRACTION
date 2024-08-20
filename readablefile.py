# import pytesseract
# from pdf2image import convert_from_path
# from reportlab.lib.pagesizes import letter
# from reportlab.pdfgen import canvas

# # Path to the Tesseract OCR executable
# # pytesseract.pytesseract.tesseract_cmd = r'/usr/bin/tesseract'  # Update with your path to tesseract

# def ocr_image_pdf_to_readable_pdf(input_pdf, output_pdf):
#     try:
#         # Convert PDF pages to images
#         images = convert_from_path(input_pdf)

#         # Create a new PDF
#         c = canvas.Canvas(output_pdf, pagesize=letter)
#         width, height = letter

#         for img in images:
#             # Perform OCR on the image
#             text = pytesseract.image_to_string(img)
#             # print(text)

#             # Add text to the PDF
#             text_lines = text.splitlines()
#             y = height - 40  # Starting y position
#             for line in text_lines:
#                 c.drawString(40, y, line)
#                 y -= 14  # Move to the next line

#             # Add a new page for each image
#             c.showPage()
#         print(c)
#         c.save()

#         print(f"Conversion successful! Readable PDF file saved as {output_pdf}")

#     except Exception as e:
#         print(f"An error occurred: {e}")

# # Example usage
# ocr_image_pdf_to_readable_pdf('D:\\OLD APPS\\Test\\Repository\\ALLPMS\\19. Checkin\\Daily Status Report.pdf', 'readable_file.txt')


from reportlab.pdfgen import canvas
import fitz  # PyMuPDF

# Step 1: Create the PDF
file_path = "D:\\OLD APPS\\Test\\Repository\\ALLPMS\\19. Checkin\\Daily Status Report.pdf"
c = canvas.Canvas(file_path)
c.drawString(100, 750, "Hello, this is a test PDF.")
c.drawString(100, 730, "Here is some more text.")
c.save()

# Step 2: Extract Text from the PDF
def extract_text_from_pdf(file_path):
    pdf_document = fitz.open(file_path)
    text = ""

    for page_num in range(pdf_document.page_count):
        page = pdf_document.load_page(page_num)
        text += page.get_text()

    return text

# Extract and print the text
extracted_text = extract_text_from_pdf(file_path)
print(extracted_text)


# from reportlab.pdfgen import canvas
# import os
# import fitz  # PyMuPDF

# # Step 1: Create the PDF
# directory = "static"
# if not os.path.exists(directory):
#     os.makedirs(directory)

# file_path = os.path.join(directory, "example.pdf")
# c = canvas.Canvas(file_path)
# c.drawString(100, 750, "Hello, this is a test PDF.")
# c.drawString(100, 730, "Here is some more text.")
# c.save()

# # Step 2: Extract Text from the PDF
# def extract_text_from_pdf(file_path):
#     pdf_document = fitz.open(file_path)
#     text = ""

#     for page_num in range(pdf_document.page_count):
#         page = pdf_document.load_page(page_num)
#         text += page.get_text()

#     return text

# # Extract and print the text
# extracted_text = extract_text_from_pdf(file_path)
# print(extracted_text)
