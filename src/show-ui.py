import streamlit as st
import base64
import json

def page_to_html(page, number_of_pages):
    image_path = page['screenshot-file']
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()

    return f"""<img src="data:image/png;base64,{encoded_string}" style="width:100%;"><p>Page {page['page_number']} / {number_of_pages}"""


def create_copy_button_html(key, text, content): 
    copy_script = """
    <script>
        function copyToClipboardFor{key}() {
            navigator.clipboard.writeText({content}).then(function() {
                console.log('Copied to clipboard successfully!');
            }).catch(function(err) {
                console.error('Could not copy text: ', err);
            });
        }
    </script>

    <button onclick="copyToClipboardFor{key}()">{text}</button>
    """

    return copy_script.replace("{content}", json.dumps(content)).replace("{text}", text).replace("{key}", key)

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
    st.components.v1.html(create_copy_button_html("copy_1", "Copy", "Hello world"), height=50)
    st.components.v1.html(create_copy_button_html("copy_2", "Copy", "Hello world 2"), height=50)