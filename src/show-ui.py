import streamlit as st
import base64
import json

def page_to_html(page, number_of_pages):
    image_path = page['screenshot-file']
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()

    return f"""<img src="data:image/png;base64,{encoded_string}" style="width:100%;"><p>Page {page['page_number']} / {number_of_pages}"""

def image_to_html(image_path):
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()

    return f"""<img src="data:image/png;base64,{encoded_string}" style="width:100%;">"""

def create_copy_button(text, html_content):
    with open('./src/copy-button.html', 'r') as file:
        copy_button_html = file.read()
    
    return copy_button_html \
        .replace("BUTTON_TEXT", text) \
        .replace("HTML_CONTENT", json.dumps(html_content))

def create_copy_text_button(text): 
    text_path = get_current_page()['text-file']
    with open(text_path, "r", encoding="utf-8") as text_file:
        content = text_file.read()

    return create_copy_button(text, content)

def create_copy_image_button(text): 
    image_path = get_current_page()['screenshot-file']
    image_html = image_to_html(image_path)

    return create_copy_button(text, image_html)

def create_copy_button_source(text): 
    html_path = get_current_page()['html-file']

    with open(html_path, "r", encoding="utf-8") as html_file:
        html_content = html_file.read()

    return create_copy_button(text, html_content)





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
    st.components.v1.html(create_copy_text_button("Copy Text"), height=50)
    st.components.v1.html(create_copy_image_button("Copy Image"), height=50)
    st.components.v1.html(create_copy_button_source("Copy HTML"), height=50)