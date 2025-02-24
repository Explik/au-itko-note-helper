import uuid
from shared import combine_page_details, extract_plain_text, extract_rich_text, extract_screenshots, generate_data
import json
import os
import sys
import shutil

def process_file(pdf_file_path, working_dir, output_dir):
    pdf_file_name = os.path.basename(pdf_file_path)
    pdf_file_dir = os.path.dirname(pdf_file_path)
    print("Processing file: ", pdf_file_path)

    # Extract screenshots, plain text, and rich text from PDF
    os.makedirs(working_dir, exist_ok=True)

    screenshot_pages = extract_screenshots(pdf_file_path, working_dir, 'screenshots')
    print("Screenshots extracted")

    plain_text_pages = extract_plain_text(pdf_file_path, working_dir, 'text')
    print("Plain text extracted")

    rich_text_pages = extract_rich_text(pdf_file_path, working_dir, 'html')
    print("Rich text extracted")

    data = generate_data(pdf_file_path, screenshot_pages, rich_text_pages, plain_text_pages)
    print(data)
    with open(os.path.join(working_dir, "data.json"), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print("Data file created")
    
    # Zip the contents of the PDF directory
    os.makedirs(output_dir, exist_ok=True)

    zip_file_name_without_ext = f"{os.path.splitext(pdf_file_name)[0]}-pdf"
    shutil.make_archive(
        os.path.join(pdf_file_dir, zip_file_name_without_ext),
        'zip', 
        output_dir)

    print(f"Output directory zipped to {output_dir}")

def main(path, working_directory, output_directory): 
    if os.path.isdir(path):
        csv_files = [f for f in os.listdir(path) if f.endswith('.pdf')]
        if not csv_files:
            print('No PDF files found in the directory')
            sys.exit(1)
        for csv_file in csv_files:
            process_file(os.path.join(path, csv_file), working_directory, output_directory)
    else:
        if not os.path.isfile(path):
            print('The provided path is not a valid file or directory')
            sys.exit(1)
        process_file(path, working_directory, output_directory)

if __name__ == "__main__":
    # Get csv/directory path from arguments 
    file_path = None 
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else: 
        print('Please provide a path to a PDF file')
        sys.exit(1)

    # Check for optional arguments 
    # --working-directory [path]
    working_directory = os.path.join(".", "temporary", str(uuid.uuid4()))
    if '--working-directory' in sys.argv:
        working_directory = sys.argv.index('--working-directory') + 1
        if working_directory < len(sys.argv):
            working_directory = sys.argv[working_directory]

            if "--" in working_directory:
                print('Please provide a valid working directory path')
                sys.exit(1)
        else:
            print('Please provide a valid working directory path')
            sys.exit(1)

    # --output-directory [path]
    output_directory = os.path.dirname(file_path)
    if '--output-directory' in sys.argv:
        output_index = sys.argv.index('--output-directory') + 1
        if output_index < len(sys.argv):
            output_directory = sys.argv[output_index]

            if "--" in output_directory:
                print('Please provide a valid output directory path')
                sys.exit(1)
        else:
            print('Please provide a valid output directory path')
            sys.exit(1)

    main(file_path, working_directory, output_directory)