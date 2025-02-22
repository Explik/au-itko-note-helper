

from shared import extract_rich_text

file_path = ".\\slides\\1-software-udvikling.pdf"
output_dir = ".\\output"

pages = extract_rich_text(file_path, output_dir)
print(pages)