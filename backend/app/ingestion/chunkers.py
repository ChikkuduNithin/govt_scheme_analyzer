import re
from typing import List, Dict
from langchain_text_splitters import RecursiveCharacterTextSplitter

def chunk_document(text: str, chunk_size: int = 800, chunk_overlap: int = 120) -> List[Dict]:
    """
    Split text into semantic chunks while extracting page number metadata where available.
    """
    if not text or not text.strip():
        return []
    
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", "; ", " ", ""]
    )
    
    # Check if text contains structured page markers: "--- Page X ---"
    page_sections = re.split(r"(?:^|\n)--- Page (\d+) ---\n", text)
    
    chunks: List[Dict] = []
    
    if len(page_sections) > 1:
        # First element might be preface or empty
        current_page = 1
        i = 1
        while i < len(page_sections):
            try:
                page_num = int(page_sections[i])
                page_content = page_sections[i + 1] if i + 1 < len(page_sections) else ""
            except (ValueError, IndexError):
                i += 1
                continue
                
            page_chunks = splitter.split_text(page_content)
            for idx, c in enumerate(page_chunks):
                clean_chunk = c.strip()
                if clean_chunk:
                    chunks.append({
                        "text": clean_chunk,
                        "page_number": page_num,
                        "section": f"Page {page_num} Part {idx + 1}"
                    })
            i += 2
    else:
        # Generic text splitting
        split_texts = splitter.split_text(text)
        for idx, c in enumerate(split_texts):
            clean_chunk = c.strip()
            if clean_chunk:
                chunks.append({
                    "text": clean_chunk,
                    "page_number": 1,
                    "section": f"Section {idx + 1}"
                })
                
    return chunks
