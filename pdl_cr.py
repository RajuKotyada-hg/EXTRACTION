from paddleocr import PaddleOCR, draw_ocr
from pdf2image import convert_from_path
import matplotlib.pyplot as plt
from PIL import Image
import os

# Initialize PaddleOCR
ocr = PaddleOCR(use_angle_cls=True, lang='en')  # Use English model

# Path to the PDF file
pdf_path = 'D:\\OLD APPS\\Test\\Repository\\Pending\\Autoclerk\\Feb\\23\\tranSummary_2024-02-23.pdf'

# Check if PDF file exists
if not os.path.exists(pdf_path):
    raise FileNotFoundError(f"The PDF file at {pdf_path} was not found.")

try:
    # Convert PDF to images
    pages = convert_from_path(pdf_path, 300)  # 300 dpi resolution
except Exception as e:
    raise RuntimeError(f"Failed to convert PDF to images: {e}")

# Process each page
for page_number, page_image in enumerate(pages):
    try:
        # Convert PIL image to RGB
        image = page_image.convert('RGB')
        
        # Perform OCR on the image
        result = ocr.ocr(image, cls=True)

        # Print the extracted text
        print(f"Text from page {page_number + 1}:")
        for line in result:
            print(line)

        # Optionally, visualize the results
        boxes = [elements[0] for elements in result[0]]
        txts = [elements[1][0] for elements in result[0]]
        scores = [elements[1][1] for elements in result[0]]
        im_show = draw_ocr(image, boxes, txts, scores, font_path='path_to_your_font.ttf')
        im_show = Image.fromarray(im_show)

        # Display the image with OCR results
        plt.figure(figsize=(10, 10))
        plt.imshow(im_show)
        plt.title(f'Page {page_number + 1}')
        plt.axis('off')
        plt.show()

    except AssertionError as e:
        print(f"AssertionError on page {page_number + 1}: {e}")
    except Exception as e:
        print(f"Error on page {page_number + 1}: {e}")


# from paddleocr import PaddleOCR, draw_ocr
# from pdf2image import convert_from_path
# import matplotlib.pyplot as plt
# from PIL import Image

# # Initialize PaddleOCR
# ocr = PaddleOCR(use_angle_cls=True, lang='en')  # Use English model

# # Path to the PDF file
# pdf_path = "D:\\OLD APPS\\Test\\Repository\\Pending\\Autoclerk\\Feb\\23\\tranSummary_2024-02-23.pdf"

# # Convert PDF to images
# pages = convert_from_path(pdf_path, 300)  # 300 dpi resolution

# # Process each page
# for page_number, page_image in enumerate(pages):
#     # Convert PIL image to RGB
#     image = page_image.convert('RGB')

#     # Perform OCR on the image
#     result = ocr.ocr(image, cls=True)

#     # Print the extracted text
#     print(f"Text from page {page_number + 1}:")
#     for line in result:
#         print(line)

#     # Optionally, visualize the results
#     boxes = [elements[0] for elements in result[0]]
#     txts = [elements[1][0] for elements in result[0]]
#     scores = [elements[1][1] for elements in result[0]]
#     im_show = draw_ocr(image, boxes, txts, scores, font_path='path_to_your_font.ttf')
#     im_show = Image.fromarray(im_show)

#     # Display the image with OCR results
#     plt.figure(figsize=(10, 10))
#     plt.imshow(im_show)
#     plt.title(f'Page {page_number + 1}')
#     plt.axis('off')
#     plt.show()
