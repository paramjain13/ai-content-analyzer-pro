import os
from dotenv import load_dotenv
from openai import OpenAI, RateLimitError

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key) if api_key else None

class LLMUnavailable(Exception):
    pass

def preprocess_text(text):
    """Clean and prepare text for better summarization"""
    # Remove excessive whitespace
    text = ' '.join(text.split())
    
    # Remove common noise patterns
    noise_patterns = [
        r'Cookie Policy.*?(?=\.|$)',
        r'Privacy Policy.*?(?=\.|$)',
        r'Terms of Service.*?(?=\.|$)',
        r'Subscribe to our newsletter.*?(?=\.|$)',
        r'Follow us on.*?(?=\.|$)',
        r'All rights reserved.*?(?=\.|$)',
        r'Copyright \d{4}.*?(?=\.|$)',
    ]
    
    import re
    for pattern in noise_patterns:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE)
    
    return text.strip()

def summarize_with_llm(text, source_type, summary_length="short"):
    """
    Summarize text using OpenAI LLM with improved prompt for academic/technical content
    """
    if not client:
        raise LLMUnavailable()

    # Preprocess and limit text (increased from 8000 to 10000)
    text = preprocess_text(text)[:10000]
    
    if len(text) < 100:
        raise LLMUnavailable("Insufficient content to summarize")

    # Adjust bullet count based on summary length
    if summary_length == "short":
        exec_bullets = "2-3"
        detail_bullets = "4-6"
    else:
        exec_bullets = "3-4"
        detail_bullets = "8-12"

    # Enhanced prompt for better content extraction
    prompt = f"""You are analyzing a {source_type}. Provide an accurate, focused summary.

CRITICAL INSTRUCTIONS:
1. IGNORE: slide numbers, page numbers, dates, course codes, repeated headers/footers, navigation elements
2. FOCUS ON: the actual content, main concepts, key ideas, important facts, data, arguments
3. For academic/technical content: extract key concepts, algorithms, theorems, methods, findings
4. For articles/reports: extract main argument, evidence, conclusions, recommendations
5. Be SPECIFIC: include names, numbers, technical terms, specific examples when mentioned
6. SKIP: meta-information like "Class objectives", "Reading assignment", "Table of contents"

WHAT MAKES A GOOD SUMMARY:
- Captures the SUBSTANCE of what's being communicated
- Focuses on WHAT rather than document structure
- Includes specific facts, data, names, concepts
- Ignores formatting artifacts and boilerplate

OUTPUT FORMAT (MUST FOLLOW EXACTLY):

Executive Summary:
- [Main topic/concept/argument - what is this really about?]
- [Second most critical point or finding]
{f"- [Third important point if relevant]" if summary_length == "long" else ""}

Detailed Summary:
- [First major concept/topic with specific details, examples, or data]
- [Second major concept/topic with specifics]
- [Third major concept/topic with specifics]
- [Fourth important point with details]
{"- [Fifth point with specifics]" if summary_length == "long" else ""}
{"- [Additional relevant concepts, methods, findings, or examples]" if summary_length == "long" else ""}
{"- [Conclusions, recommendations, or implications if mentioned]" if summary_length == "long" else ""}

Confidence Score:
[A single number between 60-100 based on content clarity and completeness]

SOURCE TYPE: {source_type.upper()}

CONTENT TO ANALYZE:
{text}

Remember: Extract MEANING and SUBSTANCE. Ignore document formatting and metadata."""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system", 
                    "content": """You are an expert content analyst and technical summarizer. 

Your strengths:
- Distinguishing content from formatting/metadata
- Extracting key concepts from academic and technical material
- Identifying main arguments in articles and reports
- Focusing on substance over form
- Creating accurate, meaningful summaries

You ALWAYS ignore:
- Slide numbers, page numbers, dates
- Repeated headers and footers
- Navigation elements and boilerplate
- Document structure metadata

You ALWAYS focus on:
- Key concepts, theories, algorithms
- Main arguments and evidence
- Specific facts, data, and examples
- Technical details and methods
- Conclusions and implications"""
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=1000 if summary_length == "long" else 500
        )
        return response.choices[0].message.content.strip()
    except RateLimitError:
        raise LLMUnavailable("OpenAI rate limit reached")
    except Exception as e:
        raise LLMUnavailable(f"OpenAI API error: {str(e)}")