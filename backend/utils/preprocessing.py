from io import BytesIO
import re
from docling.document_converter import DocumentConverter, DocumentStream


def clean_artifacts(text: str) -> str:
    # Remove page numbers or common OCR artifacts
    text = re.sub(r'\n\s*\d+\s*\n', '\n', text)  # standalone numbers
    text = re.sub(r'\s*[-–—]{3,}\s*', '\n', text)  # horizontal lines
    text = re.sub(r'\n{3,}', '\n\n', text)  # multiple blank lines
    return text

def normalize_lists(text: str) -> str:
    # Standardize bullet points to '- '
    text = re.sub(r'^[\*\•\–]\s+', '- ', text, flags=re.MULTILINE)
    return text

def normalize_headings(text: str) -> str:
    # Ensure headings have proper spacing
    text = re.sub(r'^(#{1,6})([^\s#])', r'\1 \2', text, flags=re.MULTILINE)
    return text

def merge_broken_paragraphs(text: str) -> str:
    # Merge lines that are broken in the middle of a paragraph
    lines = text.split('\n')
    merged_lines = []
    for line in lines:
        if line.strip() == '':
            merged_lines.append('')
        elif merged_lines and not merged_lines[-1].endswith(('.', '?', '!', ':')) and not merged_lines[-1].startswith('#') and not merged_lines[-1].startswith('- '):
            merged_lines[-1] += ' ' + line.strip()
        else:
            merged_lines.append(line.strip())
    return '\n'.join(merged_lines)

def preprocess_markdown(markdown_text: str) -> str:
    text = markdown_text
    text = clean_artifacts(text)
    text = normalize_lists(text)
    text = normalize_headings(text)
    text = merge_broken_paragraphs(text)
    return text


def convert_file_to_md(source_file: BytesIO) -> str:
    converter = DocumentConverter()
    doc_stream = DocumentStream(name="document", stream=source_file)
    file = converter.convert(doc_stream).document
    md_file = file.export_to_markdown()
    return preprocess_markdown(md_file)

