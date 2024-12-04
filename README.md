# image_text_translator

## Key Features:
* Image preprocessing (grayscale, thresholding, deskewing)
* OCR (EasyOCR)
* Translation support

## Main Workflow:
* Preprocess image
* Extract text using selected OCR method
* Translate extracted text
* Return results

## Dependencies:
* easyocr: OCR method with multi-language support
* opencv-python: Image preprocessing
* boto3: Text translation
* pillow: Image handling
* streamlit: For deployment

## Deployment
* create a dockerfile
* create requirements.txt file
* create a docker compose file
* Build the Docker image
  docker compose build
* Run the application
  docker compose up

## Ship to Render.com
