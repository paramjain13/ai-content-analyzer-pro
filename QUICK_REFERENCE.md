# ⚡ Quick Reference Guide

## 🚀 Quick Start Commands

### Initial Setup
```bash
# Clone repository
git clone https://github.com/yourusername/ai-content-analyzer-pro.git
cd ai-content-analyzer-pro

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
python -m spacy download en_core_web_sm

# Setup environment
cp .env.example .env
# Edit .env with your API keys

# Initialize database
python -c "from app import app, db; app.app_context().push(); db.create_all()"

# Run application
python app.py
```

### Git Commands
```bash
# Check status
git status

# Add files
git add .

# Commit changes
git commit -m "your message"

# Push to GitHub
git push origin main

# Pull latest changes
git pull origin main

# View commit history
git log --oneline
```

## 📚 File Structure

```
ai-content-analyzer-pro/
├── app.py                          # Main application
├── models.py                       # Database models
├── requirements.txt                # Dependencies
├── .env.example                    # Environment template
├── .gitignore                      # Git ignore rules
├── README.md                       # Main documentation
├── LICENSE                         # MIT License
├── SETUP_GUIDE.md                  # Setup instructions
├── GITHUB_UPLOAD_GUIDE.md          # GitHub upload steps
├── DEPLOYMENT.md                   # Deployment guide
├── CONTRIBUTING.md                 # Contributing guidelines
│
├── .github/
│   └── workflows/
│       └── ci-cd.yml              # GitHub Actions
│
├── docs/
│   ├── ARCHITECTURE.md            # System architecture
│   └── screenshots/               # Project screenshots
│
├── services/
│   ├── analyzer.py                # Content analysis
│   └── content_analyzer.py        # Document processing
│
├── templates/
│   ├── index.html                 # Main interface
│   ├── login.html                 # Login page
│   ├── register.html              # Registration
│   ├── history.html               # Analysis history
│   ├── collections.html           # Collections
│   └── batch.html                 # Batch processing
│
├── static/
│   ├── css/
│   │   └── app.js                # JavaScript
│   └── dark-mode.css             # Dark theme
│
├── Core modules/
│   ├── scraper.py                # Web scraping
│   ├── summarizer.py             # Summarization
│   ├── document_store.py         # Vector database
│   ├── chat_service.py           # RAG system
│   ├── export_service.py         # Export functionality
│   └── batch_processor.py        # Batch operations
│
└── Document readers/
    ├── pdf_reader.py             # PDF processing
    ├── docx_reader.py            # Word documents
    ├── pptx_reader.py            # PowerPoint
    ├── xlsx_reader.py            # Excel sheets
    ├── image_reader.py           # Image OCR
    └── youtube_reader.py         # YouTube transcripts
```

## 🔑 Environment Variables

```bash
# Required
OPENAI_API_KEY=sk-...              # OpenAI API key
GOOGLE_API_KEY=...                 # Google Gemini key
SECRET_KEY=...                     # Flask secret key

# Optional
DATABASE_URL=sqlite:///...         # Database URL
MAX_FILE_SIZE_MB=10               # Upload size limit
TESSERACT_PATH=/usr/bin/tesseract # OCR path
```

## 🎯 Key Features

### Document Support
- ✅ PDF files
- ✅ Word documents (.docx)
- ✅ PowerPoint (.pptx)
- ✅ Excel (.xlsx)
- ✅ Images (with OCR)
- ✅ Websites (web scraping)
- ✅ YouTube transcripts

### AI Capabilities
- ✅ Multi-model summarization (GPT-4, Gemini)
- ✅ RAG system with vector database
- ✅ Conversational Q&A
- ✅ Semantic search
- ✅ Context-aware responses

### User Features
- ✅ Authentication & sessions
- ✅ Document collections
- ✅ Analysis history
- ✅ Batch processing
- ✅ Export (PDF, DOCX, MD, JSON)

## 🛠 Common Commands

### Development
```bash
# Run in debug mode
python app.py

# Check Python version
python --version

# List installed packages
pip list

# Update a package
pip install --upgrade package_name

# Create requirements file
pip freeze > requirements.txt
```

### Database
```bash
# Initialize database
python -c "from app import app, db; app.app_context().push(); db.create_all()"

# Drop all tables
python -c "from app import app, db; app.app_context().push(); db.drop_all()"

# Reset database (drop + create)
python -c "from app import app, db; app.app_context().push(); db.drop_all(); db.create_all()"
```

### Testing
```bash
# Test imports
python -c "from app import app; print('Success!')"

# Check spaCy model
python -c "import spacy; nlp = spacy.load('en_core_web_sm'); print('SpaCy OK')"

# Test OpenAI connection
python -c "from openai import OpenAI; print('OpenAI imported')"
```

## 🔧 Troubleshooting

### Common Issues

**Port in use**:
```bash
# Find process
lsof -ti:5000
# Kill it
kill -9 <PID>
```

**Module not found**:
```bash
pip install -r requirements.txt
```

**Database locked**:
```bash
# Close all connections and restart
rm -rf instance/
# Recreate database
```

**API key error**:
```bash
# Check .env file
cat .env
# Ensure no extra spaces or quotes
```

## 📊 Performance Tips

1. **Use SSD** for better I/O
2. **Increase RAM** for large documents
3. **Enable caching** in production
4. **Use PostgreSQL** instead of SQLite
5. **Implement CDN** for static files

## 🔐 Security Checklist

- [ ] Strong SECRET_KEY generated
- [ ] API keys in .env (not in code)
- [ ] .env in .gitignore
- [ ] HTTPS enabled (production)
- [ ] Input validation everywhere
- [ ] File upload restrictions
- [ ] SQL injection prevention
- [ ] XSS protection enabled

## 📈 Metrics to Track

- Response time
- Error rate
- Document processing time
- API call count
- User engagement
- Storage usage

## 🎨 Customization

### Change Port
```python
# In app.py
if __name__ == '__main__':
    app.run(debug=True, port=5001)
```

### Change Database
```python
# In app.py
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://user:pass@localhost/db"
```

### Add New Document Type
1. Create reader in appropriate directory
2. Add to ALLOWED_EXTENSIONS
3. Update get_file_type()
4. Add analysis route

## 🌐 URLs

- **Application**: http://localhost:5000
- **API Docs**: http://localhost:5000/api/docs (if implemented)
- **Health Check**: http://localhost:5000/health (if implemented)

## 📝 Commit Message Examples

```bash
# New feature
git commit -m "feat: Add batch PDF processing"

# Bug fix
git commit -m "fix: Resolve memory leak in document parser"

# Documentation
git commit -m "docs: Update API documentation"

# Performance
git commit -m "perf: Optimize database queries"

# Refactoring
git commit -m "refactor: Improve code structure"
```

## 🔄 Update Workflow

```bash
# 1. Check current branch
git branch

# 2. Pull latest changes
git pull origin main

# 3. Make changes
# ... edit files ...

# 4. Check what changed
git status
git diff

# 5. Stage changes
git add .

# 6. Commit
git commit -m "your message"

# 7. Push
git push origin main
```

## 🆘 Get Help

- **Documentation**: Check README.md
- **Setup Issues**: See SETUP_GUIDE.md
- **Deployment**: Read DEPLOYMENT.md
- **GitHub**: See GITHUB_UPLOAD_GUIDE.md
- **Architecture**: Review docs/ARCHITECTURE.md
- **Issues**: Open GitHub issue
- **Email**: your.email@example.com

## 🎓 Learning Resources

- Flask Documentation: flask.palletsprojects.com
- OpenAI API: platform.openai.com/docs
- ChromaDB: docs.trychroma.com
- SQLAlchemy: docs.sqlalchemy.org
- Python: python.org/doc

## 💡 Pro Tips

1. **Commit often** with clear messages
2. **Test before pushing**
3. **Use virtual environments**
4. **Keep secrets secret**
5. **Document as you go**
6. **Follow PEP 8** style guide
7. **Use type hints** in Python
8. **Write unit tests**
9. **Review your own PRs**
10. **Stay updated** with dependencies

---

**Need more help?** Check the comprehensive guides in the docs/ folder!
