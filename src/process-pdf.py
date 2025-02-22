import uuid
from shared import combine_page_details, extract_plain_text, extract_rich_text, extract_screenshots, generate_data
import json
import os
import shutil

pdf_file_path = ".\\slides\\1-software-udvikling.pdf"
pdf_file_name = os.path.basename(pdf_file_path)
pdf_file_dir = os.path.dirname(pdf_file_path)

output_dir = os.path.join(".", "output", str(uuid.uuid4()))

# Extract screenshots, plain text, and rich text from PDF
screenshot_pages = extract_screenshots(pdf_file_path, output_dir, 'screenshots')
print("Screenshots extracted")

plain_text_pages = extract_plain_text(pdf_file_path, output_dir, 'text')
print("Plain text extracted")

rich_text_pages = extract_rich_text(pdf_file_path, output_dir, 'html')
print("Rich text extracted")

# Combine all extraction data into a single JSON file
data = generate_data(pdf_file_path, screenshot_pages, rich_text_pages, plain_text_pages)
print(data)

with open(os.path.join(output_dir, "data.json"), "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=4)
print("Data file created")

# Create the output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

# Zip the contents of the output directory
zip_file_name_without_ext = f"{os.path.splitext(pdf_file_name)[0]}-pdf"
shutil.make_archive(
    os.path.join(pdf_file_dir, zip_file_name_without_ext),
    'zip', 
    output_dir)

print(f"Output directory zipped to {output_dir}")
