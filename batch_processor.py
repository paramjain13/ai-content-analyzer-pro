from services.analyzer import (
    analyze_website, analyze_pdf, analyze_docx,
    analyze_pptx, analyze_xlsx, analyze_image
)
from export_service import export_to_pdf, export_to_docx, export_to_markdown, export_to_json
import os
from werkzeug.utils import secure_filename
import zipfile
import io

def get_file_type(filename):
    """Determine file type from extension"""
    ext = filename.rsplit(".", 1)[1].lower() if "." in filename else ""
    
    if ext in ["docx", "doc"]:
        return "docx"
    elif ext in ["pptx", "ppt"]:
        return "pptx"
    elif ext in ["xlsx", "xls"]:
        return "xlsx"
    elif ext == "pdf":
        return "pdf"
    elif ext in ["png", "jpg", "jpeg", "gif", "bmp", "tiff"]:
        return "image"
    else:
        return None

def process_batch_urls(urls, mode="llm", summary_length="short", summary_format="bullets"):
    """
    Process multiple URLs
    Returns: list of results
    """
    results = []
    
    for idx, url in enumerate(urls):
        url = url.strip()
        if not url:
            continue
        
        try:
            result = analyze_website(url, mode, summary_length, summary_format)
            result['index'] = idx + 1
            result['source'] = url
            results.append(result)
        except Exception as e:
            results.append({
                'index': idx + 1,
                'source': url,
                'error': f"Failed to analyze: {str(e)}"
            })
    
    return results

def process_batch_files(files, upload_folder, mode="llm", summary_length="short", summary_format="bullets"):
    """
    Process multiple files
    Returns: list of results
    """
    results = []
    
    for idx, file in enumerate(files):
        if not file or not file.filename:
            continue
        
        try:
            filename = secure_filename(file.filename)
            file_type = get_file_type(filename)
            
            if not file_type:
                results.append({
                    'index': idx + 1,
                    'source': filename,
                    'error': 'Unsupported file type'
                })
                continue
            
            # Save file temporarily
            path = os.path.join(upload_folder, f"batch_{idx}_{filename}")
            file.save(path)
            
            # Analyze based on type
            if file_type == "pdf":
                result = analyze_pdf(path, mode, summary_length, summary_format)
            elif file_type == "docx":
                result = analyze_docx(path, mode, summary_length, summary_format)
            elif file_type == "pptx":
                result = analyze_pptx(path, mode, summary_length, summary_format)
            elif file_type == "xlsx":
                result = analyze_xlsx(path, mode, summary_length, summary_format)
            elif file_type == "image":
                result = analyze_image(path, mode, summary_length, summary_format)
            else:
                result = {'error': 'Unsupported file type'}
            
            result['index'] = idx + 1
            result['source'] = filename
            result['file_type'] = file_type
            results.append(result)
            
            # Clean up
            if os.path.exists(path):
                os.remove(path)
                
        except Exception as e:
            results.append({
                'index': idx + 1,
                'source': file.filename if file else 'Unknown',
                'error': f"Failed to process: {str(e)}"
            })
    
    return results

def create_batch_export_zip(results, export_format='pdf'):
    """
    Create a ZIP file containing all batch results
    Returns: BytesIO buffer
    """
    buffer = io.BytesIO()
    
    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for result in results:
            if 'error' in result:
                continue
            
            try:
                filename_base = f"analysis_{result.get('index', 1)}"
                
                if export_format == 'pdf':
                    pdf_buffer = export_to_pdf(result)
                    zip_file.writestr(f"{filename_base}.pdf", pdf_buffer.getvalue())
                
                elif export_format == 'docx':
                    docx_buffer = export_to_docx(result)
                    zip_file.writestr(f"{filename_base}.docx", docx_buffer.getvalue())
                
                elif export_format == 'markdown':
                    md_content = export_to_markdown(result)
                    zip_file.writestr(f"{filename_base}.md", md_content)
                
                elif export_format == 'json':
                    json_content = export_to_json(result)
                    zip_file.writestr(f"{filename_base}.json", json_content)
            
            except Exception as e:
                print(f"Error exporting result {result.get('index')}: {e}")
                continue
    
    buffer.seek(0)
    return buffer