import re
from pypdf import PdfReader
from pypdf.errors import PdfReadError
from collections import Counter

def detect_repeated_patterns(text):
    """Detect and remove repeated headers/footers"""
    lines = text.split('\n')
    line_counts = Counter(lines)
    
    # Find lines that appear more than 3 times (likely headers/footers)
    repeated_lines = {line for line, count in line_counts.items() if count > 3 and len(line.strip()) > 5}
    
    return repeated_lines

def clean_academic_pdf(text):
    """Clean academic PDFs (slides, papers) with aggressive noise removal"""
    
    # Remove date patterns
    text = re.sub(r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+\d{4}\b', '', text, flags=re.IGNORECASE)
    
    # Remove standalone numbers (slide numbers)
    text = re.sub(r'^\s*\d+\s*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'\n\s*\d+\s*\n', '\n', text)
    
    # Remove page number patterns
    text = re.sub(r'\bPage\s+\d+\s+of\s+\d+\b', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\b\d+\s*/\s*\d+\b', '', text)
    
    # Remove common academic headers
    academic_patterns = [
        r'CS\s*\d+\s*[–-]\s*\w+.*?(?=\n)',  # Course codes
        r'Class\s+\d+:.*?(?=\n)',
        r'Lecture\s+\d+.*?(?=\n)',
        r'Fall\s+\d{4}.*?(?=\n)',
        r'Spring\s+\d{4}.*?(?=\n)',
        r'Winter\s+\d{4}.*?(?=\n)',
        r'Summer\s+\d{4}.*?(?=\n)',
    ]
    
    for pattern in academic_patterns:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE)
    
    # Remove ellipsis
    text = re.sub(r'…+', ' ', text)
    text = re.sub(r'\.{3,}', ' ', text)
    
    # Remove URLs
    text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
    
    # Remove email addresses
    text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '', text)
    
    # Split into lines and clean
    lines = text.split('\n')
    
    # Detect repeated patterns
    repeated_patterns = detect_repeated_patterns(text)
    
    # Filter lines
    cleaned_lines = []
    for line in lines:
        line = line.strip()
        
        # Skip empty lines
        if not line:
            continue
        
        # Skip very short lines (likely noise)
        if len(line) < 10:
            continue
        
        # Skip repeated headers/footers
        if line in repeated_patterns:
            continue
        
        # Skip lines that are just numbers or symbols
        if re.match(r'^[\d\s\.\-–—]+$', line):
            continue
        
        cleaned_lines.append(line)
    
    # Join back together
    cleaned_text = ' '.join(cleaned_lines)
    
    # Remove multiple spaces
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text)
    
    # Remove duplicate sentences (common in slides)
    sentences = re.split(r'[.!?]+', cleaned_text)
    unique_sentences = []
    seen = set()
    
    for sentence in sentences:
        sentence = sentence.strip()
        if sentence and len(sentence) > 20:
            # Normalize for comparison
            normalized = re.sub(r'\s+', ' ', sentence.lower())
            if normalized not in seen:
                seen.add(normalized)
                unique_sentences.append(sentence)
    
    final_text = '. '.join(unique_sentences)
    
    return final_text

def extract_text_from_pdf(file_path, max_pages=30):
    """Extract text from PDF with improved cleaning for academic documents"""
    try:
        reader = PdfReader(file_path)
        
        if reader.is_encrypted:
            return "", ["PDF is encrypted and cannot be read"]
        
        total_pages = len(reader.pages)
        if total_pages == 0:
            return "", ["PDF has no pages"]
        
        text = ""
        errors = []
        pages_to_process = min(max_pages, total_pages)

        for i in range(pages_to_process):
            try:
                page = reader.pages[i]
                page_text = page.extract_text()
                
                if page_text:
                    text += page_text + "\n"
            except Exception as e:
                errors.append(f"Failed to extract text from page {i+1}: {str(e)}")
        
        if not text.strip():
            return "", ["No text could be extracted. The PDF might contain only images or scanned content"]
        
        # Clean the extracted text aggressively
        text = clean_academic_pdf(text)
        
        if len(text) < 100:
            return "", ["Insufficient meaningful text content extracted from PDF"]
        
        return text.strip(), errors
    
    except PdfReadError as e:
        raise Exception(f"Invalid or corrupted PDF file: {str(e)}")
    except FileNotFoundError:
        raise Exception("PDF file not found")
    except Exception as e:
        raise Exception(f"Error reading PDF: {str(e)}")