import base64
import io
# import math

import PIL.Image as Image
# import PIL.ImageDraw as ImageDraw
# import PIL.ImageFont as ImageFont


def pil_image_to_base64_jpeg(rgb_image: Image):
    # In-memory buffer for the JPEG image
    buffered = io.BytesIO()

    # Save as JPEG
    rgb_image.save(buffered, format="JPEG")

    # Encode as base64
    img_str = base64.b64encode(buffered.getvalue()).decode()

    return img_str

import tempfile
from pathlib import Path
from pdf2image import convert_from_bytes
# from pypdf import PdfReader
import logging
import sys


logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logger = logging.getLogger()

def extract_images_from_pdf(pdf_path: str, poppler_path, delete_temp_dir=True):
    logger.info(f"Extracting images from PDF: {pdf_path}")
    with open(pdf_path, "rb") as f:
        with tempfile.TemporaryDirectory(delete=delete_temp_dir) as path:
            logger.info(f"Converting PDF to images using temporary directory: {path}")
            images = convert_from_bytes(f.read(), output_folder=path, fmt="jpeg", poppler_path=poppler_path)
            logger.info(f"Extracted {len(images)} images from the PDF.")
            return images


class DocumentParsingAgent:
    @classmethod
    def get_images(cls, state, poppler_path):
        """
        Extract pages of a PDF as Base64-encoded JPEG images.
        """
        assert Path(state.document_path).is_file(), "File does not exist"
        # Extract images from PDF
        images = extract_images_from_pdf(state.document_path, poppler_path)
        assert images, "No images extracted"
        # Convert images to Base64-encoded JPEG
        pages_as_base64_jpeg_images = [pil_image_to_base64_jpeg(x) for x in images]
        return {"pages_as_base64_jpeg_images": pages_as_base64_jpeg_images}
    
import os

pdf_file_path = os.path.join("data/raw/pension-martijn-files-debugging", "10-page-data-kwaliteit.pdf")
poppler_path = "C:\\Users\\bvbraak\\Projects-Triple-A\\poppler-24.08.0\\Library\\bin"
images = extract_images_from_pdf(pdf_file_path, poppler_path, False)