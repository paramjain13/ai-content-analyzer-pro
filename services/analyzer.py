from scraper import scrape_website
from pdf_reader import extract_text_from_pdf
from docx_reader import extract_text_from_docx
from pptx_reader import extract_text_from_pptx
from xlsx_reader import extract_text_from_xlsx
from image_reader import extract_text_from_image
from multi_model_summarizer import summarize_with_model, ModelUnavailable, get_available_models, MODEL_INFO
from summarizer import summarize_text, parse_llm_output
from services.content_analyzer import ContentAnalyzer
from advanced_summarizer import (
    generate_qa_format, 
    generate_timeline_format, 
    generate_key_insights,
    parse_qa_format,
    parse_timeline_format,
    parse_insights_format
)
from document_store import store_document
from chat_service import generate_suggested_questions
from smart_preprocessor import SmartPreprocessor

# Initialize content analyzer
content_analyzer = ContentAnalyzer()

# Initialize smart preprocessor
preprocessor = SmartPreprocessor()

def detect_source_type(file_type="webpage"):
    """Detect source type for better summarization"""
    type_mapping = {
        "webpage": "webpage",
        "pdf": "document",
        "docx": "word document",
        "pptx": "presentation",
        "xlsx": "spreadsheet",
        "image": "image text (OCR)"
    }
    return type_mapping.get(file_type, "document")

def analyze_content(text, title, metadata, source_type, mode, summary_length, summary_format="bullets", model_id="gpt-4o-mini"):
    """
    Common analysis function for all content types
    
    Process:
    1. Clean text with SmartPreprocessor
    2. Analyze content (sentiment, entities, topics, etc.)
    3. Store cleaned text in vector DB for chat (RAG)
    4. Generate summary based on mode and format
    5. Return comprehensive results
    """
    
    print(f"\n{'='*60}")
    print(f"🔬 ANALYZING: {title}")
    print(f"📊 Source: {source_type} | Mode: {mode} | Format: {summary_format} | Model: {model_id}")
    print(f"{'='*60}")
    
    # STEP 1: Smart clean the text BEFORE everything else
    print(f"📝 Original text length: {len(text)} characters")
    cleaned_text = preprocessor.smart_clean(text, source_type)
    print(f"✨ Cleaned text length: {len(cleaned_text)} characters")
    print(f"🧹 Removed {len(text) - len(cleaned_text)} characters of noise")
    
    if len(cleaned_text) < 100:
        return {"error": "After cleaning, insufficient meaningful content found"}
    
    # STEP 2: Analyze content properties (sentiment, entities, etc.)
    print(f"\n🔍 Analyzing content properties...")
    analysis = content_analyzer.analyze_full(cleaned_text)
    print(f"✅ Analysis complete: {analysis.get('sentiment', {}).get('sentiment', 'N/A')} sentiment")
    
    # STEP 3: Store CLEANED document in vector database for chat
    doc_id = None
    suggested_questions = []
    
    try:
        print(f"\n💾 Storing cleaned document in vector database for chat...")
        doc_id = store_document(cleaned_text, title, metadata)
        print(f"✅ Document stored with ID: {doc_id}")
        
        print(f"🤔 Generating suggested questions...")
        suggested_questions = generate_suggested_questions(doc_id, title)
        print(f"✅ Generated {len(suggested_questions)} questions")
        
    except Exception as e:
        print(f"⚠️ Warning: Could not store document for chat: {e}")
        doc_id = None
        suggested_questions = []

    # STEP 4: Generate summary based on mode
    if mode == "nlp":
        # Fast NLP mode - no AI
        print(f"\n⚡ Using NLP mode (no AI)")
        parsed = {
            "executive_summary": [],
            "detailed_summary": [summarize_text(cleaned_text)],
            "confidence_score": "N/A",
            "format": "bullets",
            "model_used": "NLP (Rule-based)"
        }
        method = "NLP Summary (Fast Mode)"
        
    else:
        # AI mode - use selected model and format
        print(f"\n🤖 Using AI mode with {model_id}")
        
        try:
            if summary_format == "qa":
                print(f"📝 Generating Q&A format...")
                raw = generate_qa_format(cleaned_text, detect_source_type(source_type))
                qa_pairs = parse_qa_format(raw)
                parsed = {
                    "executive_summary": [],
                    "qa_format": qa_pairs,
                    "confidence_score": "85%",
                    "format": "qa",
                    "model_used": model_id
                }
                model_name = MODEL_INFO.get(model_id, {}).get("name", model_id)
                method = f"AI Q&A Format - {model_name}"
                print(f"✅ Generated {len(qa_pairs)} Q&A pairs")
                
            elif summary_format == "timeline":
                print(f"📝 Generating Timeline format...")
                raw = generate_timeline_format(cleaned_text, detect_source_type(source_type))
                events = parse_timeline_format(raw)
                parsed = {
                    "executive_summary": [],
                    "timeline": events,
                    "confidence_score": "85%",
                    "format": "timeline",
                    "model_used": model_id
                }
                model_name = MODEL_INFO.get(model_id, {}).get("name", model_id)
                method = f"AI Timeline Format - {model_name}"
                print(f"✅ Generated {len(events)} timeline events")
                
            elif summary_format == "insights":
                print(f"📝 Generating Key Insights format...")
                raw = generate_key_insights(cleaned_text, detect_source_type(source_type))
                insights = parse_insights_format(raw)
                parsed = {
                    "executive_summary": [],
                    "insights": insights,
                    "confidence_score": "85%",
                    "format": "insights",
                    "model_used": model_id
                }
                model_name = MODEL_INFO.get(model_id, {}).get("name", model_id)
                method = f"AI Key Insights - {model_name}"
                print(f"✅ Generated {len(insights)} insights")
                
            else:
                # Bullet points format (default)
                print(f"📝 Generating Bullet Points format...")
                raw = summarize_with_model(
                    cleaned_text, 
                    detect_source_type(source_type), 
                    summary_length, 
                    model_id
                )
                parsed = parse_llm_output(raw)
                parsed["format"] = "bullets"
                parsed["model_used"] = model_id
                
                model_name = MODEL_INFO.get(model_id, {}).get("name", model_id)
                method = f"AI Summary ({summary_length.title()}) - {model_name}"
                print(f"✅ Generated bullet point summary")
                
        except ModelUnavailable as e:
            print(f"⚠️ AI unavailable: {e}")
            print(f"📝 Falling back to NLP mode")
            parsed = {
                "executive_summary": [],
                "detailed_summary": [summarize_text(cleaned_text)],
                "confidence_score": "N/A",
                "format": "bullets",
                "model_used": "NLP (Fallback)"
            }
            method = f"NLP Summary (Fallback - {str(e)})"
            
        except Exception as e:
            print(f"❌ Analysis error: {str(e)}")
            return {"error": f"Analysis failed: {str(e)}"}

    # STEP 5: Combine all results
    result = {
        "title": title,
        "method": method,
        **parsed,
        "analysis": analysis,
        "doc_id": doc_id,
        "suggested_questions": suggested_questions
    }
    
    if metadata:
        result["metadata"] = metadata
    
    print(f"\n✅ Analysis complete!")
    print(f"{'='*60}\n")
    
    return result

def analyze_website(url, mode="llm", summary_length="short", summary_format="bullets", model_id="gpt-4o-mini"):
    """Analyze website content"""
    print(f"\n🌐 Analyzing website: {url}")
    
    data = scrape_website(url)
    if "error" in data:
        return data
    
    return analyze_content(
        data["content"], 
        data["title"], 
        None, 
        "webpage", 
        mode, 
        summary_length,
        summary_format,
        model_id
    )

def analyze_pdf(path, mode="llm", summary_length="short", summary_format="bullets", model_id="gpt-4o-mini"):
    """Analyze PDF document"""
    print(f"\n📄 Analyzing PDF: {path}")
    
    try:
        text, _ = extract_text_from_pdf(path)
    except Exception as e:
        return {"error": f"Failed to read PDF: {str(e)}"}
    
    if not text or len(text.strip()) < 50:
        return {"error": "No readable text found in PDF or content too short"}

    return analyze_content(
        text, 
        "Uploaded PDF Document", 
        None, 
        "pdf", 
        mode, 
        summary_length,
        summary_format,
        model_id
    )

def analyze_docx(path, mode="llm", summary_length="short", summary_format="bullets", model_id="gpt-4o-mini"):
    """Analyze Word document"""
    print(f"\n📝 Analyzing Word document: {path}")
    
    try:
        text, metadata = extract_text_from_docx(path)
    except Exception as e:
        return {"error": str(e)}
    
    if not text or len(text.strip()) < 50:
        return {"error": "No readable text found in Word document or content too short"}

    return analyze_content(
        text, 
        metadata.get("title", "Word Document"), 
        metadata, 
        "docx", 
        mode, 
        summary_length,
        summary_format,
        model_id
    )

def analyze_pptx(path, mode="llm", summary_length="short", summary_format="bullets", model_id="gpt-4o-mini"):
    """Analyze PowerPoint presentation"""
    print(f"\n📊 Analyzing PowerPoint: {path}")
    
    try:
        text, metadata = extract_text_from_pptx(path)
    except Exception as e:
        return {"error": str(e)}
    
    if not text or len(text.strip()) < 50:
        return {"error": "No readable text found in PowerPoint or content too short"}

    return analyze_content(
        text, 
        metadata.get("title", "PowerPoint Presentation"), 
        metadata, 
        "pptx", 
        mode, 
        summary_length,
        summary_format,
        model_id
    )

def analyze_xlsx(path, mode="llm", summary_length="short", summary_format="bullets", model_id="gpt-4o-mini"):
    """Analyze Excel spreadsheet"""
    print(f"\n📈 Analyzing Excel file: {path}")
    
    try:
        text, metadata = extract_text_from_xlsx(path)
    except Exception as e:
        return {"error": str(e)}
    
    if not text or len(text.strip()) < 50:
        return {"error": "No readable data found in Excel file or content too short"}

    return analyze_content(
        text, 
        metadata.get("title", "Excel Spreadsheet"), 
        metadata, 
        "xlsx", 
        mode, 
        summary_length,
        summary_format,
        model_id
    )

def analyze_image(path, mode="llm", summary_length="short", summary_format="bullets", model_id="gpt-4o-mini"):
    """Analyze image using OCR"""
    print(f"\n🖼️ Analyzing image: {path}")
    
    try:
        text, metadata = extract_text_from_image(path)
    except Exception as e:
        return {"error": str(e)}
    
    if not text or len(text.strip()) < 20:
        return {"error": "No readable text found in image or content too short"}

    return analyze_content(
        text, 
        "Image (OCR Extracted Text)", 
        metadata, 
        "image", 
        mode, 
        summary_length,
        summary_format,
        model_id
    )
