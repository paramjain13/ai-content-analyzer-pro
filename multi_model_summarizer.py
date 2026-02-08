import os
from dotenv import load_dotenv
from openai import OpenAI, RateLimitError
from smart_preprocessor import SmartPreprocessor

load_dotenv()

# Initialize clients
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY")) if os.getenv("OPENAI_API_KEY") else None

try:
    import google.generativeai as genai
    if os.getenv("GOOGLE_API_KEY"):
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        gemini_model = genai.GenerativeModel('gemini-pro')
    else:
        gemini_model = None
except ImportError:
    gemini_model = None
    print("Google Generative AI not installed. Run: pip install google-generativeai")

# Initialize smart preprocessor
preprocessor = SmartPreprocessor()

class ModelUnavailable(Exception):
    pass

# Model info
MODEL_INFO = {
    "gpt-4o-mini": {
        "name": "GPT-4o Mini",
        "provider": "OpenAI",
        "speed": "⚡ Very Fast",
        "quality": "Good",
        "cost": "💰 Low"
    },
    "gpt-4o": {
        "name": "GPT-4o",
        "provider": "OpenAI",
        "speed": "⚡ Fast",
        "quality": "⭐ Excellent",
        "cost": "💰 Medium"
    },
    "gemini-pro": {
        "name": "Gemini 1.5 Pro",
        "provider": "Google",
        "speed": "⚡ Fast",
        "quality": "⭐ Excellent",
        "cost": "💰 Free Tier"
    }
}

def get_available_models():
    """Return list of available models"""
    models = []
    
    if openai_client:
        models.append({"id": "gpt-4o-mini", **MODEL_INFO["gpt-4o-mini"]})
        models.append({"id": "gpt-4o", **MODEL_INFO["gpt-4o"]})
    
    if gemini_model:
        models.append({"id": "gemini-pro", **MODEL_INFO["gemini-pro"]})
    
    return models

def build_enhanced_prompt(text, source_type, summary_length, content_type='general'):
    """Build enhanced prompt with content-type awareness"""
    
    if summary_length == "short":
        exec_bullets = "2-3"
        detail_bullets = "5-7"
    else:
        exec_bullets = "3-4"
        detail_bullets = "10-15"
    
    # Content-specific instructions
    type_instructions = {
        'academic': """
ACADEMIC CONTENT - FOCUS ON:
✓ Main concepts, theories, algorithms, or principles explained
✓ Key definitions and their meanings
✓ Theorems, formulas, or laws discussed (describe conceptually)
✓ Problem-solving methods, techniques, or approaches
✓ Examples used to illustrate concepts
✓ Relationships and connections between ideas
✓ Applications, implications, or use cases

IGNORE: Slide numbers, lecture numbers, page numbers, course codes, dates, repeated headers""",
        
        'news': """
NEWS CONTENT - FOCUS ON:
✓ Main event or development (Who, What, When, Where, Why, How)
✓ Key facts and verified information
✓ Important statements or announcements (paraphrase)
✓ Context, background, and significance
✓ Impact, consequences, and implications
✓ Different perspectives or reactions mentioned
✓ Future outlook or next developments

IGNORE: Bylines, publication dates, navigation elements, related articles""",
        
        'business': """
BUSINESS CONTENT - FOCUS ON:
✓ Main business development, announcement, or decision
✓ Financial metrics: revenue, profit, growth percentages
✓ Strategic moves, changes, or initiatives
✓ Market conditions, trends, and analysis
✓ Competitive landscape and positioning
✓ Leadership actions, statements, or changes
✓ Future plans, projections, or guidance

IGNORE: Stock symbols, timestamps, disclaimers, boilerplate language""",
        
        'general': """
GENERAL CONTENT - FOCUS ON:
✓ Main topic, theme, or central message
✓ Key arguments, claims, or positions
✓ Supporting evidence, examples, and data
✓ Important facts and information
✓ Conclusions, recommendations, or takeaways
✓ Practical implications or applications

IGNORE: Document metadata, formatting elements, navigation"""
    }
    
    instructions = type_instructions.get(content_type, type_instructions['general'])
    
    prompt = f"""You are analyzing a {source_type}. Content type: {content_type.upper()}.

{instructions}

YOUR MISSION:
Extract the ESSENCE and SUBSTANCE. What does this content actually TEACH, EXPLAIN, or COMMUNICATE?

QUALITY CRITERIA:
✓ SPECIFIC - Names, numbers, technical terms, concrete examples
✓ ACCURATE - Only what's actually in the content
✓ COHERENT - Each point is clear and complete
✓ MEANINGFUL - Real insights, not superficial observations
✓ SYNTHESIZED - Combine related ideas logically

OUTPUT FORMAT (STRICT):

Executive Summary:
- [What is this fundamentally about? The core message or main topic]
- [Most critical supporting point, finding, or key concept]
{"- [Third essential point or major insight]" if summary_length == "long" else ""}

Detailed Summary:
- [First major topic/concept with specific details, examples, or data]
- [Second major topic with concrete information and context]
- [Third important aspect with specifics and explanation]
- [Fourth key point with details and relevance]
{"- [Fifth point with context and examples]" if summary_length == "long" else ""}
{"- [Sixth significant point]" if summary_length == "long" else ""}
{"- [Seventh point if relevant]" if summary_length == "long" else ""}
{"- [Additional insights, methods, findings, or applications]" if summary_length == "long" else ""}

Confidence Score:
[Single number 60-100 reflecting content clarity and your confidence]

CONTENT TO ANALYZE:
{text}"""

    return prompt

def summarize_with_gpt(text, source_type, summary_length, model="gpt-4o-mini"):
    """Enhanced GPT summarization with smart preprocessing"""
    if not openai_client:
        raise ModelUnavailable("OpenAI API key not configured")
    
    # Smart preprocessing
    cleaned_text = preprocessor.smart_clean(text, source_type)
    
    # Keep more text for better context
    cleaned_text = cleaned_text[:12000]
    
    if len(cleaned_text) < 100:
        raise ModelUnavailable("Insufficient meaningful content after cleaning")
    
    # Detect content type for intelligent prompting
    content_type = preprocessor.detect_content_type(cleaned_text)
    
    # Build enhanced prompt
    prompt = build_enhanced_prompt(cleaned_text, source_type, summary_length, content_type)
    
    try:
        response = openai_client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": f"""You are an elite content analyst specializing in {content_type} material.

Your expertise:
- Extracting substance from noisy documents
- Understanding technical and academic concepts
- Identifying what truly matters vs. formatting artifacts
- Synthesizing complex information clearly
- Creating insights, not just descriptions

Your methodology:
- Read for deep understanding
- Ignore document structure noise
- Focus on concepts, facts, arguments
- Provide specific, accurate details
- Synthesize related ideas coherently

You excel at summarizing:
- Academic papers and lecture materials
- Technical documentation
- News articles and reports  
- Business documents and analyses
- Research findings and studies"""
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=1200 if summary_length == "long" else 600,
            presence_penalty=0.1,  # Encourage covering different aspects
            frequency_penalty=0.1   # Reduce repetition
        )
        return response.choices[0].message.content.strip()
    except RateLimitError:
        raise ModelUnavailable("OpenAI rate limit reached")
    except Exception as e:
        raise ModelUnavailable(f"OpenAI API error: {str(e)}")

def summarize_with_gemini(text, source_type, summary_length):
    """Enhanced Gemini summarization with smart preprocessing"""
    if not gemini_model:
        raise ModelUnavailable("Gemini API key not configured")
    
    # Smart preprocessing
    cleaned_text = preprocessor.smart_clean(text, source_type)
    cleaned_text = cleaned_text[:12000]
    
    if len(cleaned_text) < 100:
        raise ModelUnavailable("Insufficient meaningful content after cleaning")
    
    # Detect content type
    content_type = preprocessor.detect_content_type(cleaned_text)
    
    # Build enhanced prompt
    prompt = build_enhanced_prompt(cleaned_text, source_type, summary_length, content_type)
    
    # Add system instruction for Gemini
    full_prompt = f"""You are an expert analyst for {content_type} content. Extract substance, ignore formatting.

{prompt}"""
    
    try:
        response = gemini_model.generate_content(
            full_prompt,
            generation_config={
                'temperature': 0.3,
                'max_output_tokens': 1200 if summary_length == "long" else 600,
                'top_p': 0.8,
                'top_k': 40
            }
        )
        return response.text.strip()
    except Exception as e:
        raise ModelUnavailable(f"Gemini API error: {str(e)}")

def summarize_with_model(text, source_type, summary_length, model_id="gpt-4o-mini"):
    """
    Universal enhanced summarization function
    
    Args:
        text: Content to summarize
        source_type: Type of source (webpage, document, etc.)
        summary_length: "short" or "long"
        model_id: Model identifier (gpt-4o-mini, gpt-4o, gemini-pro)
    
    Returns:
        Formatted summary text with improved quality
    """
    if model_id in ["gpt-4o", "gpt-4o-mini"]:
        return summarize_with_gpt(text, source_type, summary_length, model_id)
    elif model_id == "gemini-pro":
        return summarize_with_gemini(text, source_type, summary_length)
    else:
        raise ModelUnavailable(f"Unknown model: {model_id}")