import streamlit as st
import base64
import json
import re
from pathlib import Path

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
    return "".join([image_file_to_html(image_path) for image_path in image_paths])

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

def create_copy_button(text, html_content):
    with open('./src/copy-button.html', 'r') as file:
        copy_button_html = file.read()
    
    return copy_button_html \
        .replace("BUTTON_TEXT", text) \
        .replace("HTML_CONTENT", json.dumps(html_content))

def create_copy_text_button(text): 
    text_path = get_current_page()['text-file']
    content = text_file_to_html(text_path)

    return create_copy_button(text, content)

def create_copy_images_button(text):
    image_paths = get_current_page()['image-files']
    image_html = image_files_to_html(image_paths)

    return create_copy_button(text, image_html)

def create_copy_screenshot_button(text): 
    image_path = get_current_page()['screenshot-file']
    image_html = image_file_to_html(image_path)

    return create_copy_button(text, image_html)

def create_copy_html_button_source(text): 
    html_path = get_current_page()['html-file']
    html_content = html_file_to_html(html_path)

    return create_copy_button(text, html_content)

# Load data 
page_details = None 
with open('./output/pages.json', 'r') as file:
    page_details = json.load(file)

# Initialize session state for page index
if 'page_index' not in st.session_state:
    st.session_state.page_index = 0

# State functions

# SessionState 
# - page_index: index of the current page
# - mode: current mode (screenshot, text, images, html)
def set_mode(mode): 
    st.session_state.mode = mode

def get_mode(): 
    if 'mode' not in st.session_state: 
        st.session_state.mode = "screenshot"

    return st.session_state.mode

def get_current_index():
    return st.session_state.page_index

def set_current_index(index):
    if index < 0 or index >= get_number_of_pages():
        return

    st.session_state.page_index = index

def use_default_view():
    return st.session_state.default_view

# Derivative state functions
def get_current_page(): 
    return page_details[st.session_state.page_index]

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

# Display current page
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

    st.checkbox("Default view", True, key="default_view")
    
with main_col3: 
    st.button("View", key="view_image", disabled=get_mode() == "screenshot", on_click=lambda: set_mode("screenshot"))
    st.button("View", key="view_html", disabled=get_mode() == "html", on_click=lambda: set_mode("html"))
    st.button("View", key="view_text", disabled=get_mode() == "text", on_click=lambda: set_mode("text"))
    st.button("View", key="view_images", disabled=get_mode() == "images", on_click=lambda: set_mode("images"))