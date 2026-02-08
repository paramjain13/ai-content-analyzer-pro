import re
import requests
import xml.etree.ElementTree as ET

def extract_video_id(url):
    """Extract YouTube video ID from URL"""
    patterns = [
        r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
        r'youtu\.be\/([0-9A-Za-z_-]{11})',
        r'embed\/([0-9A-Za-z_-]{11})'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    return None

def clean_html_entities(text):
    """Clean HTML entities from text"""
    replacements = {
        '&amp;': '&',
        '&lt;': '<',
        '&gt;': '>',
        '&#39;': "'",
        '&quot;': '"',
        '&nbsp;': ' ',
        '\n': ' '
    }
    
    for old, new in replacements.items():
        text = text.replace(old, new)
    
    return text

def extract_transcript_from_youtube(url):
    """
    Extract transcript from YouTube using YouTube's timedtext API
    This method doesn't require youtube-transcript-api library
    """
    try:
        # Extract video ID
        video_id = extract_video_id(url)
        
        if not video_id:
            raise Exception(
                "Invalid YouTube URL. Please use format: "
                "https://www.youtube.com/watch?v=VIDEO_ID or "
                "https://youtu.be/VIDEO_ID"
            )
        
        # Try to get English captions from YouTube's API
        caption_urls = [
            f"https://www.youtube.com/api/timedtext?v={video_id}&lang=en",
            f"https://www.youtube.com/api/timedtext?v={video_id}&lang=en-US",
            f"https://www.youtube.com/api/timedtext?v={video_id}&lang=en-GB",
        ]
        
        transcript_text = None
        text_parts = []
        
        for api_url in caption_urls:
            try:
                response = requests.get(api_url, timeout=10)
                
                if response.status_code == 200 and response.content:
                    # Parse XML response
                    try:
                        root = ET.fromstring(response.content)
                        
                        # Extract text from all <text> elements
                        for text_elem in root.findall('.//text'):
                            if text_elem.text:
                                cleaned_text = clean_html_entities(text_elem.text)
                                text_parts.append(cleaned_text.strip())
                        
                        if text_parts:
                            transcript_text = ' '.join(text_parts)
                            break
                            
                    except ET.ParseError:
                        continue
                        
            except requests.exceptions.RequestException:
                continue
        
        # If no English captions found, try auto-generated
        if not transcript_text:
            try:
                auto_url = f"https://www.youtube.com/api/timedtext?v={video_id}&lang=en&kind=asr"
                response = requests.get(auto_url, timeout=10)
                
                if response.status_code == 200 and response.content:
                    root = ET.fromstring(response.content)
                    text_parts = []
                    
                    for text_elem in root.findall('.//text'):
                        if text_elem.text:
                            cleaned_text = clean_html_entities(text_elem.text)
                            text_parts.append(cleaned_text.strip())
                    
                    if text_parts:
                        transcript_text = ' '.join(text_parts)
                        
            except Exception:
                pass
        
        # Check if we got any transcript
        if not transcript_text or not text_parts:
            raise Exception(
                "No captions/subtitles found for this video. "
                "Please try a video with captions enabled."
            )
        
        # Clean up the transcript
        transcript_text = re.sub(r'\s+', ' ', transcript_text).strip()
        transcript_text = re.sub(r'\[.*?\]', '', transcript_text)  # Remove [Music], etc.
        transcript_text = re.sub(r'\(.*?\)', '', transcript_text)  # Remove (sounds), etc.
        
        if len(transcript_text) < 50:
            raise Exception(
                "Transcript is too short. The video might not have proper captions."
            )
        
        # Create metadata
        metadata = {
            "video_id": video_id,
            "url": f"https://www.youtube.com/watch?v={video_id}",
            "duration": "Unknown",
            "segments": len(text_parts),
            "word_count": len(transcript_text.split()),
            "caption_type": "Available"
        }
        
        return transcript_text, metadata
        
    except requests.exceptions.Timeout:
        raise Exception("Request timed out while fetching YouTube captions.")
    
    except requests.exceptions.RequestException as e:
        raise Exception(f"Network error while fetching captions: {str(e)}")
    
    except Exception as e:
        error_msg = str(e)
        
        # Pass through our custom error messages
        if any(phrase in error_msg for phrase in [
            "Invalid YouTube URL",
            "No captions/subtitles found",
            "Transcript is too short",
            "Request timed out"
        ]):
            raise Exception(error_msg)
        else:
            raise Exception(f"Error extracting YouTube transcript: {error_msg}")