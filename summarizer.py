import re
from collections import Counter

def extract_key_sentences(text, max_sentences=5):
    """Extract most important sentences using keyword frequency"""
    # Split into sentences
    sentences = [s.strip() for s in re.split(r'[.!?]+', text) if len(s.strip()) > 40]
    
    if not sentences:
        return text[:500] if len(text) > 500 else text
    
    # Get word frequencies (excluding common words)
    common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
                   'of', 'with', 'by', 'from', 'is', 'was', 'are', 'were', 'be', 'been',
                   'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
                   'should', 'may', 'might', 'this', 'that', 'these', 'those', 'it', 'its'}
    
    words = re.findall(r'\b[a-z]{4,}\b', text.lower())
    word_freq = Counter(w for w in words if w not in common_words)
    
    # Score sentences by word importance
    sentence_scores = []
    for sentence in sentences:
        score = sum(word_freq.get(w, 0) for w in re.findall(r'\b[a-z]{4,}\b', sentence.lower()))
        # Boost first few sentences (often contain key info)
        if sentences.index(sentence) < 3:
            score *= 1.5
        sentence_scores.append((score, sentence))
    
    # Get top sentences
    sentence_scores.sort(reverse=True, key=lambda x: x[0])
    top_sentences = [sent for score, sent in sentence_scores[:max_sentences]]
    
    return ". ".join(top_sentences) + "."

def summarize_text(text, max_sentences=5):
    """Improved NLP-based summarization"""
    return extract_key_sentences(text, max_sentences)

def parse_llm_output(raw):
    """Parse LLM output with improved robustness"""
    exec_sum, detail_sum, confidence = [], [], "N/A"
    section = None

    lines = raw.split("\n")
    
    for line in lines:
        line = line.strip()
        
        # Detect sections
        if re.search(r'executive\s+summary', line, re.IGNORECASE):
            section = "exec"
            continue
        elif re.search(r'detailed?\s+summary', line, re.IGNORECASE):
            section = "detail"
            continue
        elif re.search(r'confidence\s+score', line, re.IGNORECASE):
            section = "conf"
            continue
        
        # Extract bullet points
        if line.startswith("-") or line.startswith("•") or line.startswith("*"):
            clean_line = re.sub(r'^[-•*]\s*', '', line).strip()
            if clean_line and len(clean_line) > 10:  # Filter out too-short points
                if section == "exec":
                    exec_sum.append(clean_line)
                elif section == "detail":
                    detail_sum.append(clean_line)
        
        # Extract confidence score
        elif section == "conf":
            m = re.search(r'(\d+)', line)
            if m:
                score = int(m.group(1))
                if 0 <= score <= 100:
                    confidence = f"{score}%"

    # Validate we got meaningful content
    if not exec_sum and not detail_sum:
        # Try to extract any numbered or bulleted list
        all_bullets = re.findall(r'(?:^|\n)[-•*\d.]+\s+(.+?)(?=\n|$)', raw, re.MULTILINE)
        if all_bullets:
            detail_sum = [b.strip() for b in all_bullets if len(b.strip()) > 10][:7]

    return {
        "executive_summary": exec_sum,
        "detailed_summary": detail_sum,
        "confidence_score": confidence
    }