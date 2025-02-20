import os
from pypdf import PdfReader

input_file = "slides\\1-software-udvikling.pdf"
output_folder = "output\\text\\"

# Create output folder if it doesn't exist
os.makedirs(output_folder, exist_ok=True)

pdf_reader = PdfReader(input_file)

for i, page in enumerate(pdf_reader.pages, start=1):
    text = page.extract_text()
    
    with open(os.path.join(output_folder, f"page_{i}.txt"), "w", encoding="utf-8") as f:
        f.write(text)