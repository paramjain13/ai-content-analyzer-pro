# 🚀 Complete Setup Guide

This guide will walk you through setting up AI Content Analyzer Pro from scratch.

## 📋 Table of Contents
1. [System Requirements](#system-requirements)
2. [Installation Steps](#installation-steps)
3. [API Keys Setup](#api-keys-setup)
4. [Database Configuration](#database-configuration)
5. [Optional Components](#optional-components)
6. [Verification](#verification)
7. [Troubleshooting](#troubleshooting)

## System Requirements

### Minimum Requirements
- **OS**: Windows 10+, macOS 10.14+, or Linux (Ubuntu 20.04+)
- **Python**: 3.8 or higher
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 2GB free space
- **Internet**: Required for AI API calls

### Recommended Requirements
- **Python**: 3.10 or 3.11
- **RAM**: 8GB or more
- **Storage**: 5GB free space for models and data

## Installation Steps

### Step 1: Install Python

#### Windows
1. Download from [python.org](https://www.python.org/downloads/)
2. Run installer and **check "Add Python to PATH"**
3. Verify: `python --version`

#### macOS
```bash
# Using Homebrew
brew install python@3.11

# Verify
python3 --version
```

#### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip
python3 --version
```

### Step 2: Install Git

#### Windows
Download from [git-scm.com](https://git-scm.com/download/win)

#### macOS
```bash
brew install git
```

#### Linux
```bash
sudo apt install git
```

### Step 3: Clone the Repository

```bash
# Create a directory for your projects
mkdir ~/projects
cd ~/projects

# Clone the repository
git clone https://github.com/yourusername/ai-content-analyzer-pro.git
cd ai-content-analyzer-pro
```

### Step 4: Create Virtual Environment

#### Windows
```bash
python -m venv venv
venv\Scripts\activate
```

#### macOS/Linux
```bash
python3 -m venv venv
source venv/bin/activate
```

You should see `(venv)` at the start of your command prompt.

### Step 5: Install Dependencies

```bash
# Upgrade pip first
pip install --upgrade pip

# Install all requirements
pip install -r requirements.txt

# Download spaCy language model
python -m spacy download en_core_web_sm
```

This may take 5-10 minutes depending on your internet connection.

### Step 6: Set Up Environment Variables

1. **Copy the example file**:
```bash
cp .env.example .env
```

2. **Edit .env file** (use any text editor):
```bash
# Windows
notepad .env

# macOS/Linux
nano .env
# or
vim .env
```

3. **Add your API keys** (see next section)

## API Keys Setup

### OpenAI API Key

1. **Create OpenAI Account**
   - Visit [platform.openai.com](https://platform.openai.com/)
   - Sign up or log in

2. **Generate API Key**
   - Go to API Keys section
   - Click "Create new secret key"
   - Copy the key (starts with `sk-`)

3. **Add to .env**
   ```
   OPENAI_API_KEY=sk-your-actual-key-here
   ```

4. **Add Credits**
   - Go to Billing
   - Add payment method and credits ($5-10 recommended for testing)

### Google Gemini API Key (Optional but Recommended)

1. **Visit Google AI Studio**
   - Go to [makersuite.google.com/app/apikey](https://makersuite.google.com/app/apikey)
   - Sign in with Google account

2. **Create API Key**
   - Click "Create API Key"
   - Select existing project or create new one
   - Copy the generated key

3. **Add to .env**
   ```
   GOOGLE_API_KEY=your-google-api-key-here
   ```

### Generate Secret Key

```bash
# Run this command to generate a secure secret key
python -c "import secrets; print(secrets.token_hex(32))"
```

Copy the output and add to `.env`:
```
SECRET_KEY=your-generated-secret-key-here
```

## Database Configuration

### Initialize Database

```bash
# Start Python interactive shell
python

# Run these commands
>>> from app import app, db
>>> with app.app_context():
...     db.create_all()
>>> exit()
```

You should see a new `instance` folder with `content_analyzer.db`.

## Optional Components

### Tesseract OCR (for Image Text Extraction)

#### Windows
1. Download from [github.com/UB-Mannheim/tesseract](https://github.com/UB-Mannheim/tesseract/wiki)
2. Install to `C:\Program Files\Tesseract-OCR`
3. Add to `.env`:
   ```
   TESSERACT_PATH=C:\Program Files\Tesseract-OCR\tesseract.exe
   ```

#### macOS
```bash
brew install tesseract
```

#### Linux
```bash
sudo apt install tesseract-ocr
```

## Verification

### Test Installation

1. **Start the application**:
```bash
python app.py
```

2. **Check output**:
```
 * Running on http://127.0.0.1:5000
 * Debug mode: on
```

3. **Open browser**:
   - Navigate to `http://localhost:5000`
   - You should see the registration page

### Create Test Account

1. Click "Register"
2. Enter:
   - Name: Test User
   - Email: test@example.com
   - Password: testpassword123
3. Click "Register"
4. You should be redirected to the main interface

### Test Basic Functionality

1. **Test Website Scraping**:
   - Enter URL: `https://example.com`
   - Click "Analyze"
   - Wait for results

2. **Test File Upload**:
   - Upload a small PDF or Word document
   - Choose summary options
   - Click "Analyze"

## Troubleshooting

### Common Issues

#### 1. "Module not found" Error
```bash
# Solution: Reinstall dependencies
pip install -r requirements.txt
```

#### 2. "Port 5000 already in use"
```bash
# Windows - Find and kill process
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# macOS/Linux
lsof -ti:5000 | xargs kill -9
```

Or change the port in `app.py`:
```python
if __name__ == '__main__':
    app.run(debug=True, port=5001)  # Change to 5001
```

#### 3. "API Key Invalid" Error
- Double-check your API key in `.env`
- Ensure no extra spaces or quotes
- Verify the key is active in your OpenAI dashboard
- Check billing credits

#### 4. Database Errors
```bash
# Delete and recreate database
rm -rf instance/
python
>>> from app import app, db
>>> with app.app_context():
...     db.create_all()
>>> exit()
```

#### 5. spaCy Model Error
```bash
python -m spacy download en_core_web_sm --force
```

#### 6. Virtual Environment Issues
```bash
# Deactivate current environment
deactivate

# Delete and recreate
rm -rf venv/  # or rmdir /s venv on Windows
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

#### 7. Import Errors
```bash
# Verify you're in the virtual environment
which python  # Should show path to venv
# or on Windows: where python

# If not, activate it again
source venv/bin/activate
```

### Getting Help

If you encounter issues not covered here:

1. **Check Application Logs**
   - Look for error messages in the terminal
   - Check `app.log` file if it exists

2. **Search Existing Issues**
   - Visit the GitHub Issues page
   - Search for similar problems

3. **Open New Issue**
   - Describe the problem clearly
   - Include error messages
   - Mention your OS and Python version
   - Share relevant logs

4. **Contact**
   - Email: your.email@example.com
   - GitHub: @yourusername

## Next Steps

After successful setup:

1. **Read the Main README**: Understand all features
2. **Explore the Interface**: Try different document types
3. **Test Collections**: Organize your analyses
4. **Try Chat Feature**: Ask questions about your documents
5. **Export Data**: Test different export formats

## Performance Tips

### For Better Performance

1. **Use SSD**: Store the app on an SSD drive
2. **Increase RAM**: 8GB+ recommended for large documents
3. **Faster Internet**: Required for AI API calls
4. **Close Other Apps**: Free up system resources

### For Faster Development

1. **Use Debug Mode**: Already enabled by default
2. **Hot Reload**: Changes reload automatically
3. **Check Logs**: Monitor terminal for errors

## Security Best Practices

1. **Never commit .env**: Already in .gitignore
2. **Use strong passwords**: For user accounts
3. **Keep keys secure**: Don't share API keys
4. **Regular updates**: Keep dependencies updated
5. **Backup data**: Regularly backup your database

## Updating the Application

```bash
# Pull latest changes
git pull origin main

# Update dependencies
pip install -r requirements.txt --upgrade

# Migrate database if needed
python
>>> from app import app, db
>>> with app.app_context():
...     db.create_all()
>>> exit()
```

## Uninstallation

If you need to remove the application:

```bash
# Deactivate virtual environment
deactivate

# Delete project folder
cd ..
rm -rf ai-content-analyzer-pro
```

---

🎉 **Congratulations!** Your AI Content Analyzer Pro is now set up and ready to use!

For more information, check out:
- [README.md](README.md) - Feature overview
- [DEPLOYMENT.md](DEPLOYMENT.md) - Production deployment
- [CONTRIBUTING.md](CONTRIBUTING.md) - Contributing guidelines
