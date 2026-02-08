# Contributing to AI Content Analyzer Pro

First off, thank you for considering contributing to AI Content Analyzer Pro! It's people like you that make this project better for everyone.

## Code of Conduct

By participating in this project, you are expected to uphold our Code of Conduct of being respectful and inclusive to all contributors.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the existing issues to avoid duplicates. When you create a bug report, include as many details as possible:

- **Use a clear and descriptive title**
- **Describe the exact steps to reproduce the problem**
- **Provide specific examples**
- **Describe the behavior you observed and what you expected**
- **Include screenshots if relevant**
- **Include your environment details** (OS, Python version, etc.)

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, include:

- **Use a clear and descriptive title**
- **Provide a detailed description of the suggested enhancement**
- **Explain why this enhancement would be useful**
- **List any alternative solutions you've considered**

### Pull Requests

1. Fork the repo and create your branch from `main`
2. If you've added code that should be tested, add tests
3. Ensure your code follows the existing style
4. Make sure your code lints
5. Write a clear commit message
6. Create a Pull Request with a clear description

## Development Setup

1. Fork and clone the repository
2. Create a virtual environment: `python -m venv venv`
3. Activate it: `source venv/bin/activate` (Unix) or `venv\Scripts\activate` (Windows)
4. Install dependencies: `pip install -r requirements.txt`
5. Set up your `.env` file based on `.env.example`
6. Run the application: `python app.py`

## Coding Standards

- Follow PEP 8 style guide for Python code
- Use meaningful variable and function names
- Add comments for complex logic
- Keep functions small and focused
- Write docstrings for functions and classes

## Commit Messages

- Use the present tense ("Add feature" not "Added feature")
- Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit the first line to 72 characters
- Reference issues and pull requests after the first line

Example:
```
Add batch processing feature

- Implement concurrent document processing
- Add progress tracking
- Update UI to show batch status

Closes #123
```

## Project Structure

```
ai-content-analyzer-pro/
├── app.py              # Main Flask application
├── models.py           # Database models
├── services/           # Business logic
├── templates/          # HTML templates
├── static/            # CSS, JS, images
└── tests/             # Test files
```

## Testing

Before submitting a PR, make sure all tests pass:

```bash
python -m pytest
```

## Questions?

Feel free to open an issue with the label "question" if you have any questions about contributing.

Thank you for contributing! 🎉
