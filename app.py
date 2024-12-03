# Pillow ANTIALIAS compatibility layer
try:
    import PIL.Image
    if not hasattr(PIL.Image, 'ANTIALIAS'):
        try:
            PIL.Image.ANTIALIAS = PIL.Image.Resampling.LANCZOS
        except AttributeError:
            # Fallback for different Pillow versions
            PIL.Image.ANTIALIAS = 1
except ImportError:
    pass

import streamlit as st
import numpy as np
import cv2
import easyocr
import boto3

class ImageTextTranslator:
    def __init__(self, region_name='us-east-1'):
        """
        Initialize AWS Translate and EasyOCR capabilities
        """
        # AWS Translate Client
        self.translate_client = boto3.client('translate', region_name=region_name)
        
        # Initialize EasyOCR reader with multiple languages
        self.reader = easyocr.Reader([
            'en', 'es', 'fr', 'de', 'it', 
            'no'
        ], gpu=False)
        
        self.target_languages = {
        'English': 'en', 
        'Spanish': 'es', 
        'French': 'fr', 
        'German': 'de', 
        'Chinese': 'zh-cn', 
        'Japanese': 'ja', 
        'Arabic': 'ar', 
        'Swahili': 'sw',
        'Norwegian':'no'
        }

        self.source_languages = {
        'English': 'en', 
        'Spanish': 'es', 
        'French': 'fr', 
        'German': 'de', 
        'Chinese': 'zh-cn', 
        'Japanese': 'ja', 
        'Arabic': 'ar', 
        'Swahili': 'sw',
        'Norwegian':'no'
        }

    def preprocess_image(self, image):
        """
        Preprocess image to improve OCR accuracy
        
        Args:
            image (numpy.ndarray): Input image
        
        Returns:
            numpy.ndarray: Preprocessed image
        """
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply thresholding
        gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
        
        return gray

    def extract_text(self, image):
        """
        Extract text from image using EasyOCR
        
        Args:
            image (numpy.ndarray): Input image
        
        Returns:
            str: Extracted text
        """
        try:
            # Use EasyOCR to read text
            results = self.reader.readtext(image)
            
            # Combine all detected text
            text = ' '.join([result[1] for result in results])
            return text.strip()
        except Exception as e:
            st.error(f"OCR Error: {e}")
            return ""

    def translate_text(self, text, source_lang='auto', target_lang='en'):
        """
        Translate text using AWS Translate
        
        Args:
            text (str): Text to translate
            source_lang (str): Source language code
            target_lang (str): Target language code
        
        Returns:
            str: Translated text
        """
        try:
            # Remove 'auto' for AWS Translate
            source_lang = 'auto' if source_lang == 'auto' else source_lang
            
            response = self.translate_client.translate_text(
                Text=text,
                SourceLanguageCode=source_lang,
                TargetLanguageCode=target_lang
            )
            return response['TranslatedText']
        except Exception as e:
            st.error(f"Translation Error: {e}")
            return text

def main():
    # Set page configuration
    st.set_page_config(
        page_title="Image Text Translator", 
        page_icon="🌐",
        layout="wide"
    )

    # Title and description
    st.title("🖼️ Image Text Translator")
    st.write("Upload an image or use your camera to extract and translate text")

    # Initialize translator
    translator = ImageTextTranslator()

    # Sidebar for input methods
    st.sidebar.header("Translation Settings")
    
    # Input method selection
    input_method = st.sidebar.radio(
        "Select Input Method", 
        ["Upload Image", "Camera Input"]
    )

    target_languages = translator.target_languages
    source_languages = translator.source_languages
    source_key = st.sidebar.selectbox(
        "Source Language", 
        list(source_languages.keys()), 
        index=0
    )
    target_key = st.sidebar.selectbox(
        "Target Language", 
        list(target_languages.keys()), 
        index=0
    )

    source_lang = source_languages[source_key]
    target_lang = target_languages[target_key]

    # Session state to manage translation
    if 'extracted_text' not in st.session_state:
        st.session_state.extracted_text = ""
    if 'translated_text' not in st.session_state:
        st.session_state.translated_text = ""
    if 'show_translation' not in st.session_state:
        st.session_state.show_translation = False

    # Input image based on method
    if input_method == "Upload Image":
        uploaded_file = st.file_uploader(
            "Choose an image...", 
            type=["jpg", "jpeg", "png"]
        )
        if uploaded_file is not None:
            # Read image
            file_bytes = uploaded_file.read()
            image = cv2.imdecode(
                np.frombuffer(file_bytes, np.uint8), 
                cv2.IMREAD_COLOR
            )
    else:
        # Camera input
        camera_image = st.camera_input("Take a picture")
        if camera_image is not None:
            # Read camera image
            file_bytes = camera_image.read()
            image = cv2.imdecode(
                np.frombuffer(file_bytes, np.uint8), 
                cv2.IMREAD_COLOR
            )
    
    # Process if image is available
    if 'image' in locals():
        # Create columns for display
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Original Image")
            st.image(image, channels="BGR")
        
        # Extract text
        st.session_state.extracted_text = translator.extract_text(image)
        
        # Translate button
        if st.session_state.extracted_text:
            if st.button("Translate Text"):
                # Translate text
                st.session_state.translated_text = translator.translate_text(
                    st.session_state.extracted_text, 
                    source_lang=source_lang, 
                    target_lang=target_lang
                )
                st.session_state.show_translation = True
        
        # Show translation if button is pressed
        if st.session_state.show_translation:
            with col2:
                st.subheader("Translated Text")
                st.text_area(
                    f"Translation ({source_lang} → {target_lang})", 
                    st.session_state.translated_text, 
                    height=150
                )

if __name__ == "__main__":
    main()