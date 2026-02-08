from llm_summarizer import LLMUnavailable
from smart_preprocessor import SmartPreprocessor
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

# OpenAI client
openai_key = os.getenv("OPENAI_API_KEY")
openai_client = OpenAI(api_key=openai_key) if openai_key else None

# Gemini client
try:
    import google.generativeai as genai
    if os.getenv("GOOGLE_API_KEY"):
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        gemini_model = genai.GenerativeModel('gemini-pro')
    else:
        gemini_model = None
except ImportError:
    gemini_model = None

# Initialize smart preprocessor
preprocessor = SmartPreprocessor()

def call_ai_model(prompt, system_prompt, model_preference="openai"):
    """
    Call AI model with fallback support
    Tries OpenAI first, falls back to Gemini if needed
    """
    # Try OpenAI first if available and preferred
    if openai_client and model_preference == "openai":
        try:
            response = openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1000
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            # If OpenAI fails (quota, etc.), fall back to Gemini
            if "429" in str(e) or "quota" in str(e).lower():
                print("OpenAI quota exceeded, falling back to Gemini...")
                if gemini_model:
                    return call_gemini(prompt, system_prompt)
            raise LLMUnavailable(f"Error: {str(e)}")
    
    # Try Gemini if OpenAI not available or preference is Gemini
    if gemini_model:
        return call_gemini(prompt, system_prompt)
    
    # No models available
    raise LLMUnavailable("No AI models available. Please configure API keys.")

def call_gemini(prompt, system_prompt):
    """Call Gemini model"""
    try:
        full_prompt = f"{system_prompt}\n\n{prompt}"
        response = gemini_model.generate_content(
            full_prompt,
            generation_config={
                'temperature': 0.3,
                'max_output_tokens': 1000,
            }
        )
        return response.text.strip()
    except Exception as e:
        raise LLMUnavailable(f"Gemini error: {str(e)}")

def generate_qa_format(text, source_type="document"):
    """
    Generate Q&A format summary with multi-model support
    """
    # Smart clean the text
    text = preprocessor.smart_clean(text, source_type)[:10000]
    
    if len(text) < 100:
        raise LLMUnavailable("Insufficient content")
    
    # Detect content type for better questions
    content_type = preprocessor.detect_content_type(text)
    
    # Content-specific Q&A instructions
    qa_instructions = {
        'academic': "Focus questions on: key concepts, definitions, algorithms, theorems, problem-solving methods, examples, and applications",
        'news': "Focus questions on: main events, key facts, who/what/when/where/why, impact, and future implications",
        'business': "Focus questions on: business decisions, financial metrics, strategy, market conditions, and outcomes",
        'general': "Focus questions on: main topics, key arguments, important facts, conclusions, and practical takeaways"
    }
    
    instruction = qa_instructions.get(content_type, qa_instructions['general'])
    
    prompt = f"""Analyze this {source_type} ({content_type} content) and create an insightful Q&A summary.

INSTRUCTIONS:
- Generate 6-8 important questions that readers would naturally ask
- {instruction}
- Questions should cover main topics and important details
- Answers must be clear, specific, and based ONLY on the content
- Each answer should be 2-4 sentences with concrete details
- IGNORE document formatting, slide numbers, page numbers, dates

FORMAT (STRICT):
Q: [Insightful question about main concept/topic]
A: [Clear, detailed answer with specifics]

Q: [Question about key finding/method]
A: [Comprehensive answer with examples or data]

[Continue for 6-8 Q&As total]

CONTENT TO ANALYZE:
{text}"""
    
    system_prompt = f"You are an expert at creating insightful Q&A summaries for {content_type} content. You ask questions readers want answered and provide clear, specific answers."
    
    return call_ai_model(prompt, system_prompt, "gemini" if gemini_model else "openai")


def generate_timeline_format(text, source_type="document"):
    """
    Generate chronological/timeline format with multi-model support
    """
    # Smart clean the text
    text = preprocessor.smart_clean(text, source_type)[:10000]
    
    if len(text) < 100:
        raise LLMUnavailable("Insufficient content")
    
    # Detect content type
    content_type = preprocessor.detect_content_type(text)
    
    timeline_instructions = {
        'academic': "Create a learning progression showing how concepts build on each other. Use 'Concept 1:', 'Concept 2:', etc.",
        'news': "Create a chronological timeline of events. Include actual dates/times if mentioned.",
        'business': "Show sequence of business developments, decisions, or market events.",
        'general': "Show logical progression or sequence of main points discussed."
    }
    
    instruction = timeline_instructions.get(content_type, timeline_instructions['general'])
    
    prompt = f"""Analyze this {source_type} and create a chronological timeline or logical sequence.

INSTRUCTIONS:
- Identify 6-9 key events, steps, concepts, or developments
- {instruction}
- Present in chronological or logical order
- Each entry should be substantial and informative
- IGNORE slide numbers, page numbers, repeated headers

FORMAT:
[Date/Time/Step/Concept 1]: Clear description of the key point

[Date/Time/Step/Concept 2]: Description with relevant details

[Continue for 6-9 entries]

CONTENT TO ANALYZE:
{text}"""
    
    system_prompt = "You create clear chronological timelines and logical sequences. You identify natural flow and progression of content."
    
    return call_ai_model(prompt, system_prompt, "gemini" if gemini_model else "openai")


def generate_key_insights(text, source_type="document"):
    """
    Generate key insights format with multi-model support
    """
    # Smart clean the text
    text = preprocessor.smart_clean(text, source_type)[:10000]
    
    if len(text) < 100:
        raise LLMUnavailable("Insufficient content")
    
    # Detect content type
    content_type = preprocessor.detect_content_type(text)
    
    insights_instructions = {
        'academic': "Extract key learnings, important concepts to understand, critical algorithms or methods, and practical applications",
        'news': "Extract significance of events, implications, impact on stakeholders, and what this means for the future",
        'business': "Extract strategic insights, market implications, competitive advantages, risks, and opportunities",
        'general': "Extract main takeaways, important lessons, actionable insights, and key understanding"
    }
    
    instruction = insights_instructions.get(content_type, insights_instructions['general'])
    
    prompt = f"""Extract the most valuable insights from this {source_type}.

INSTRUCTIONS:
- Identify 6-9 CRITICAL INSIGHTS - the most important takeaways
- {instruction}
- Each insight should be substantial and meaningful
- Focus on "SO WHAT?" - why does this matter?
- Include specific details that make insights concrete
- IGNORE document structure, focus on MEANING

FORMAT:
💡 Insight 1: [Meaningful, specific insight with context]

💡 Insight 2: [Important takeaway with details]

[Continue for 6-9 insights]

CONTENT TO ANALYZE:
{text}"""
    
    system_prompt = f"You extract meaningful insights from {content_type} content. You identify what truly matters and communicate it clearly."
    
    return call_ai_model(prompt, system_prompt, "gemini" if gemini_model else "openai")


def parse_qa_format(raw_text):
    """Parse Q&A format into structured data"""
    qa_pairs = []
    lines = raw_text.split('\n')
    
    current_q = None
    current_a = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        if line.startswith('Q:'):
            if current_q:
                qa_pairs.append({
                    "question": current_q,
                    "answer": ' '.join(current_a)
                })
            current_q = line[2:].strip()
            current_a = []
        elif line.startswith('A:'):
            current_a.append(line[2:].strip())
        elif current_q:
            current_a.append(line)
    
    if current_q:
        qa_pairs.append({
            "question": current_q,
            "answer": ' '.join(current_a)
        })
    
    return qa_pairs


def parse_timeline_format(raw_text):
    """Parse timeline format into structured data"""
    events = []
    lines = raw_text.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line or line.startswith('[Continue') or line.startswith('If no') or line.startswith('FORMAT'):
            continue
        
        if ':' in line:
            parts = line.split(':', 1)
            if len(parts) == 2:
                timestamp = parts[0].strip().strip('[]')
                description = parts[1].strip()
                
                if description and len(description) > 15:
                    events.append({
                        "timestamp": timestamp,
                        "description": description
                    })
    
    return events


def parse_insights_format(raw_text):
    """Parse insights format into structured data"""
    insights = []
    lines = raw_text.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Remove emoji and insight markers
        line = line.replace('💡', '').strip()
        
        if line.startswith('Insight'):
            if ':' in line:
                insight_text = line.split(':', 1)[1].strip()
                if insight_text and len(insight_text) > 15:
                    insights.append(insight_text)
        elif line and not line.startswith('[') and not line.startswith('FORMAT') and not line.startswith('INSTRUCTIONS') and len(line) > 20:
            insights.append(line)
    
    return insights