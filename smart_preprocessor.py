import re
from collections import Counter

class SmartPreprocessor:
    """Intelligent text preprocessing based on content type"""
    
    def __init__(self):
        self.academic_indicators = ['theorem', 'lemma', 'proof', 'algorithm', 'lecture', 'chapter', 'section']
        self.news_indicators = ['reported', 'according to', 'sources say', 'announced', 'breaking']
        self.business_indicators = ['revenue', 'profit', 'market', 'quarter', 'earnings', 'CEO', 'company']
        
    def detect_content_type(self, text):
        """Detect if content is academic, news, business, or general"""
        text_lower = text.lower()
        
        academic_score = sum(1 for word in self.academic_indicators if word in text_lower)
        news_score = sum(1 for word in self.news_indicators if word in text_lower)
        business_score = sum(1 for word in self.business_indicators if word in text_lower)
        
        scores = {
            'academic': academic_score,
            'news': news_score,
            'business': business_score
        }
        
        max_score = max(scores.values())
        if max_score < 2:
            return 'general'
        
        return max(scores.items(), key=lambda x: x[1])[0]
    
    def detect_repeated_noise(self, text):
        """Find and remove repeated headers/footers"""
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        # Count line occurrences
        line_counts = Counter(lines)
        
        # Lines appearing more than 3 times are likely noise
        noise_lines = {
            line for line, count in line_counts.items() 
            if count > 3 and 5 < len(line) < 100
        }
        
        return noise_lines
    
    def remove_academic_noise(self, text):
        """Remove academic document noise"""
        # Remove course codes and semester info
        text = re.sub(r'\b[A-Z]{2,4}\s*\d{3,5}\b', '', text)
        text = re.sub(r'\b(?:Fall|Spring|Summer|Winter)\s+\d{4}\b', '', text, flags=re.IGNORECASE)
        
        # Remove class/lecture numbers
        text = re.sub(r'\b(?:Class|Lecture|Chapter|Section)\s+\d+\s*:?', '', text, flags=re.IGNORECASE)
        
        # Remove slide indicators
        text = re.sub(r'Slide\s+\d+', '', text, flags=re.IGNORECASE)
        
        return text
    
    def remove_dates(self, text):
        """Remove standalone dates"""
        # Remove dates like "December 1, 2025"
        text = re.sub(
            r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+\d{4}\b',
            '', text, flags=re.IGNORECASE
        )
        
        # Remove dates like "12/01/2025"
        text = re.sub(r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b', '', text)
        
        return text
    
    def remove_page_numbers(self, text):
        """Remove page numbers and related info"""
        # Page X of Y
        text = re.sub(r'\bPage\s+\d+\s+of\s+\d+\b', '', text, flags=re.IGNORECASE)
        
        # Standalone numbers on their own lines
        text = re.sub(r'^\s*\d+\s*$', '', text, flags=re.MULTILINE)
        text = re.sub(r'\n\s*\d+\s*\n', '\n', text)
        
        return text
    
    def extract_meaningful_sentences(self, text, min_length=30):
        """Extract sentences with actual content"""
        # Split into sentences
        sentences = re.split(r'[.!?]+', text)
        
        meaningful = []
        for sentence in sentences:
            sentence = sentence.strip()
            
            # Skip too short
            if len(sentence) < min_length:
                continue
            
            # Skip if mostly numbers/symbols
            if re.match(r'^[\d\s\.\-–—:;,]+$', sentence):
                continue
            
            # Skip if it's just a header pattern
            if re.match(r'^[A-Z\s\d\-–—:]+$', sentence) and len(sentence) < 100:
                continue
            
            meaningful.append(sentence)
        
        return meaningful
    
    def smart_clean(self, text, source_type='document'):
        """
        Intelligently clean text based on content type
        
        Args:
            text: Raw text
            source_type: Type of document
            
        Returns:
            Cleaned text
        """
        # Detect content type
        content_type = self.detect_content_type(text)
        
        # Remove common noise
        text = self.remove_dates(text)
        text = self.remove_page_numbers(text)
        text = re.sub(r'…+', ' ', text)  # Remove ellipsis
        text = re.sub(r'\.{3,}', ' ', text)
        
        # Content-type specific cleaning
        if content_type == 'academic' or 'slide' in text.lower() or 'lecture' in text.lower():
            text = self.remove_academic_noise(text)
        
        # Detect and remove repeated noise
        noise_lines = self.detect_repeated_noise(text)
        for noise in noise_lines:
            text = text.replace(noise, '')
        
        # Extract meaningful sentences
        sentences = self.extract_meaningful_sentences(text)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_sentences = []
        for sentence in sentences:
            normalized = re.sub(r'\s+', ' ', sentence.lower().strip())
            if normalized not in seen and len(normalized) > 20:
                seen.add(normalized)
                unique_sentences.append(sentence)
        
        # Join back
        cleaned_text = '. '.join(unique_sentences)
        
        # Final cleanup
        cleaned_text = re.sub(r'\s+', ' ', cleaned_text)
        cleaned_text = re.sub(r'\s*\.\s*\.', '.', cleaned_text)
        
        return cleaned_text.strip()