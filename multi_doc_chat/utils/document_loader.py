from pathlib import Path 
from typing import Iterable, List
from langchain_core.documents import Document
import fitz 
import os
import pymupdf 
from multi_doc_chat.logger import GLOBAL_LOGGER as log 
from multi_doc_chat.exceptions.custom_exception import CustomException 
from langchain_community.document_loaders import (
    PyMuPDFLoader,
    TextLoader,
    Docx2txtLoader,
    UnstructuredPowerPointLoader,
    CSVLoader,
    UnstructuredExcelLoader
)
from fastapi import UploadFile

def load_documents(file_path: str, output_dir: str = "./extracted_images") -> List[Document]:
    """
    Load text from various file formats and extract images (for PDFs only).

    Supported:
        .pdf, .docx, .txt, .pptx, .md, .csv, .xlsx, .xls
    Returns:
        List[Document]
    """
    try:
        ext = Path(file_path).suffix.lower()
        # Handle PDF with images 
        if ext == '.pdf':
            os.makedirs(output_dir, exist_ok=True)
            loader = PyMuPDFLoader(file_path)
            documents = loader.load() 

            pdf = fitz.open(file_path)
            images_metadata = [] 

            for page_index in range(len(pdf)):
                page = pdf[page_index]
                images = page.get_images(full = True)

                for img_index, img in enumerate(images, start = 1):
                    xref = img[0] 
                    name = img[7]
                    base_image = pdf.extract_image(xref)
                    image_bytes = base_image["image"]
                    img_ext = base_image["ext"]

                    # Save Image 
                    image_filename = f"page{page_index + 1}_img{img_index}.{img_ext}"
                    image_path = os.path.join(output_dir, image_filename)
                    with open(image_path, 'wb') as f:
                        f.write(image_bytes)

                    # Get bounding box if possible 
                    bbox = None 
                    try:
                        rect = page.get_image_bbox(name)
                        bbox = [round(coord, 2) for coord in rect]
                    except ValueError:
                        try:
                            rects = page.get_image_rects(xref)
                            bbox = [round(coord, 2) for coord in rects[0]] if rects else None 
                        except Exception:
                            bbox = None 
                    
                    images_metadata.append({
                        "page": page_index + 1, 
                        "image_path": image_path, 
                        "bbox": bbox, 
                        "xref": xref
                    })
            pdf.close()

            # Attach image metadata to corresponding page documents
            for doc in documents:
                page_num = doc.metadata.get("page", 0) + 1
                page_images = [img for img in images_metadata if img["page"] == page_num]
                doc.metadata["images"] = page_images
            
            log.info("PDF Text and Images extracted succesfully", document_counts = len(documents), image_count = len(images_metadata))
            print(f"Extracted {len(images_metadata)} images and {len(documents)} text documents.")
            return documents

        # Handle Other File Types
        elif ext == ".docx":
            loader = Docx2txtLoader(file_path)
        elif ext in [".txt", ".md"]:
            loader = TextLoader(file_path)
        elif ext == ".pptx":
            loader = UnstructuredPowerPointLoader(file_path)
        elif ext == ".csv":
            loader = CSVLoader(file_path)
        elif ext in [".xlsx", ".xls"]:
            loader = UnstructuredExcelLoader(file_path)
        else:
            raise ValueError(f"Unsupported file format: {ext}")

        documents = loader.load()
        log.info("Documents loaded successfully", document_count=len(documents))
        print(f"Loaded {len(documents)} text documents from {ext}")
        return documents

    except Exception as e:
        log.error("Error loading document", error=str(e))
        raise CustomException(e, error_details="Error while loading file")

if __name__ == "__main__":
    file_path = r"C:\Users\hites\OneDrive\Desktop\LLMops\data\human-nutrition-text.pdf"
    docs = load_documents(file_path)
    print(docs[100])