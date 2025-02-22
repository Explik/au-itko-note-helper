from shared import combine_page_details, extract_plain_text, extract_rich_text, extract_screenshots, generate_data
import json
import os

pdf_file_path = ".\\slides\\1-software-udvikling.pdf"
pdf_file_name = os.path.basename(pdf_file_path)

# Extract screenshots, plain text, and rich text from PDF
screenshot_pages = extract_screenshots(pdf_file_path, '.\\output\\screenshots')
print("Screenshots extracted")

plain_text_pages = extract_plain_text(pdf_file_path, ".\\output\\text")
print("Plain text extracted")

rich_text_pages = extract_rich_text(pdf_file_path, ".\\output")
print("Rich text extracted")

# Combine all extraction data into a single JSON file
data = generate_data(pdf_file_path, screenshot_pages, rich_text_pages, plain_text_pages)
print(data)

with open(".\\output\\data.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=4)
print("Data file created")