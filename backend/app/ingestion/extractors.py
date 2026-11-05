import io
from typing import Optional

def extract_text(file_bytes: bytes, file_type: str) -> str:
    """
    Extract raw text from PDF, DOCX, HTML, or plain text files using real parsers.
    """
    clean_type = file_type.lower().lstrip(".")
    
    if clean_type == "pdf":
        try:
            import fitz  # PyMuPDF
            doc = fitz.open(stream=file_bytes, filetype="pdf")
            extracted_pages = []
            for page_index in range(len(doc)):
                page = doc[page_index]
                page_text = page.get_text().strip()
                if page_text:
                    extracted_pages.append(f"--- Page {page_index + 1} ---\n{page_text}")
            doc.close()
            return "\n\n".join(extracted_pages)
        except Exception as e:
            print(f"Error extracting PDF text with PyMuPDF: {e}")
            raise ValueError(f"Failed to extract text from PDF: {e}")
            
    elif clean_type in ["docx", "doc"]:
        try:
            import docx
            doc = docx.Document(io.BytesIO(file_bytes))
            paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
            return "\n\n".join(paragraphs)
        except Exception as e:
            print(f"Error extracting DOCX text: {e}")
            raise ValueError(f"Failed to extract text from DOCX: {e}")
            
    elif clean_type in ["html", "htm"]:
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(file_bytes.decode("utf-8", errors="ignore"), "html.parser")
            return soup.get_text(separator="\n").strip()
        except Exception as e:
            print(f"Error extracting HTML text: {e}")
            raise ValueError(f"Failed to extract text from HTML: {e}")
            
    else:
        # Fallback to plain UTF-8 text decoding
        return file_bytes.decode("utf-8", errors="ignore").strip()
