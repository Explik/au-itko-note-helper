from subprocess import Popen, PIPE, STDOUT
import os
from bs4 import BeautifulSoup

def generate_html(file_path: str, output_dir: str):
    if (file_path.endswith(".pdf") == False):
        raise ValueError("The file must be a PDF file.")

    # Run conversion command
    command = [
        "marker_single",
        file_path,
        "--output_format", "html",
        "--output_dir", output_dir,
        "--paginate_output"
    ]
    
    process = Popen(command, shell=True, stdout=PIPE, stderr=STDOUT)
    
    with process.stdout:
        for line in iter(process.stdout.readline, b''):
            print(line.decode("utf-8").strip())

    result = process.wait()
    
    if result != 0:
        print("An error occurred while converting the PDF to HTML.")

def segment_html(file_path: str, output_dir: str):
    # Find generated HTML file
    file_name_without_ext = os.path.splitext(os.path.basename(file_path))[0]

    html_folder_path = os.path.join(output_dir, file_name_without_ext)
    html_file_path = os.path.join(html_folder_path, file_name_without_ext + ".html")
    if (os.path.exists(html_file_path) == False):
        raise ValueError("The HTML file does not exist.")
    
    # Read HTML file
    with open(html_file_path, "r", encoding="utf-8") as file:
        html_content = file.read()

    # Split HTML content into pages
    soup = BeautifulSoup(html_content, "html.parser")
    pages = soup.find_all(class_="page")

    for page in pages:
        page_id = page.get("data-page-id")
        if page_id:

            # Create new HTML file
            output_html_file_path = os.path.join(html_folder_path, f"page_{page_id}.html")
            with open(output_html_file_path, "w", encoding="utf-8") as output_file:
                for child in page.children:
                    output_file.write(str(child))

            output_text_file_path = os.path.join(html_folder_path, f"page_{page_id}.txt")
            with open(output_text_file_path, "w", encoding="utf-8") as output_file:
                page_text = page.get_text().replace("  ", " ").strip()
                output_file.write(page_text)

def rename_output_folder(file_path: str, output_dir: str):
    # Find generated HTML file
    file_name_without_ext = os.path.splitext(os.path.basename(file_path))[0]

    html_folder_path = os.path.join(output_dir, file_name_without_ext)
    if (os.path.exists(html_folder_path) == False):
        raise ValueError("The HTML folder does not exist.")
    
    # Rename output folder
    new_html_folder_path = os.path.join(output_dir, "html")
    os.rename(html_folder_path, new_html_folder_path)

if __name__ == "__main__":
    file_path = ".\\slides\\1-software-udvikling.pdf"
    output_dir = ".\\output"

    generate_html(file_path, output_dir)
    segment_html(file_path, output_dir)
    rename_output_folder(file_path, output_dir)
    