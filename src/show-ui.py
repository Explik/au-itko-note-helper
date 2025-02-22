import streamlit as st
import os
from PIL import Image
import base64

# Function to convert image to HTML
def image_to_html(image_path):
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()
    return f'<img src="data:image/png;base64,{encoded_string}" style="width:100%;">'

# Get list of image files in the directory
image_folder = './output/screenshots'
image_files = [os.path.join(image_folder, file) for file in os.listdir(image_folder) if file.endswith(('png', 'jpg', 'jpeg'))]

# Generate HTML pages from images
pages = [image_to_html(image_file) for image_file in image_files]

# Initialize session state for page index
if 'page_index' not in st.session_state:
    st.session_state.page_index = 0

# Function to navigate pages
def navigate(direction):
    if direction == 'next':
        st.session_state.page_index = (st.session_state.page_index + 1) % len(pages)
    elif direction == 'prev':
        st.session_state.page_index = (st.session_state.page_index - 1) % len(pages)

# Display current page
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