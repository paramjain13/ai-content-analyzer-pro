import os
import re
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session, send_file, make_response
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
from werkzeug.utils import secure_filename
from datetime import datetime

from models import db, User, Analysis, Collection
from services.analyzer import (
    analyze_website, analyze_pdf, analyze_docx, 
    analyze_pptx, analyze_xlsx, analyze_image
)
from chat_service import chat_with_document
from export_service import export_to_pdf, export_to_docx, export_to_markdown, export_to_json

UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"pdf", "docx", "doc", "pptx", "ppt", "xlsx", "xls", "png", "jpg", "jpeg", "gif", "bmp", "tiff"}
MAX_FILE_SIZE_MB = 10

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = MAX_FILE_SIZE_MB * 1024 * 1024
app.config["SECRET_KEY"] = "your-secret-key-change-this-in-production-12345"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///content_analyzer.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize extensions
db.init_app(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Create database tables
with app.app_context():
    db.create_all()
    # Migrate existing data if needed
    try:
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        columns = [col['name'] for col in inspector.get_columns('analyses')]
        if 'collection_id' not in columns:
            with db.engine.connect() as conn:
                conn.execute(db.text('ALTER TABLE analyses ADD COLUMN collection_id INTEGER'))
                conn.execute(db.text('ALTER TABLE analyses ADD COLUMN notes TEXT'))
                conn.commit()
    except:
        pass

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def get_file_type(filename):
    """Determine file type from extension"""
    ext = filename.rsplit(".", 1)[1].lower()
    
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

def validate_url(url):
    """Validate URL format and protocol"""
    if not url:
        return False, "URL cannot be empty"
    
    url_pattern = re.compile(
        r'^https?://'
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'
        r'localhost|'
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
        r'(?::\d+)?'
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    if not url_pattern.match(url):
        return False, "Invalid URL format. Please include http:// or https://"
    
    return True, None

def save_analysis_to_db(result, source_type, source_url, mode, summary_length, summary_format):
    """Save analysis results to database"""
    if not current_user.is_authenticated:
        return None
    
    try:
        analysis = Analysis(
            user_id=current_user.id,
            title=result.get('title', 'Untitled'),
            source_type=source_type,
            source_url=source_url,
            doc_id=result.get('doc_id'),
            summary_format=summary_format,
            summary_mode=mode,
            summary_length=summary_length,
            word_count=result.get('analysis', {}).get('reading_time', {}).get('word_count', 0),
            reading_time=result.get('analysis', {}).get('reading_time', {}).get('reading_time', 'Unknown')
        )
        
        analysis.set_result_data(result)
        
        db.session.add(analysis)
        db.session.commit()
        
        return analysis.id
    except Exception as e:
        db.session.rollback()
        print(f"Error saving analysis: {e}")
        return None

@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")
        
        if not username or len(username) < 3:
            flash("Username must be at least 3 characters long", "error")
            return render_template("register.html")
        
        if not email or "@" not in email:
            flash("Please enter a valid email address", "error")
            return render_template("register.html")
        
        if not password or len(password) < 6:
            flash("Password must be at least 6 characters long", "error")
            return render_template("register.html")
        
        if password != confirm_password:
            flash("Passwords do not match", "error")
            return render_template("register.html")
        
        if User.query.filter_by(username=username).first():
            flash("Username already exists", "error")
            return render_template("register.html")
        
        if User.query.filter_by(email=email).first():
            flash("Email already registered", "error")
            return render_template("register.html")
        
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User(username=username, email=email, password_hash=hashed_password)
        
        try:
            db.session.add(new_user)
            db.session.commit()
            flash("Account created successfully! Please log in.", "success")
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash("An error occurred. Please try again.", "error")
            return render_template("register.html")
    
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        remember = request.form.get("remember", False)
        
        user = User.query.filter_by(username=username).first()
        
        if user and bcrypt.check_password_hash(user.password_hash, password):
            login_user(user, remember=remember)
            next_page = request.args.get('next')
            flash(f"Welcome back, {user.username}!", "success")
            return redirect(next_page if next_page else url_for('home'))
        else:
            flash("Invalid username or password", "error")
    
    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out successfully", "success")
    return redirect(url_for('login'))

@app.route("/history")
@login_required
def history():
    """View analysis history with filters"""
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    # Build query
    query = Analysis.query.filter_by(user_id=current_user.id)
    
    # Apply filters
    search = request.args.get('search', '').strip()
    if search:
        query = query.filter(Analysis.title.ilike(f'%{search}%'))
    
    source_type = request.args.get('source_type', '').strip()
    if source_type:
        query = query.filter_by(source_type=source_type)
    
    collection_id = request.args.get('collection', '').strip()
    if collection_id:
        query = query.filter_by(collection_id=int(collection_id))
    
    favorites = request.args.get('favorites', '').strip()
    if favorites == 'true':
        query = query.filter_by(is_favorite=True)
    
    # Order by created date
    query = query.order_by(Analysis.created_at.desc())
    
    # Paginate
    analyses = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template("history.html", analyses=analyses)

@app.route("/analysis/<int:analysis_id>")
@login_required
def view_analysis(analysis_id):
    """View a specific analysis"""
    analysis = Analysis.query.get_or_404(analysis_id)
    
    if analysis.user_id != current_user.id:
        flash("You don't have permission to view this analysis", "error")
        return redirect(url_for('history'))
    
    result = analysis.get_result_data()
    
    # Store in session for export
    session['current_result'] = result
    
    return render_template("index.html", result=result, from_history=True)

@app.route("/analysis/<int:analysis_id>/delete", methods=["POST"])
@login_required
def delete_analysis(analysis_id):
    """Delete an analysis"""
    analysis = Analysis.query.get_or_404(analysis_id)
    
    if analysis.user_id != current_user.id:
        flash("You don't have permission to delete this analysis", "error")
        return redirect(url_for('history'))
    
    try:
        db.session.delete(analysis)
        db.session.commit()
        flash("Analysis deleted successfully", "success")
    except Exception as e:
        db.session.rollback()
        flash("Error deleting analysis", "error")
    
    return redirect(url_for('history'))

@app.route("/analysis/<int:analysis_id>/toggle-favorite", methods=["POST"])
@login_required
def toggle_favorite(analysis_id):
    """Toggle favorite status"""
    analysis = Analysis.query.get_or_404(analysis_id)
    
    if analysis.user_id != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403
    
    analysis.is_favorite = not analysis.is_favorite
    
    try:
        db.session.commit()
        return jsonify({"success": True, "is_favorite": analysis.is_favorite})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route("/analysis/<int:analysis_id>/update", methods=["POST"])
@login_required
def update_analysis(analysis_id):
    """Update analysis tags, notes, collection"""
    analysis = Analysis.query.get_or_404(analysis_id)
    
    if analysis.user_id != current_user.id:
        flash("You don't have permission to update this analysis", "error")
        return redirect(url_for('history'))
    
    # Update tags
    tags = request.form.get("tags", "").strip()
    if tags:
        analysis.tags = tags
    else:
        analysis.tags = None
    
    # Update notes
    notes = request.form.get("notes", "").strip()
    analysis.notes = notes if notes else None
    
    # Update collection
    collection_id = request.form.get("collection_id")
    if collection_id and collection_id != "none":
        analysis.collection_id = int(collection_id)
    else:
        analysis.collection_id = None
    
    try:
        db.session.commit()
        flash("Analysis updated successfully", "success")
    except Exception as e:
        db.session.rollback()
        flash("Error updating analysis", "error")
    
    return redirect(url_for('history'))

@app.route("/collections")
@login_required
def collections():
    """View all collections"""
    user_collections = Collection.query.filter_by(user_id=current_user.id).all()
    return render_template("collections.html", collections=user_collections)

@app.route("/collections/create", methods=["POST"])
@login_required
def create_collection():
    """Create a new collection"""
    name = request.form.get("name", "").strip()
    description = request.form.get("description", "").strip()
    color = request.form.get("color", "#667eea")
    
    if not name:
        flash("Collection name is required", "error")
        return redirect(url_for('collections'))
    
    collection = Collection(
        user_id=current_user.id,
        name=name,
        description=description,
        color=color
    )
    
    try:
        db.session.add(collection)
        db.session.commit()
        flash(f"Collection '{name}' created successfully!", "success")
    except Exception as e:
        db.session.rollback()
        flash("Error creating collection", "error")
    
    return redirect(url_for('collections'))

@app.route("/collections/<int:collection_id>/edit", methods=["POST"])
@login_required
def edit_collection(collection_id):
    """Edit a collection"""
    collection = Collection.query.get_or_404(collection_id)
    
    if collection.user_id != current_user.id:
        flash("You don't have permission to edit this collection", "error")
        return redirect(url_for('collections'))
    
    name = request.form.get("name", "").strip()
    description = request.form.get("description", "").strip()
    color = request.form.get("color", "#667eea")
    
    if not name:
        flash("Collection name is required", "error")
        return redirect(url_for('collections'))
    
    collection.name = name
    collection.description = description
    collection.color = color
    
    try:
        db.session.commit()
        flash(f"Collection '{name}' updated successfully!", "success")
    except Exception as e:
        db.session.rollback()
        flash("Error updating collection", "error")
    
    return redirect(url_for('collections'))

@app.route("/collections/<int:collection_id>/delete", methods=["POST"])
@login_required
def delete_collection(collection_id):
    """Delete a collection"""
    collection = Collection.query.get_or_404(collection_id)
    
    if collection.user_id != current_user.id:
        flash("You don't have permission to delete this collection", "error")
        return redirect(url_for('collections'))
    
    try:
        # Remove collection from analyses (set to None)
        Analysis.query.filter_by(collection_id=collection_id).update({'collection_id': None})
        
        db.session.delete(collection)
        db.session.commit()
        flash("Collection deleted successfully", "success")
    except Exception as e:
        db.session.rollback()
        flash("Error deleting collection", "error")
    
    return redirect(url_for('collections'))

@app.route("/", methods=["GET", "POST"])
def home():
    result = None

    if request.method == "POST":
        try:
            mode = request.form.get("mode", "llm")
            summary_length = request.form.get("summary_length", "short")
            summary_format = request.form.get("summary_format", "bullets")
            model_id = request.form.get("model_id", "gpt-4o-mini")  # NEW: Get model selection
            
            if mode not in ["llm", "nlp"]:
                result = {"error": "Invalid mode selected"}
                return render_template("index.html", result=result)
            
            if summary_length not in ["short", "long"]:
                result = {"error": "Invalid summary length selected"}
                return render_template("index.html", result=result)
            
            if summary_format not in ["bullets", "qa", "timeline", "insights"]:
                result = {"error": "Invalid summary format selected"}
                return render_template("index.html", result=result)

            url = request.form.get("url", "").strip()
            has_file = any(key in request.files and request.files[key].filename 
                          for key in ["pdf", "docx", "pptx", "xlsx", "image"])

            inputs_provided = sum([bool(url), has_file])

            if inputs_provided > 1:
                result = {"error": "Please provide only ONE input: either a URL or file"}
            elif inputs_provided == 0:
                result = {"error": "Please provide a URL or upload a file"}
            elif url:
                is_valid, error_msg = validate_url(url)
                if not is_valid:
                    result = {"error": error_msg}
                else:
                    result = analyze_website(url, mode, summary_length, summary_format, model_id)
                    if 'error' not in result:
                        save_analysis_to_db(result, 'website', url, mode, summary_length, summary_format)
            elif has_file:
                file = None
                file_key = None
                
                for key in ["pdf", "docx", "pptx", "xlsx", "image"]:
                    if key in request.files and request.files[key].filename:
                        file = request.files[key]
                        file_key = key
                        break
                
                if not file:
                    result = {"error": "No file uploaded"}
                elif not allowed_file(file.filename):
                    result = {"error": "Invalid file type. Allowed: PDF, DOCX, PPTX, XLSX, Images"}
                else:
                    try:
                        filename = secure_filename(file.filename)
                        if not filename:
                            result = {"error": "Invalid filename"}
                        else:
                            path = os.path.join(UPLOAD_FOLDER, filename)
                            file.save(path)
                            
                            if os.path.getsize(path) == 0:
                                result = {"error": "Uploaded file is empty"}
                            else:
                                file_type = get_file_type(filename)
                                
                                if file_type == "pdf":
                                    result = analyze_pdf(path, mode, summary_length, summary_format, model_id)
                                elif file_type == "docx":
                                    result = analyze_docx(path, mode, summary_length, summary_format, model_id)
                                elif file_type == "pptx":
                                    result = analyze_pptx(path, mode, summary_length, summary_format, model_id)
                                elif file_type == "xlsx":
                                    result = analyze_xlsx(path, mode, summary_length, summary_format, model_id)
                                elif file_type == "image":
                                    result = analyze_image(path, mode, summary_length, summary_format, model_id)
                                else:
                                    result = {"error": "Unsupported file type"}
                                
                                if 'error' not in result:
                                    save_analysis_to_db(result, file_type, filename, mode, summary_length, summary_format)
                            
                            if os.path.exists(path):
                                os.remove(path)
                    except Exception as e:
                        result = {"error": f"File processing failed: {str(e)}"}
                        try:
                            if 'path' in locals() and os.path.exists(path):
                                os.remove(path)
                        except:
                            pass

        except Exception as e:
            result = {"error": f"An unexpected error occurred: {str(e)}"}
    
    # Store result in session for export
    if result and 'error' not in result:
        session['current_result'] = result

    return render_template("index.html", result=result)

@app.route("/chat", methods=["POST"])
def chat():
    """API endpoint for chatting with documents"""
    try:
        data = request.get_json()
        
        question = data.get("question", "").strip()
        doc_id = data.get("doc_id", "").strip()
        conversation_history = data.get("history", [])
        
        if not question:
            return jsonify({"error": "Question is required"}), 400
        
        if not doc_id:
            return jsonify({"error": "Document ID is required"}), 400
        
        result = chat_with_document(question, doc_id, conversation_history)
        
        if result["error"]:
            return jsonify({"error": result["error"]}), 500
        
        return jsonify({
            "answer": result["answer"],
            "sources": result["sources"]
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/batch")
def batch():
    """Batch processing page"""
    return render_template("batch.html")

@app.route("/batch/urls", methods=["POST"])
def batch_process_urls():
    """Process multiple URLs"""
    from batch_processor import process_batch_urls
    
    try:
        urls_text = request.form.get("urls", "").strip()
        mode = request.form.get("mode", "llm")
        summary_length = request.form.get("summary_length", "short")
        summary_format = request.form.get("summary_format", "bullets")
        
        if not urls_text:
            flash("Please enter at least one URL", "error")
            return redirect(url_for('batch'))
        
        urls = [url.strip() for url in urls_text.split('\n') if url.strip()]
        
        if len(urls) > 10:
            flash("Maximum 10 URLs allowed per batch", "error")
            return redirect(url_for('batch'))
        
        results = process_batch_urls(urls, mode, summary_length, summary_format)
        
        session['batch_results'] = results
        
        flash(f"Processed {len(results)} URLs successfully!", "success")
        return render_template("batch.html", batch_results=results)
        
    except Exception as e:
        flash(f"Batch processing failed: {str(e)}", "error")
        return redirect(url_for('batch'))

@app.route("/batch/files", methods=["POST"])
def batch_process_files():
    """Process multiple files"""
    from batch_processor import process_batch_files
    
    try:
        mode = request.form.get("mode", "llm")
        summary_length = request.form.get("summary_length", "short")
        summary_format = request.form.get("summary_format", "bullets")
        
        files = request.files.getlist("files")
        
        if not files or all(not f.filename for f in files):
            flash("Please upload at least one file", "error")
            return redirect(url_for('batch'))
        
        if len(files) > 10:
            flash("Maximum 10 files allowed per batch", "error")
            return redirect(url_for('batch'))
        
        results = process_batch_files(files, UPLOAD_FOLDER, mode, summary_length, summary_format)
        
        session['batch_results'] = results
        
        flash(f"Processed {len(results)} files successfully!", "success")
        return render_template("batch.html", batch_results=results)
        
    except Exception as e:
        flash(f"Batch processing failed: {str(e)}", "error")
        return redirect(url_for('batch'))

@app.route("/batch/export/<format>")
def export_batch_results(format):
    """Export all batch results as ZIP"""
    from batch_processor import create_batch_export_zip
    
    try:
        batch_results = session.get('batch_results')
        
        if not batch_results:
            flash("No batch results available to export", "error")
            return redirect(url_for('batch'))
        
        zip_buffer = create_batch_export_zip(batch_results, format)
        
        filename = f"batch_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
        
        return send_file(
            zip_buffer,
            as_attachment=True,
            download_name=filename,
            mimetype='application/zip'
        )
        
    except Exception as e:
        flash(f"Export failed: {str(e)}", "error")
        return redirect(url_for('batch'))

@app.route("/analysis/<int:analysis_id>/export/<format>")
@login_required
def export_analysis(analysis_id, format):
    """Export analysis from history in various formats"""
    analysis = Analysis.query.get_or_404(analysis_id)
    
    if analysis.user_id != current_user.id:
        flash("You don't have permission to export this analysis", "error")
        return redirect(url_for('history'))
    
    result_data = analysis.get_result_data()
    filename_base = f"analysis_{analysis.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    try:
        if format == 'pdf':
            buffer = export_to_pdf(result_data)
            return send_file(
                buffer,
                as_attachment=True,
                download_name=f"{filename_base}.pdf",
                mimetype='application/pdf'
            )
        
        elif format == 'docx':
            buffer = export_to_docx(result_data)
            return send_file(
                buffer,
                as_attachment=True,
                download_name=f"{filename_base}.docx",
                mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            )
        
        elif format == 'markdown':
            md_content = export_to_markdown(result_data)
            response = make_response(md_content)
            response.headers['Content-Type'] = 'text/markdown'
            response.headers['Content-Disposition'] = f'attachment; filename={filename_base}.md'
            return response
        
        elif format == 'json':
            json_content = export_to_json(result_data)
            response = make_response(json_content)
            response.headers['Content-Type'] = 'application/json'
            response.headers['Content-Disposition'] = f'attachment; filename={filename_base}.json'
            return response
        
        else:
            flash("Invalid export format", "error")
            return redirect(url_for('view_analysis', analysis_id=analysis_id))
    
    except Exception as e:
        flash(f"Export failed: {str(e)}", "error")
        return redirect(url_for('view_analysis', analysis_id=analysis_id))

@app.route("/export/current/<format>")
def export_current_analysis(format):
    """Export current analysis result from session"""
    try:
        result_data = session.get('current_result')
        
        if not result_data:
            flash("No analysis available to export. Please analyze content first.", "error")
            return redirect(url_for('home'))
        
        filename_base = f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        if format == 'pdf':
            buffer = export_to_pdf(result_data)
            return send_file(
                buffer,
                as_attachment=True,
                download_name=f"{filename_base}.pdf",
                mimetype='application/pdf'
            )
        
        elif format == 'docx':
            buffer = export_to_docx(result_data)
            return send_file(
                buffer,
                as_attachment=True,
                download_name=f"{filename_base}.docx",
                mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            )
        
        elif format == 'markdown':
            md_content = export_to_markdown(result_data)
            response = make_response(md_content)
            response.headers['Content-Type'] = 'text/markdown'
            response.headers['Content-Disposition'] = f'attachment; filename={filename_base}.md'
            return response
        
        elif format == 'json':
            json_content = export_to_json(result_data)
            response = make_response(json_content)
            response.headers['Content-Type'] = 'application/json'
            response.headers['Content-Disposition'] = f'attachment; filename={filename_base}.json'
            return response
        
        else:
            flash("Invalid export format", "error")
            return redirect(url_for('home'))
    
    except Exception as e:
        flash(f"Export failed: {str(e)}", "error")
        return redirect(url_for('home'))

@app.errorhandler(413)
def too_large(e):
    result = {"error": f"File is too large. Maximum size is {MAX_FILE_SIZE_MB}MB"}
    return render_template("index.html", result=result), 413

if __name__ == "__main__":
    app.run(debug=True)