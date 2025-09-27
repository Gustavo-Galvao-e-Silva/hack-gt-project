from docling.document_converter import DocumentConverter, DocumentStream


def covert_file_to_md(source_file: DocumentStream) -> str:
    converter = DocumentConverter()
    doc = converter.convert(source_file).document
    return doc.export_to_markdown()

