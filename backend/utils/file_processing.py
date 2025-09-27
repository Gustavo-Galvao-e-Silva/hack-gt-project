from docling.document_converter import DocumentConverter, DocumentStream
import os
import magic
import requests
import re

ALLOWED_EXTENSIONS = {'.pdf', '.doc', '.txt'}

# def load_document(url):
#     mime = magic.Magic(mime=True)
#     file_type = mime.from_file(url)
#     print(file_type)

def load_document(file_path) -> str:
    ext = os.path.splitext(file_path)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError(f"Unsupported file type: {ext}")
    else: 
        return convert_file_to_md(file_path)

def clean_text(raw_text: str) -> str:
    text = re.sub(r'\s+', ' ', raw_text)
    text = text.replace("–", "-").replace("—", "-")
    text = text.replace("“", '"').replace("”", '"').replace("’", "'")
    text = re.sub(r'!\[.*?\]\(.*?\)', '', text)
    return text.strip()

def convert_file_to_md(source_file: DocumentStream) -> str:
    converter = DocumentConverter()
    doc = converter.convert(source_file).document
    cleantext = doc.export_to_markdown()
    return clean_text(cleantext)

print(load_document('/Users/valeriesong/Downloads/Remarkably Bright Creatures Week I (Sept 24-26) Response Sheet.pdf'))
#load_document('https://www.google.com/images/branding/googlelogo/1x/googlelogo_light_color_272x92dp.png')

# image processing