# import module
from pdf2image import convert_from_path
from pypdf import PdfReader
import os

def create_dir_if_not_exists(dir_path):
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

def extract_screenshots(pdf_file_path, output_dir): 
    # Store Pdf with convert_from_path function
    images = convert_from_path(pdf_file_path)

    # Create directory if it doesn't exist
    create_dir_if_not_exists(output_dir)

    # Save PDF pages as images in output directory
    buffer = []
    for i in range(len(images)):
        image_file_name = output_dir + '/page_'+ str(i) +'.jpg'
        images[i].save(image_file_name, 'JPEG')

        buffer.append(image_file_name)
    
    return buffer

def extract_plain_text(pdf_file_path, output_dir): 
    # Initialize PdfReader
    pdf_reader = PdfReader(pdf_file_path)

    # Create output folder if it doesn't exist
    create_dir_if_not_exists(output_dir)

    # Save PDF pages as text files in output directory
    buffer = []
    for i, page in enumerate(pdf_reader.pages, start=0):
        file_path = os.path.join(output_dir, f"page_{i}.txt")
        file_content = page.extract_text()
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(file_content)
        
        buffer.append(file_path)
    
    return buffer


