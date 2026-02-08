# AI Content Analyzer Pro

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.0+-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4-orange.svg)

**A production-ready AI-powered platform for intelligent document analysis, summarization, and conversational Q&A**

[Features](#-features) • [Demo](#-demo) • [Installation](#-installation) • [Usage](#-usage) • [Tech Stack](#-tech-stack) • [Architecture](#-architecture)

</div>

---

## Overview

AI Content Analyzer Pro is an enterprise-grade web application that leverages cutting-edge AI technologies to extract, analyze, and summarize content from multiple sources including websites, PDFs, Word documents, PowerPoints, Excel files, and images. Built with scalability and user experience in mind, it features a RAG (Retrieval-Augmented Generation) system for intelligent document Q&A.

### Key Highlights

- **Multi-format Support**: Process PDFs, DOCX, PPTX, XLSX, and images
- **AI-Powered Analysis**: Utilizes GPT-4 and Google's Gemini models
- **RAG Implementation**: Vector database with ChromaDB for semantic search
- **User Management**: Complete authentication system with secure password hashing
- **Document Collections**: Organize and categorize analyses
- **Batch Processing**: Handle multiple documents simultaneously
- **Export Options**: PDF, DOCX, Markdown, and JSON export formats
- **Conversational Q&A**: Chat with your documents using advanced NLP

## Features

### Content Analysis
- **Website Scraping**: Extract and summarize content from any public URL
- **Multi-Document Support**: Process PDFs, Word docs, PowerPoints, spreadsheets, and images
- **OCR Integration**: Extract text from images using Tesseract
- **Smart Summarization**: Multiple AI models with fallback mechanisms
- **Customizable Output**: Choose summary length and format (paragraph, bullet points, detailed)

### RAG & Chat System
- **Semantic Search**: ChromaDB vector database for intelligent document retrieval
- **Conversational Interface**: Ask questions about your documents in natural language
- **Context-Aware Responses**: Leverages document embeddings for accurate answers
- **Multi-Model Support**: OpenAI GPT-4 and Google Gemini integration

### User Management
- **Secure Authentication**: BCrypt password hashing
- **Session Management**: Flask-Login integration
- **User-Specific Content**: Private document collections per user
- **Analysis History**: Track all your document analyses

### Organization & Export
- **Collections**: Create custom collections to organize related documents
- **Tagging System**: Add notes and categorize analyses
- **Multiple Export Formats**: 
  - PDF with professional formatting
  - Microsoft Word (DOCX)
  - Markdown for documentation
  - JSON for data processing
- **Batch Operations**: Process multiple files simultaneously

### Modern UI/UX
- **Responsive Design**: Mobile-friendly interface
- **Dark Mode**: Eye-friendly dark theme
- **Real-time Feedback**: Progress indicators and status updates
- **Intuitive Navigation**: Clean, professional interface

## Tech Stack

### Backend
- **Framework**: Flask 3.0+
- **Database**: SQLAlchemy with SQLite (easily upgradable to PostgreSQL)
- **Authentication**: Flask-Login + BCrypt
- **AI/ML**: 
  - OpenAI GPT-4 API
  - Google Generative AI (Gemini)
  - Sentence Transformers
  - ChromaDB (Vector Database)
- **NLP**: 
  - TextBlob
  - spaCy
  - Langdetect

### Document Processing
- **PDF**: PyPDF, ReportLab
- **Word**: python-docx
- **PowerPoint**: python-pptx
- **Excel**: openpyxl
- **Images**: Pillow, Pytesseract (OCR)
- **Web**: BeautifulSoup4, Requests

### Frontend
- **HTML5/CSS3**: Modern responsive design
- **JavaScript**: Vanilla JS for interactivity
- **UI Components**: Custom-built components

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Git
- (Optional) Tesseract OCR for image text extraction

### Quick Start

1. **Clone the repository**
```bash
git clone https://github.com/paramjain13/ai-content-analyzer-pro.git
cd ai-content-analyzer-pro
```

2. **Create and activate virtual environment**
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Download spaCy language model**
```bash
python -m spacy download en_core_web_sm
```

5. **Set up environment variables**
```bash
# Create .env file
cp .env.example .env

# Edit .env and add your API keys:
# OPENAI_API_KEY=your_openai_key_here
# GOOGLE_API_KEY=your_google_key_here
```

6. **Initialize the database**
```bash
python
>>> from app import app, db
>>> with app.app_context():
>>>     db.create_all()
>>> exit()
```

7. **Run the application**
```bash
python app.py
```

8. **Open your browser**
```
http://localhost:5000
```

## Usage

### Basic Workflow

1. **Register/Login**: Create an account or log in to existing one
2. **Analyze Content**:
   - Enter a website URL for web scraping
   - Upload documents (PDF, DOCX, PPTX, XLSX, images)
   - Choose summary length and format
3. **Organize**: Create collections and add analyses to them
4. **Chat**: Ask questions about your documents using the RAG system
5. **Export**: Download summaries in your preferred format

### API Keys Setup

#### OpenAI API
1. Visit [OpenAI Platform](https://platform.openai.com/)
2. Create an account and generate an API key
3. Add to `.env`: `OPENAI_API_KEY=sk-...`

#### Google Gemini API
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create an API key
3. Add to `.env`: `GOOGLE_API_KEY=...`

## Architecture

```
ai-content-analyzer-pro/
├── app.py                      # Main Flask application
├── models.py                   # Database models
├── requirements.txt            # Python dependencies
├── .env.example               # Environment template
├── .gitignore                 # Git ignore rules
│
├── services/                   # Business logic
│   ├── analyzer.py            # Content analysis services
│   └── content_analyzer.py    # Document processing
│
├── readers/                    # Document readers
│   ├── pdf_reader.py          # PDF processing
│   ├── docx_reader.py         # Word documents
│   ├── pptx_reader.py         # PowerPoint
│   ├── xlsx_reader.py         # Excel sheets
│   ├── image_reader.py        # Image OCR
│   └── youtube_reader.py      # YouTube transcripts
│
├── core/                      # Core functionality
│   ├── scraper.py            # Web scraping
│   ├── summarizer.py         # Text summarization
│   ├── llm_summarizer.py     # LLM integration
│   ├── multi_model_summarizer.py
│   ├── advanced_summarizer.py
│   ├── smart_preprocessor.py # Text preprocessing
│   ├── document_store.py     # Vector database
│   ├── chat_service.py       # RAG chat system
│   ├── export_service.py     # Export functionality
│   └── batch_processor.py    # Batch operations
│
├── templates/                 # HTML templates
│   ├── index.html            # Main interface
│   ├── login.html            # Authentication
│   ├── register.html
│   ├── history.html          # Analysis history
│   ├── collections.html      # Collection management
│   └── batch.html            # Batch processing
│
└── static/                    # Static files
    ├── css/
    │   └── app.js
    └── dark-mode.css
```

## Security Features

- **Password Hashing**: BCrypt with salt rounds
- **Session Management**: Secure Flask sessions
- **File Upload Validation**: Type and size checking
- **SQL Injection Prevention**: SQLAlchemy ORM
- **XSS Protection**: Template escaping
- **Environment Variables**: Sensitive data in .env

## Performance

- **Async Operations**: Non-blocking document processing
- **Caching**: Vector embeddings cached in ChromaDB
- **Batch Processing**: Efficient multi-document handling
- **Optimized Queries**: Indexed database operations
- **Smart Chunking**: Efficient text splitting for large documents

## Roadmap

- [ ] PostgreSQL migration for production
- [ ] Docker containerization
- [ ] REST API endpoints
- [ ] Real-time collaboration features
- [ ] Advanced analytics dashboard
- [ ] Cloud storage integration (S3, Azure Blob)
- [ ] Webhook support for automation
- [ ] Multi-language support
- [ ] Mobile app (React Native)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

**Your Name**
- GitHub: [paramjain13](https://github.com/paramjain13)
- LinkedIn: [Param Jain](https://www.linkedin.com/in/paramsachinjain/)
- Email: jain.param@northeastern.edu

## Acknowledgments

- OpenAI for GPT-4 API
- Google for Gemini AI
- ChromaDB for vector database
- Flask community for the excellent framework
- All open-source contributors



