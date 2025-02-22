import os
import uuid
import streamlit as st
import base64
import json
import re
from pathlib import Path

from shared import create_dir_if_not_exists, extract_plain_text, extract_rich_text, extract_screenshots, generate_data
import time
import zipfile

st.set_page_config(layout="wide")

def text_file_to_html(text_path):
    with open(text_path, "r", encoding="utf-8") as text_file:
        content = text_file.read()

    return f"""<p> {content} </p> """

def image_file_to_html(image_path):
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()

    return f"""<img src="data:image/png;base64,{encoded_string}" style="width:100%;">"""

def image_files_to_html(image_paths):
    html = "".join([image_file_to_html(image_path) for image_path in image_paths])
    return html.replace('style="width:100%;"', 'style="display: block; margin-bottom: 10px;"')

def html_file_to_html(html_path):
    with open(html_path, "r", encoding="utf-8") as html_file:
        html_content = html_file.read()

    def replace_img_tags(html_content, html_path):
        folder = Path(html_path).parent
        img_tags = re.findall(r'<img src="([^"]+)"', html_content)
        for img_tag in img_tags:
            img_path = folder / img_tag
            if img_path.exists():
                with open(img_path, "rb") as img_file:
                    encoded_string = base64.b64encode(img_file.read()).decode()
                inline_img_tag = f'<img src="data:image/jpeg;base64,{encoded_string}"">'
                html_content = html_content.replace(f'<img src="{img_tag}"/>', inline_img_tag)
        return html_content

    html_content = replace_img_tags(html_content, html_path)

    return html_content

def create_copy_button(text, html_content, text_content = ""):
    with open('./src/copy-button.html', 'r') as file:
        copy_button_html = file.read()
    
    return copy_button_html \
        .replace("BUTTON_TEXT", text) \
        .replace("HTML_CONTENT", json.dumps(html_content)) \
        .replace("TEXT_CONTENT", json.dumps(text_content))

def create_copy_text_button(text): 
    text_path = get_current_page()['text-file']
    html_content = text_file_to_html(text_path)
    txt_content = html_content.replace("<p>", "").replace("</p>", "").strip()

    return create_copy_button(text, html_content, txt_content)

def create_copy_images_button(text):
    image_paths = get_current_page()['image-files']
    image_html = image_files_to_html(image_paths)

    return create_copy_button(text, image_html)

def create_copy_screenshot_button(text): 
    image_path = get_current_page()['screenshot-file']
    image_html = image_file_to_html(image_path)

    if get_add_heading():
        heading = get_current_page()['first-heading']

        if heading is not None:
            image_html = f"<h1>{heading}</h1>" + image_html

    return create_copy_button(text, image_html)

def create_copy_html_button_source(text): 
    html_path = get_current_page()['html-file']
    html_content = html_file_to_html(html_path)

    return create_copy_button(text, html_content)

def start_processing_pdf_file(pdf_file_path):
    pdf_file_name = os.path.basename(pdf_file_path)

    output_dir = os.path.join(".\\output", str(uuid.uuid4()))
    create_dir_if_not_exists(output_dir)

    st.markdown("### Processing file...")
    progress_bar = st.progress(0)

    # Extract screenshots, plain text, and rich text from PDF
    st.markdown("#### Extracting screenshots...")
    screenshot_pages = extract_screenshots(pdf_file_path, os.path.join(output_dir, 'screenshots'))
    progress_bar.progress(0.3)

    st.markdown("#### Extracting text...")
    plain_text_pages = extract_plain_text(pdf_file_path, os.path.join(output_dir, "text"))
    progress_bar.progress(0.4)

    st.markdown("#### Extracting layout, image, texts...")
    rich_text_pages = extract_rich_text(pdf_file_path, output_dir)
    progress_bar.progress(0.9)

    # Combine all extraction metadata into a single JSON file
    st.markdown("#### Finalizing...")
    data = generate_data(pdf_file_name, screenshot_pages, rich_text_pages, plain_text_pages)
    with open(os.path.join(output_dir, "data.json"), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    progress_bar.progress(1.0)

    set_working_dir(output_dir)
    st.rerun()

def list_items_recursively(directory, max_items=5, level=0):
    items = os.listdir(directory)
    for i, item in enumerate(items):
        if i >= max_items:
            print("  " * level + "...")
            break
        item_path = os.path.join(directory, item)
        print("  " * level + f"- {item}")
        if os.path.isdir(item_path):
            list_items_recursively(item_path, max_items, level + 1)

def start_processing_zip_file(zip_file_path):
    output_dir = os.path.join(".\\output", str(uuid.uuid4()))
    create_dir_if_not_exists(output_dir)

    print(f"Extracting {zip_file_path} to {output_dir}")
    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        zip_ref.extractall(output_dir)

    print("Extracted items: ")
    list_items_recursively(output_dir)

    set_working_dir(output_dir)
    st.rerun()

def start_processing_any_file(file_path):
    if file_path.endswith('.pdf'):
        start_processing_pdf_file(file_path)
    elif file_path.endswith('.zip'):
        start_processing_zip_file(file_path)
    
    raise ValueError("Invalid file type")

def download_working_dir_as_zip():
    working_dir = get_working_dir()
    zip_file_name = os.path.basename(working_dir) + ".zip"

    with zipfile.ZipFile(zip_file_name, 'w') as zip_ref:
        for root, dirs, files in os.walk(working_dir):
            for file in files:
                zip_ref.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), working_dir))

    with open(zip_file_name, 'rb') as file:
        return file.read()
        
# SessionState 
# - page_index: index of the current page
# - mode: current mode (screenshot, text, images, html)
def set_working_dir(dir):
    st.session_state.working_dir = dir

def get_working_dir():
    if 'working_dir' not in st.session_state:
        st.session_state.working_dir = None

    return st.session_state.working_dir

def set_mode(mode): 
    st.session_state.mode = mode

def get_mode(): 
    if 'mode' not in st.session_state: 
        st.session_state.mode = "screenshot"

    return st.session_state.mode

def get_current_index():
    if 'page_index' not in st.session_state:
        st.session_state.page_index = 0

    return st.session_state.page_index

def set_current_index(index):
    if index < 0 or index >= get_number_of_pages():
        return

    st.session_state.page_index = index

def use_default_view():
    return st.session_state.use_default_view

def get_add_heading():
    if 'add_heading' not in st.session_state: 
        st.session_state.add_heading = False

    return st.session_state.add_heading

# Load data 
file_name = ""
page_details = []

working_dir = get_working_dir()

if working_dir is not None:
    data_path = os.path.join(working_dir, 'data.json')

    with open(data_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

        file_name = data['file-name']
        page_details = data['pages']

def get_current_page(): 
    current_index = get_current_index()
    return page_details[current_index]

def get_current_page_html():
    mode = get_mode()

    if mode == "screenshot":
        return image_file_to_html(get_current_page()['screenshot-file'])
    if mode == "text":
        return text_file_to_html(get_current_page()['text-file'])
    if mode == "html":
        return html_file_to_html(get_current_page()['html-file'])
    if mode == "images":
        return image_files_to_html(get_current_page()['image-files'])

    return "Error, invalid mode"

def get_number_of_pages():
    return len(page_details)

def navigate(direction):
    index = get_current_index() 
    max_index = get_number_of_pages()

    if direction == 'next':
        set_current_index((index + 1) % max_index)
    elif direction == 'prev':
        set_current_index((index - 1) % max_index)

    if use_default_view():
        set_mode("screenshot")

def handle_page_input_change():
    page_input = st.session_state.page_input
    if not page_input:
        return

    page_number = page_input.split(' / ')[0].strip()
    if not page_number.isdigit():
        return
    
    set_current_index(int(page_number) - 1)

# Display landing page 
if working_dir is None:
    st.markdown("# 📝 Note Helper")
    st.markdown("Upload a PDF file to get started.")

    uploaded_file = st.file_uploader("Choose a file", type=["pdf", "zip"])

    if uploaded_file is not None:
        upload_dir = "uploads"

        create_dir_if_not_exists(upload_dir)
        file_path = os.path.join(upload_dir, uploaded_file.name)
    
        with open(file_path, 'wb') as out_file:
            bytes_data = uploaded_file.read()
            out_file.write(bytes_data)
        
        if st.button("Convert and Process"):
            start_processing_any_file(file_path)

# Display PDF page
else: 
    # Header
    header_col1, header_col2 = st.columns([3, 1], vertical_alignment="bottom")
    
    with header_col1:
        st.markdown("# " + file_name)
        
    
    with header_col2:
        st.download_button("Download as ZIP", data=download_working_dir_as_zip(), file_name=file_name.replace(".pdf", "-pdf") + ".zip", mime="application/zip")

    # Padding between header and main content
    st.text("")

    # Main content
    main_col1, main_col2, main_col3 = st.columns([3, 1, 1])
    with main_col1:
        st.markdown(f"<div style='border: 2px solid black; padding: 10px; height: 500px; overflow-y: scroll'>{get_current_page_html()}</div>", unsafe_allow_html=True)
        st.text("")

        # Navigation buttons
        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            st.button('⬅️', use_container_width=True, on_click=lambda: navigate('prev'))

        with col2:
            st.text_input(
                "Page number", 
                f"{get_current_index() + 1} / {get_number_of_pages()}", 
                key="page_input", 
                label_visibility="collapsed",
                on_change=handle_page_input_change)
        
        with col3:
            st.button('➡️', use_container_width=True, on_click=lambda: navigate('next'))

    with main_col2:
        st.components.v1.html(create_copy_screenshot_button("Copy screenshot"), height=32)
        st.components.v1.html(create_copy_html_button_source("Copy text/images"), height=32)
        st.components.v1.html(create_copy_text_button("Copy text-only"), height=32)
        st.components.v1.html(create_copy_images_button("Copy images-only"), height=32)

        st.checkbox("Use default view (screenshot)", True, key="use_default_view")
        st.checkbox("Add heading to screenshot", False, key="add_heading")

    with main_col3: 
        st.button("View", key="view_image", disabled=get_mode() == "screenshot", on_click=lambda: set_mode("screenshot"))
        st.button("View", key="view_html", disabled=get_mode() == "html", on_click=lambda: set_mode("html"))
        st.button("View", key="view_text", disabled=get_mode() == "text", on_click=lambda: set_mode("text"))
        st.button("View", key="view_images", disabled=get_mode() == "images", on_click=lambda: set_mode("images"))