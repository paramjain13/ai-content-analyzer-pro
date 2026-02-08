import requests
from bs4 import BeautifulSoup
import re

def scrape_website(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, timeout=10, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, "html.parser")

        # Extract title
        title = soup.title.text.strip() if soup.title else "Website"
        
        # Remove unwanted elements that add noise
        for element in soup(['script', 'style', 'nav', 'header', 'footer', 
                            'aside', 'iframe', 'noscript', 'form']):
            element.decompose()
        
        # Try to find main content area first
        main_content = None
        
        # Look for common main content containers
        main_selectors = [
            'main',
            'article',
            '[role="main"]',
            '.main-content',
            '.content',
            '#main',
            '#content',
            '.article-content',
            '.post-content'
        ]
        
        for selector in main_selectors:
            main_content = soup.select_one(selector)
            if main_content:
                break
        
        # If no main content area found, use body
        if not main_content:
            main_content = soup.find("body")
        
        if not main_content:
            return {"error": "Could not extract content from webpage"}
        
        # Extract text from paragraphs and headings for better structure
        content_parts = []
        
        # Get headings and paragraphs in order
        for element in main_content.find_all(['h1', 'h2', 'h3', 'p', 'li']):
            text = element.get_text(strip=True)
            if text and len(text) > 20:  # Filter out very short snippets
                content_parts.append(text)
        
        content = " ".join(content_parts)
        
        # Clean up the content
        content = re.sub(r'\s+', ' ', content)  # Normalize whitespace
        content = re.sub(r'\.{2,}', '.', content)  # Remove multiple dots
        
        # Remove common footer/boilerplate patterns
        boilerplate_patterns = [
            r'All rights reserved.*',
            r'Copyright \d{4}.*',
            r'Terms and Conditions.*',
            r'Privacy Policy.*',
            r'Cookie Settings.*'
        ]
        
        for pattern in boilerplate_patterns:
            content = re.sub(pattern, '', content, flags=re.IGNORECASE)
        
        content = content.strip()
        
        if not content or len(content) < 100:
            return {"error": "Insufficient meaningful content found on the webpage"}

        return {"title": title, "content": content}
    
    except requests.exceptions.Timeout:
        return {"error": "Request timed out. The website took too long to respond"}
    except requests.exceptions.ConnectionError:
        return {"error": "Failed to connect to the website. Please check the URL"}
    except requests.exceptions.HTTPError as e:
        return {"error": f"HTTP error occurred: {e.response.status_code}"}
    except requests.exceptions.RequestException as e:
        return {"error": f"Failed to fetch website: {str(e)}"}
    except Exception as e:
        return {"error": f"An error occurred while processing the website: {str(e)}"}