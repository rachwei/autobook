import cv2 
import pytesseract
import os
from io import BytesIO
from PIL import Image
from pdf2image import convert_from_bytes

pytesseract.pytesseract.tesseract_cmd = r'/opt/homebrew/bin/tesseract'


def getText(media):
    # make this process better: https://aurigait.com/blog/how-to-increase-accuracy-of-tesseract/
    output = ""
    print("In the get text functions")

    for file in media:
        # image_data = images.read()
        # format = images.filename.rsplit('.', 1)[-1].lower()
        # img_io = BytesIO(image_data) # simulate a file
        # img = Image.open(img_io, "PDF")

        # # Adding custom options
        custom_config = r'--oem 3 --psm 6'
        # output += pytesseract.image_to_string(img, config=custom_config)
        content_type = file.content_type

        if content_type == 'application/pdf':
            img_io = BytesIO(file.read())
            images = convert_from_bytes(img_io.read())

            # Process each page as a separate image
            for page_image in images:
                extracted_text = pytesseract.image_to_string(page_image, config=custom_config)
                output += extracted_text + "\n"
        else:
            # If not a PDF, directly read and process the file
            img_io = BytesIO(file.read())
            img = Image.open(img_io)
            extracted_text = pytesseract.image_to_string(img, config=custom_config)
            output += extracted_text + "\n"

    return output


# get text using tesseract from folder path
# def getText(folder_path):
#     # make this process better: https://aurigait.com/blog/how-to-increase-accuracy-of-tesseract/
#     output = ""

#     for images in os.listdir(folder_path):
#         img = Image.open(folder_path + images)

#         # Adding custom options
#         custom_config = r'--oem 3 --psm 6'
#         output = pytesseract.image_to_string(img, config=custom_config)

#     return output