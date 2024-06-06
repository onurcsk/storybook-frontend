import streamlit as st
from PIL import Image
import os
from io import BytesIO
import hashlib
import requests
import pdfkit

API_HOST = os.environ['API_HOST']

generated_story = ""

# Streamlit app configuration
st.set_page_config(
    page_title="Storybook",
    page_icon="📖",
    layout="centered",
    initial_sidebar_state="auto"
)

# Set header image
image_url = "https://cdn.pixabay.com/animation/2023/06/13/15/13/15-13-16-625_512.gif"  # Replace with your image URL
st.markdown(
    f"""
    <div style="display: flex; justify-content: center;">
        <img src="{image_url}" width="200">
    </div>
    """,
    unsafe_allow_html=True
)

if 'cached_captions' not in st.session_state:
    st.session_state.cached_captions = {}

if 'story_history' not in st.session_state:
    st.session_state.story_history = []

if 'characters' not in st.session_state:
    st.session_state.characters = []

# Function to hash image
def hash_image(image):
    buffer = BytesIO()
    image.save(buffer, format='PNG')
    img_str = buffer.getvalue()
    return hashlib.md5(img_str).hexdigest()

def display_header():
    header_html = """
    <h1 style="text-align: center; color: #ff69b4;">
        <span style="color:red; margin-right: 0px;">S</span>
        <span style="color:orange; margin-right: 0px;">t</span>
        <span style="color:yellow; margin-right: 0px;">o</span>
        <span style="color:green; margin-right: 0px;">r</span>
        <span style="color:blue; margin-right: 0px;">y</span>
        <span style="color:indigo; margin-right: 0px;">b</span>
        <span style="color:violet; margin-right: 0px;">o</span>
        <span style="color:red; margin-right: 0px;">o</span>
        <span style="color:orange; margin-right: 0px;">k</span>
        <span style="margin-right: 15px;"> </span>  <!-- Extra space between words -->
        <span style="color:green; margin-right: 0px;">y</span>
        <span style="color:blue; margin-right: 0px;">o</span>
        <span style="color:indigo; margin-right: 0px;">u</span>
        <span style="color:violet; margin-right: 0px;">r</span>
        <span style="margin-right: 15px;"> </span>  <!-- Extra space between words -->
        <span style="color:orange; margin-right: 0px;">p</span>
        <span style="color:yellow; margin-right: 0px;">h</span>
        <span style="color:green; margin-right: 0px;">o</span>
        <span style="color:blue; margin-right: 0px;">t</span>
        <span style="color:indigo; margin-right: 0px;">o</span>
        <span style="color:violet; margin-right: 0px;">s</span>
        <span style="color:red;">!</span>
    </h1>
    """
    st.markdown(header_html, unsafe_allow_html=True)

display_header()

st.markdown(
    """
    <div style="position: fixed; bottom: 10px; right: 10px; color: gray; font-size: 12px;">
        LeWagon | Data Science & AI | Final Project | Storybook
    </div>
    """,
    unsafe_allow_html=True
)

# Initialize session state for user inputs if not already present
if 'genre' not in st.session_state:
    st.session_state['genre'] = ""
if 'num_words' not in st.session_state:
    st.session_state['num_words'] = 25  # Default to 25 or another appropriate default value
if 'reader_age' not in st.session_state:
    st.session_state['reader_age'] = 0  # Default to the youngest age or another appropriate initial value
if 'language' not in st.session_state:
    st.session_state['language'] = ""

# User inputs for story generation
st.subheader("📖 Story Details")
st.session_state['genre'] = st.text_input(
    "Enter the story genre or theme description (optional):",
    value=st.session_state['genre'],
    placeholder="e.g. Baking, Dragons, Travel, Jealousy..."
)

st.session_state['num_words'] = st.number_input(
    "Enter the number of words in your story (optional):",
    min_value=25,
    step=1,
    value=st.session_state['num_words'],
)

st.session_state['reader_age'] = st.selectbox(
    "Select the reader's age (optional):",
    list(range(0, 19)),
    index=st.session_state['reader_age']
)

# Select box for language
language_options = ["English", "Japanese", "Korean", "Arabic", "Bahasa Indonesia", "Bengali", "Bulgarian",
    "Chinese (Simplified / Traditional)", "Croatian", "Czech", "Danish", "Dutch", "Estonian",
    "Farsi", "Finnish", "French", "German", "Gujarati", "Greek", "Hebrew", "Hindi", "Hungarian",
    "Italian", "Kannada", "Latvian", "Lithuanian", "Malayalam", "Marathi", "Norwegian", "Polish",
    "Portuguese", "Romanian", "Russian", "Serbian", "Slovak", "Slovenian", "Spanish", "Swahili",
    "Swedish", "Tamil", "Telugu", "Thai", "Turkish", "Ukrainian", "Urdu", "Vietnamese"
]

# Use st.selectbox to display the options with a default value of "English"
language = st.selectbox("Choose Language:", language_options, index=0)  # Select "English" by default

# Use st.empty as a placeholder to display the user's selection
user_selection = st.empty()

# Check if a selection was made using a conditional statement
if language != "English":
  user_selection.text(f"")  # Display selection
else:
  user_selection.text("No language selected. Using English by default.")  # Display default message

st.session_state['language'] = language

# Character names and genders input
st.subheader("🫅🏻 Character Details")
new_character_name = st.text_input("Enter the character's name:", key="new_character_name", placeholder="e.g. Lola")
new_character_gender = st.selectbox(
    "Select character gender:",
    ["Female", "Male", "Non-Binary", "Prefer not to say"],
    key="new_character_gender"
)

# Button to add character to the list
if st.button("Add a Character"):
    if new_character_name:
        st.session_state.characters.append({
            'name': new_character_name,
            'gender': new_character_gender
        })
    else:
        st.warning("Character name cannot be empty.")

# Display the list of added characters
if st.session_state.get("characters"):
    st.write("**Characters:**")
    for idx, character in enumerate(st.session_state.characters):
        col1, col2 = st.columns([15, 1])
        with col2:
            # Button to delete character
            if st.button(f"❌", key=f"delete_button_{idx}"):
                st.session_state.characters.pop(idx)
        with col1:
            st.write(f"{idx + 1}. {character['name']} ({character['gender']})")

st.markdown("---")

# Image upload and captioning
st.subheader("📸 Upload Images and Generate Story")
uploaded_files = st.file_uploader("Upload up to 5 images", type=["jpg", "jpeg", "png"], accept_multiple_files=True)
image_captions = []

if uploaded_files:
    if len(uploaded_files) > 5:
        st.warning("You can only upload up to 5 images.")
    else:
        for uploaded_file in uploaded_files:
            # Open the image
            image = Image.open(uploaded_file)
            # Hash the image
            image_hash = hash_image(image)
            # Check if the image has been processed before
            if image_hash in st.session_state.cached_captions:
                caption = st.session_state.cached_captions[image_hash]
            else:
                # Generate and cache the caption
                caption = requests.post(API_HOST + "generate_caption/", files={"file": uploaded_file.getvalue()}).json()["caption"]
                st.session_state.cached_captions[image_hash] = caption
            image_captions.append(caption)

        with st.expander("View uploaded images and captions"):
            for uploaded_file, caption in zip(uploaded_files, image_captions):
                # Open and display the image
                image = Image.open(uploaded_file)
                st.image(image, caption='Uploaded Image', use_column_width=True)
                # Display the caption
                st.write(f"**Caption:** {caption}")

  # Generate PDF
def generate_story_pdf(story):
    html_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                font-family: 'Times New Roman', serif;
                font-size: 30px;
                margin: 0; /* Remove margin to ensure full centering */
                border: 1px solid #000;
                padding: 10px;
                flex-direction: column; /* Aligns children vertically */
                justify-content: center;
                align-items: center; /* Centers children horizontally */
            }}
            .story-container {{
                padding: 20px;
                margin: 20px; /* Adjust or remove margin if necessary */
                line-height: 1.3;
                text-align:  justify; /* Centers the text within the container */
            }}
            h1 {{
                text-align: center; /* Explicitly center the header text */
            }}
            .footer {{
            text-align: center;
            font-size: 12px;
            color: gray;
            margin-top: 20px;
        }}
        </style>
        <meta charset="utf-8">
    </head>
    <body>
        <h1> Your Story </h1>
        <div class="story-container">
        {generated_story}
    </div>
        <div class="footer">
        Your story brought to you by the creators of Storybook
    </div>
    </body>
    </html>
    """

    pdf = pdfkit.from_string(html_template, False)
    #st.download_button(
        #label="⬇️ Download story as PDF",
        #data=pdf,
        #file_name="story.pdf",
        #mime="application/octet-stream")
    return pdf

# Initialize session state
if 'story_pdfs' not in st.session_state:
    st.session_state['story_pdfs'] = []

# Button to generate story
if st.button("✨ Write my story!"):
    # Fetch current input values from session state
    genre = st.session_state['genre']
    num_words = st.session_state['num_words']
    reader_age = st.session_state['reader_age']
    language = st.session_state['language']
    character_names = ",".join([char['name'] for char in st.session_state.characters])
    character_genders = ",".join([char['gender'] for char in st.session_state.characters])

    # Generate the story using the fetched values and save the story and its details in the session state
    data = {
        "genre": genre,
        "num_words": num_words,
        "reader_age": reader_age,
        "language": language,
        "character_names": character_names,
        "character_genders": character_genders,
        "captions": image_captions,
    }
    
    generated_story = requests.post(API_HOST + "generate_story/", data=data).json()["story"]
    story_details = {
        "genre": genre,
        "num_words": num_words,
        "reader_age": reader_age,
        "language": language,
        "character_names": character_names,
        "character_genders": character_genders,
        "captions": image_captions,
        "story": generated_story
    }

 # Append the new story details to the history, limit to 5
    st.session_state.story_history.append(story_details)
    if len(st.session_state.story_history) > 5:
        st.session_state.story_history.pop(0)

    st.subheader("✨ Your Story:")
    st.write(generated_story)

    # Generate PDF for the newly generated story
    story_pdf = generate_story_pdf(generated_story)

    # Store the PDF in session state for later download
    st.session_state.story_pdfs.append(story_pdf)

st.markdown("---")

# Display the story history
if st.session_state.story_history:
    with st.expander("View story history and download your favourite(s)!"):
        tab_titles = [f"Story {i+1}" for i in range(len(st.session_state.story_history))]
        tabs = st.tabs(tab_titles)

        for idx, (tab, story_details, story_pdf) in enumerate(zip(tabs, st.session_state.story_history, st.session_state.story_pdfs)):
            with tab:
                st.write(f"**Story Genre or Theme:** {story_details['genre']}")
                st.write(f"**Number of Words:** {story_details['num_words']}")
                st.write(f"**Reader's Age:** {story_details['reader_age']}")
                st.write(f"**Character Names:** {', '.join(story_details['character_names'])}")
                st.write(f"**Character Genders:** {', '.join(story_details['character_genders'])}")
                st.write(f"**Captions:** {', '.join(story_details['captions'])}")

                # Display the story
                st.write(f"**Story:** {story_details['story']}")

                # Display the download button for the PDF
                st.download_button(
                    label="⬇️ Download story as PDF",
                    data=story_pdf,
                    file_name=f"story_{idx+1}.pdf",  # Use a unique filename for each story
                    mime="application/octet-stream",
                    key=f"download_button_{idx}")
