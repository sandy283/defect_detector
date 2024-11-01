import base64
import streamlit as st
import google.generativeai as genai
from PIL import Image
import time

@st.cache_data
def get_img_as_base64(file):
    with open(file, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

img = get_img_as_base64("image.jpg")

page_bg_img = f"""
<style>
[data-testid="stAppViewContainer"] > .main {{
background-image: url("https://images.unsplash.com/photo-1501426026826-31c667bdf23d");
background-size: 180%;
background-position: top left;
background-repeat: no-repeat;
background-attachment: local;
}}

[data-testid="stSidebar"] > div:first-child {{
background-image: url("data:image/png;base64,{img}");
background-position: center; 
background-repeat: no-repeat;
background-attachment: fixed;
}}

[data-testid="stHeader"] {{
background: rgba(0,0,0,0);
}}

[data-testid="stToolbar"] {{
right: 2rem;
}}
</style>
"""

st.markdown(page_bg_img, unsafe_allow_html=True)
st.title("Defect Checker!")
st.sidebar.markdown(
    """
    <h2 style="color:white; font-size:48px; font-weight:bold;">
        Formbid
    </h2>
    <p style="color:white; font-size:24px; font-weight:bold;">
        Together we are creating a smarter Formwork industry
    </p>
    """,
    unsafe_allow_html=True
)

# Input for API Key
api_key = st.sidebar.text_input("Enter your Google API Key:", type="password")

def app_function(image):
    # Check if API key is provided
    if not api_key:
        st.warning("Please enter your Google API key.")
        return "No response due to missing API key."

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')

    def resize_image(image):
        original_width, original_height = image.size
        
        scale_factor = max(1, min(original_width / 256, original_height / 256))
        
        new_width = int(original_width / scale_factor)
        new_height = int(original_height / scale_factor)
        
        resized_image = image.resize((new_width, new_height), Image.LANCZOS)

        return resized_image

    img_resized = resize_image(image)

    response = model.generate_content([f"""
                                    Is this aluminium steel or slab defective or not? The defect can be of various types like crack, bent, cut-off, etc. 

                                    For example:
                                            - Welded portion got cut-off
                                            - Bent slab
                                            - Cracked slab
                                            - Damaged panel
                                            - etc.
                                    
                                    Note: Holes are not considered defects.
                                    
                                    Answer YES or NO only.""", img_resized], stream=True)
    response.resolve()

    return response.text

st.sidebar.markdown(
    """
    <style>
    .custom-uploader {
        font-size: 20px;  /* Increase font size */
        font-weight: bold;  /* Make text bold */
        color: white;  /* Change text color to white */
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.sidebar.markdown('<div class="custom-uploader">Upload Images</div>', unsafe_allow_html=True)
uploaded_files = st.sidebar.file_uploader("", type=['png', 'jpg', 'jpeg'], accept_multiple_files=True)

if st.sidebar.button("Check Defect"):
    if uploaded_files:
        responses = []
        images = []
        with st.spinner("Processing images... Please wait."):
            for uploaded_file in uploaded_files:
                image = Image.open(uploaded_file)
                images.append(image)

                time.sleep(1)
                response = app_function(image)
                responses.append((uploaded_file.name, response))
        
        st.success("Processing complete!")

        for (file_name, output), image in zip(responses, images):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"Response for **{file_name}**:")
                st.write(output)
                st.markdown("---")
            with col2:
                st.image(image, use_column_width=True)
    else:
        st.warning("No images uploaded. Please upload images to check for defects.")
