from docling.document_converter import DocumentConverter, DocumentStream
import os
import magic
import requests
import re

def load_document(url):
    mime = magic.Magic(mime=True)
    file_type = mime.from_file(url)
    if not any(ext in file_type for ext in ["pdf", "word", "text"]):
        raise ValueError(f"Unsupported file type: {file_type}")
    print(file_type)

# def load_document(file_path) -> str:
#     ext = os.path.splitext(file_path)[1].lower()
#     if ext not in ALLOWED_EXTENSIONS:
#         raise ValueError(f"Unsupported file type: {ext}")
#     else: 
#         return convert_file_to_md(file_path)

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

#load_document('/Users/valeriesong/Downloads/Remarkably Bright Creatures Week I (Sept 24-26) Response Sheet.pdf')
load_document("/Users/valeriesong/Downloads/mongodb-compass-1.46.11-darwin-arm64.dmg")

# image processing