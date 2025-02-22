import streamlit as st
import os
from PIL import Image
import base64
import json
import pyperclip
import win32clipboard
from io import BytesIO
from PIL import Image

def page_to_html(page, number_of_pages):
    image_path = page['screenshot-file']
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()

    return f"""<img src="data:image/png;base64,{encoded_string}" style="width:100%;"><p>Page {page['page_number']} / {number_of_pages}"""

def copy_image_to_clipboard(image_path):
    # WINDOWS ONLY
    image = Image.open(image_path)
    
    output = BytesIO()
    image.convert("RGB").save(output, "BMP")
    data = output.getvalue()[14:]
    output.close()

    win32clipboard.OpenClipboard()
    win32clipboard.EmptyClipboard()
    win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
    win32clipboard.CloseClipboard()

def copy_text_to_clipboard(text): 
    pyperclip.copy(text)

def copy_html_to_clipboard(html):
    pyperclip.copy(html)

def handle_copy_screenshot(): 
    current_page = get_current_page()
    image_path = current_page['screenshot-file']
    copy_image_to_clipboard(image_path)

def handle_copy_text_only(): 
    current_page = get_current_page()
    text_path = current_page['text-file']

    with open(text_path, 'r') as file:
        text = file.read()
        copy_text_to_clipboard(text)

def handle_copy_html():
    current_page = get_current_page()
    html_path = current_page['html-file']

    with open(html_path, 'r') as file:
        page_html = file.read()
        copy_html_to_clipboard(page_html)

# Load data 
page_details = None 
with open('./output/pages.json', 'r') as file:
    page_details = json.load(file)

pages = [page_to_html(page, len(page_details)) for page in page_details]

# Initialize session state for page index
if 'page_index' not in st.session_state:
    st.session_state.page_index = 0

# Function to navigate pages
def navigate(direction):
    if direction == 'next':
        st.session_state.page_index = (st.session_state.page_index + 1) % len(pages)
    elif direction == 'prev':
        st.session_state.page_index = (st.session_state.page_index - 1) % len(pages)

def get_current_page(): 
    return page_details[st.session_state.page_index]

# Display current page
main_col1, main_col2 = st.columns([3, 1])

with main_col1:
    st.markdown(f"<div style='border: 2px solid black; padding: 10px;'>{pages[st.session_state.page_index]}</div>", unsafe_allow_html=True)
    st.text("")

    # Navigation buttons
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button('⬅️ Previous', use_container_width=True):
            navigate('prev')
    with col3:
        if st.button('Next ➡️', use_container_width=True):
            navigate('next')

with main_col2:
    st.button("Copy screenshot", use_container_width=True, on_click=handle_copy_screenshot)
    st.button("Copy HTML", use_container_width=True, on_click=handle_copy_html)
    st.button("Copy text-only", use_container_width=True, on_click=handle_copy_text_only)