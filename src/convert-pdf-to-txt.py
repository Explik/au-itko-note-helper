from shared import extract_plain_text

input_file = "slides\\1-software-udvikling.pdf"
output_folder = "output\\text\\"

pages = extract_plain_text(input_file, output_folder)

print(pages)