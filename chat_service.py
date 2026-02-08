from openai import OpenAI
from dotenv import load_dotenv
import os
from document_store import search_documents
import re

load_dotenv()

# Initialize OpenAI client
openai_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=openai_key) if openai_key else None

# Initialize Gemini client
try:
    import google.generativeai as genai
    if os.getenv("GOOGLE_API_KEY"):
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        gemini_model = genai.GenerativeModel('gemini-pro')
    else:
        gemini_model = None
except ImportError:
    gemini_model = None
    print("Google Generative AI not installed. Install with: pip install google-generativeai")

def clean_chunk_text(text):
    """
    Clean chunk text by removing common noise patterns
    """
    # Remove dates
    text = re.sub(
        r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+\d{4}\b',
        '', text, flags=re.IGNORECASE
    )
    
    # Remove course codes (CS5800, MATH101, etc.)
    text = re.sub(r'\b[A-Z]{2,4}\s*\d{3,5}\b', '', text, flags=re.IGNORECASE)
    
    # Remove semester info
    text = re.sub(r'\b(?:Fall|Spring|Summer|Winter)\s+\d{4}\b', '', text, flags=re.IGNORECASE)
    
    # Remove slide/page numbers
    text = re.sub(r'^\s*\d+\s*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'\n\s*\d+\s*\n', '\n', text)
    text = re.sub(r'\bSlide\s+\d+\b', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\bPage\s+\d+\b', '', text, flags=re.IGNORECASE)
    
    # Remove ellipsis
    text = re.sub(r'…+', ' ', text)
    text = re.sub(r'\.{3,}', ' ', text)
    
    # Remove common academic headers
    text = re.sub(r'(?:Class|Reading|Lecture)\s+(?:objectives|assignment|notes).*?(?:\n|$)', '', text, flags=re.IGNORECASE)
    
    # Remove repeated dashes and underscores
    text = re.sub(r'[-_]{3,}', '', text)
    
    # Clean whitespace
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)  # Max 2 newlines
    
    return text.strip()

def simple_keyword_search(question, doc_id):
    """
    Simple keyword-based search fallback (no AI needed)
    """
    try:
        relevant_chunks = search_documents(question, doc_id=doc_id, top_k=2)
        
        if not relevant_chunks:
            return {
                "answer": "I couldn't find relevant information in the document to answer your question.",
                "sources": [],
                "error": None
            }
        
        # Clean and combine chunks
        combined_parts = []
        for chunk in relevant_chunks:
            cleaned = clean_chunk_text(chunk['text'])
            if len(cleaned) > 30:
                combined_parts.append(cleaned)
        
        combined_text = "\n\n".join(combined_parts)
        
        if len(combined_text) < 50:
            answer = "I found some content but couldn't extract clear information to answer your question."
        else:
            answer = f"Based on the document:\n\n{combined_text[:800]}..."
        
        return {
            "answer": answer,
            "sources": [
                {
                    "text": clean_chunk_text(chunk['text'])[:200] + "...",
                    "chunk_index": chunk['metadata'].get('child_index', 0),
                    "section": chunk.get('section', 'Unknown')
                }
                for chunk in relevant_chunks
            ],
            "error": None
        }
        
    except Exception as e:
        return {
            "answer": None,
            "sources": [],
            "error": f"Search error: {str(e)}"
        }

def chat_with_gemini(context, question, conversation_history, sections_info):
    """
    Chat using Gemini with enhanced context
    """
    # Build conversation context
    conversation_context = ""
    if conversation_history:
        for msg in conversation_history[-4:]:  # Last 2 exchanges
            role = msg.get('role', '')
            content = msg.get('content', '')
            if role == 'user':
                conversation_context += f"\nPrevious Question: {content}\n"
            elif role == 'assistant':
                conversation_context += f"Previous Answer: {content}\n"
    
    # Build section context
    section_list = ", ".join(sections_info) if sections_info else "document"
    
    full_prompt = f"""You are an expert tutor helping someone understand a document.

CONTEXT: The following excerpts come from: {section_list}

YOUR TASK: Answer the question using ONLY the information in these excerpts.

INSTRUCTIONS:
- Provide a comprehensive, educational answer
- Ignore formatting artifacts (slide numbers, dates, course codes)
- Focus on explaining concepts clearly and thoroughly
- Use examples from the excerpts when available
- Structure your answer logically (use bullet points or numbered lists for complex topics)
- If the excerpts discuss multiple aspects, cover all of them
- Be specific and include details from the excerpts

{conversation_context}

DOCUMENT EXCERPTS:
{context}

CURRENT QUESTION: {question}

Please provide a detailed, well-structured answer:"""
    
    try:
        response = gemini_model.generate_content(
            full_prompt,
            generation_config={
                'temperature': 0.3,
                'max_output_tokens': 1200,  # Longer answers
                'top_p': 0.95,
            }
        )
        
        return response.text.strip()
    except Exception as e:
        raise Exception(f"Gemini error: {str(e)}")

def chat_with_openai(context, question, conversation_history, sections_info):
    """
    Chat using OpenAI with enhanced context
    """
    section_list = ", ".join(sections_info) if sections_info else "document"
    
    messages = [
        {
            "role": "system",
            "content": f"""You are an expert tutor providing comprehensive answers based on document excerpts.

CONTEXT: You have access to excerpts from: {section_list}

YOUR EXPERTISE:
- Deep understanding of complex topics
- Clear, educational explanations
- Logical structuring of information
- Using examples to illustrate concepts
- Focusing on substance over formatting

YOUR APPROACH:
- Extract ALL relevant information from excerpts
- Synthesize into coherent, complete explanation
- Use specific details and examples
- Structure complex answers with bullet points or steps
- IGNORE: slide numbers, dates, course codes, formatting noise
- FOCUS ON: concepts, explanations, facts, relationships

ANSWER QUALITY:
- Comprehensive (cover all aspects)
- Specific (include details from excerpts)
- Clear (easy to understand)
- Structured (organized logically)
- Educational (help user truly understand)"""
        }
    ]
    
    if conversation_history:
        messages.extend(conversation_history[-6:])
    
    messages.append({
        "role": "user",
        "content": f"""Document Excerpts:
{context}

Question: {question}

Provide a detailed, well-structured answer based on the excerpts:"""
    })
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.3,
        max_tokens=1200
    )
    
    return response.choices[0].message.content.strip()

def chat_with_document(question, doc_id, conversation_history=None):
    """
    Enhanced chat with document using parent-child RAG
    
    Process:
    1. Search child chunks (precise matching)
    2. Retrieve parent chunks (full context)
    3. Clean and prepare context
    4. Send to AI (Gemini preferred, OpenAI fallback)
    5. Return comprehensive answer with sources
    """
    
    try:
        # STEP 1: Search for relevant chunks (returns parent chunks based on child matches)
        relevant_chunks = search_documents(question, doc_id=doc_id, top_k=3)  # 3 parents = rich context
        
        if not relevant_chunks:
            return {
                "answer": "I couldn't find any relevant information in the document to answer your question.",
                "sources": [],
                "error": None
            }
        
        # STEP 2: Build context from PARENT chunks (comprehensive context)
        context_parts = []
        sections_info = []
        
        for i, chunk in enumerate(relevant_chunks):
            # Get parent text (full context)
            parent_text = chunk.get('text', '')
            section = chunk.get('section', f"Section {i+1}")
            
            # Clean the parent text
            cleaned_parent = clean_chunk_text(parent_text)
            
            if len(cleaned_parent) > 50:
                sections_info.append(section)
                context_parts.append(f"[Excerpt {i+1} - {section}]:\n{cleaned_parent}")
        
        if not context_parts:
            return {
                "answer": "The document excerpts don't contain clear information to answer this question.",
                "sources": [],
                "error": None
            }
        
        context = "\n\n".join(context_parts)
        
        # STEP 3: Generate answer using best available AI
        answer = None
        
        # Try Gemini first (you have free tier + it's good)
        if gemini_model:
            try:
                answer = chat_with_gemini(context, question, conversation_history, sections_info)
            except Exception as e:
                print(f"Gemini failed: {e}, trying OpenAI...")
                # Fall through to OpenAI
        
        # Try OpenAI if Gemini failed or unavailable
        if not answer and client:
            try:
                answer = chat_with_openai(context, question, conversation_history, sections_info)
            except Exception as e:
                error_str = str(e)
                # If quota error and no Gemini, inform user
                if "429" in error_str or "quota" in error_str.lower():
                    if not gemini_model:
                        return {
                            "answer": "OpenAI quota exceeded. Please add credits or configure Gemini API key as backup.",
                            "sources": [],
                            "error": None
                        }
                raise
        
        # If still no answer, use simple search
        if not answer:
            return simple_keyword_search(question, doc_id)
        
        # STEP 4: Return answer with sources
        return {
            "answer": answer,
            "sources": [
                {
                    "text": clean_chunk_text(chunk.get('child_text', chunk['text']))[:250] + "...",
                    "chunk_index": chunk['metadata'].get('child_index', 0),
                    "section": chunk.get('section', 'Unknown Section')
                }
                for chunk in relevant_chunks
            ],
            "error": None
        }
            
    except Exception as e:
        return {
            "answer": None,
            "sources": [],
            "error": f"Error processing question: {str(e)}"
        }

def generate_suggested_questions(doc_id, title):
    """
    Generate suggested questions based on document content
    Uses parent-child chunks for better question generation
    """
    default_questions = [
        "What is this document about?",
        "What are the main concepts explained?",
        "Can you summarize the key points?",
        "What are the important takeaways?"
    ]
    
    try:
        # Get sample chunks (now returns parents with richer content)
        collection_sample = search_documents("main concepts key topics overview", doc_id=doc_id, top_k=2)
        
        if not collection_sample:
            return default_questions
        
        # Clean sample text from parent chunks
        sample_texts = []
        for chunk in collection_sample:
            cleaned = clean_chunk_text(chunk['text'])
            if len(cleaned) > 100:  # Ensure meaningful content
                sample_texts.append(cleaned)
        
        if not sample_texts:
            return default_questions
        
        sample_text = "\n\n".join(sample_texts)[:3000]  # More context for better questions
        
        if len(sample_text) < 100:
            return default_questions
        
        prompt = f"""Based on this document titled "{title}", suggest 4 specific, insightful questions someone studying this material would ask.

Document excerpts:
{sample_text}

INSTRUCTIONS:
- Generate questions about KEY CONCEPTS and MAIN IDEAS
- Make questions specific to this content (not generic)
- Focus on understanding and learning
- Questions should be clear and direct
- Cover different aspects of the content

FORMAT: One question per line, no numbering or bullets.

Generate 4 questions:"""
        
        # Try Gemini first (free tier)
        if gemini_model:
            try:
                response = gemini_model.generate_content(
                    prompt,
                    generation_config={
                        'temperature': 0.7,
                        'max_output_tokens': 250,
                    }
                )
                
                questions = [q.strip() for q in response.text.strip().split('\n') if q.strip()]
                
                # Clean and filter questions
                good_questions = []
                for q in questions:
                    # Remove numbering if present
                    q = re.sub(r'^\d+[\.\)]\s*', '', q)
                    q = re.sub(r'^[-•]\s*', '', q)
                    q = q.strip()
                    
                    # Keep if good quality
                    if len(q) > 20 and len(q) < 150 and '?' in q:
                        good_questions.append(q)
                
                if len(good_questions) >= 3:
                    return good_questions[:4]
                    
            except Exception as e:
                print(f"Gemini question generation failed: {e}")
                # Fall through to OpenAI
        
        # Try OpenAI if Gemini failed or unavailable
        if client:
            try:
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {
                            "role": "system", 
                            "content": "You generate specific, insightful questions that help people understand document content."
                        },
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=250
                )
                
                questions = [q.strip() for q in response.choices[0].message.content.strip().split('\n') if q.strip()]
                
                # Clean and filter
                good_questions = []
                for q in questions:
                    q = re.sub(r'^\d+[\.\)]\s*', '', q)
                    q = re.sub(r'^[-•]\s*', '', q)
                    q = q.strip()
                    
                    if len(q) > 20 and len(q) < 150 and '?' in q:
                        good_questions.append(q)
                
                if len(good_questions) >= 3:
                    return good_questions[:4]
                    
            except Exception as e:
                print(f"OpenAI question generation failed: {e}")
        
        return default_questions
        
    except Exception as e:
        print(f"Question generation error: {e}")
        return default_questions