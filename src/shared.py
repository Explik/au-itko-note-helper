# import module
import json
from pdf2image import convert_from_path
from pypdf import PdfReader
from subprocess import Popen, PIPE, STDOUT
from bs4 import BeautifulSoup
import os

# Utility functions
def create_dir_if_not_exists(dir_path):
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

def delete_dir_if_exists(dir_path):
    assert dir_path not in ['/', '\\'], "Cannot delete root directory."
    
    if os.path.exists(dir_path):
        assert os.path.isdir(dir_path), f"{dir_path} is not a directory."

        for root, dirs, files in os.walk(dir_path):
            for file in files:
                os.remove(os.path.join(root, file))
            for dir in dirs:
                os.rmdir(os.path.join(root, dir))
        os.rmdir(dir_path)

def run_command(command):
    process = Popen(command, shell=True, stdout=PIPE, stderr=STDOUT)
    
    with process.stdout:
        for line in iter(process.stdout.readline, b''):
            print(line.decode("utf-8").strip())

    return process.wait()

# page_number is 0-based
def create_page_details(page_number, properties): 
    # Create page details object
    page_details = {
        "page_number": page_number + 1,
    }

    # Attach properties to object
    for key, value in properties.items():
        page_details[key] = value

    return page_details

def combine_page_details(*pages_list: list[list[dict]]): 
    buffer_map = { }

    # Combine pages from all lists
    for pages in pages_list:
        for page in pages:
            page_number = page["page_number"]
            if page_number in buffer_map:
                buffer_map[page_number].update(page)
            else:
                buffer_map[page_number] = page.copy()

    # Sort pages by page number
    buffer_list = list(buffer_map.values())
    buffer_list.sort(key=lambda x: x["page_number"])

    return buffer_list

def generate_data(file_path, *pages_list: list[list[dict]]): 
    combined_pages = combine_page_details(*pages_list)
    
    return {
        "file-name": os.path.basename(file_path),
        "directory_separator": os.path.sep,
        "pages": combined_pages
    }

def load_data_file(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        old_data = json.load(f)

    old_directory_separator = old_data.get("directory_separator")
    new_directory_separator = os.path.sep

    def replace_separators(obj):
        if isinstance(obj, dict):
            return {k: replace_separators(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [replace_separators(elem) for elem in obj]
        elif isinstance(obj, str):
            return obj.replace(old_directory_separator, new_directory_separator)
        else:
            return obj

    return replace_separators(old_data)

# PDF extraction functions
def extract_screenshots(pdf_file_path, output_dir): 
    # Store Pdf with convert_from_path function
    images = convert_from_path(pdf_file_path)

    # Create directory if it doesn't exist
    create_dir_if_not_exists(output_dir)

    # Save PDF pages as images in output directory
    buffer = []
    for i in range(len(images)):
        image_file_name = os.path.join(output_dir, 'page_'+ str(i) +'.jpg')
        images[i].save(image_file_name, 'JPEG')

        page_details = create_page_details(i, { "screenshot-file": image_file_name })
        buffer.append(page_details)

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
        
        page_details = create_page_details(i, { "text-file": file_path })
        buffer.append(page_details)
    
    return buffer

def extract_rich_text(pdf_file_path, output_dir): 
    html_file_name = generate_single_html_file(pdf_file_path, output_dir)
    html_file_names = split_single_html_file(html_file_name, os.path.join(output_dir, 'html'))
    
    return html_file_names

def generate_single_html_file(pdf_file_path: str, output_dir: str):
    if (pdf_file_path.endswith(".pdf") == False):
        raise ValueError("The file must be a PDF file.")

    # Create output directory if it doesn't exist
    create_dir_if_not_exists(output_dir)

    # Run conversion command
    command_status = run_command([
        "marker_single",
        pdf_file_path,
        "--output_format", "html",
        "--output_dir", output_dir,
        "--paginate_output"
    ])

    if command_status != 0:
        raise ValueError("An error occurred while converting the PDF to HTML.", command_status)

    # Rename output folder to "html" instead of file name without extension (overwrite any existing folder)
    file_name_without_ext = os.path.splitext(os.path.basename(pdf_file_path))[0]
    html_folder_path = os.path.join(output_dir, file_name_without_ext)
    new_html_folder_path = os.path.join(output_dir, "html")
    
    delete_dir_if_exists(new_html_folder_path)

    os.rename(html_folder_path, new_html_folder_path)

    # Return HTML file path
    return os.path.join(new_html_folder_path, file_name_without_ext + ".html")

def split_single_html_file(html_file_path: str, output_dir: str):
    if (os.path.exists(html_file_path) == False):
        raise ValueError("The HTML file does not exist.")
    
    # Read HTML file
    with open(html_file_path, "r", encoding="utf-8") as file:
        html_content = file.read()

    # Split HTML content into pages
    soup = BeautifulSoup(html_content, "html.parser")
    pages = soup.find_all(class_="page")

    buffer = []
    for page in pages:
        page_id = page.get("data-page-id")
        if page_id:
            # Create new HTML file
            output_html_file_path = os.path.join(output_dir, f"page_{page_id}.html")
            with open(output_html_file_path, "w", encoding="utf-8") as output_file:
                for child in page.children:
                    output_file.write(str(child))

            # Create new text file
            output_text_file_path = os.path.join(output_dir, f"page_{page_id}.txt")
            with open(output_text_file_path, "w", encoding="utf-8") as output_file:
                page_text = page.get_text().replace("  ", " ").strip()
                output_file.write(page_text)

            # Find images 
            image_file_paths = []
            for img in page.find_all("img"):
                img_src = img.get("src")
                if img_src:
                    image_file_path = os.path.join(output_dir, img_src)
                    image_file_paths.append(image_file_path)

            # Find first heading 
            first_heading = None
            for level in range(1, 7):
                heading_tag = page.find(f"h{level}")
                if heading_tag:
                    first_heading = heading_tag.get_text().strip()
                    break

            # Create page details 
            page_details = create_page_details(int(page_id), { 
                "html-file": output_html_file_path, 
                "text-file": output_text_file_path,
                "image-files": image_file_paths,
                "first-heading": first_heading
            })
            buffer.append(page_details)

    return buffer