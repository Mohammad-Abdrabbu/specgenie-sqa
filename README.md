# SpecGenie 🧞

A simple specification generator for software projects. Built for a university Software Quality Management course project.

## What is SpecGenie?

SpecGenie takes a natural-language project description and automatically generates:

1. **User Stories** - Agile-format stories derived from your description
2. **UML-Like Entity View** - Identifies potential entities and their responsibilities
3. **Risk Analysis** - Lists generic and context-specific project risks

## Quick Start

### Prerequisites
- Python 3.8 or higher

### Setup

```bash
# Navigate to project directory
cd spec-genie

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
.\venv\Scripts\Activate.ps1
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
```

### Access the Application
Open your browser and go to: **http://127.0.0.1:5000**

### Quick Demo
Visit **http://127.0.0.1:5000/demo** to load a sample project description.

## Project Structure

```
spec-genie/
├── app.py              # Main Flask application
├── requirements.txt    # Python dependencies
├── README.md           # This file
└── templates/
    ├── base.html       # Base template with Bootstrap
    ├── index.html      # Home page with input form
    └── results.html    # Results display page
```

## Features

- **Simple Heuristic Processing**: No heavy AI/ML libraries; just Python string processing
- **Session Persistence**: Results are stored in Flask session (survives page refresh)
- **Demo Mode**: Pre-loaded sample description for quick demonstrations
- **Bootstrap Styling**: Clean, responsive UI using Bootstrap 5 CDN

## Known Issues

These are intentional limitations suitable for turning into GitHub issues for SQA purposes:

1. **Naive Entity Detection**: Entity extraction is based on simple keyword matching. It doesn't understand context or relationships between entities. For example, "the user ordered a pizza" would detect "user" and "order" as separate entities but wouldn't understand their relationship.

2. **Simple Risk Rules**: Risk generation uses basic keyword matching. It doesn't consider the probability or severity based on project context. All "High" impact risks are treated equally regardless of the specific project domain.

3. **Basic User Story Format**: All user stories follow the same template and use generic benefits. The system doesn't extract actual user benefits from the description or differentiate between user types.

4. **No Data Persistence**: Analysis results are stored only in the Flask session. Restarting the server or clearing session cookies will lose all data.

## License

This project is for educational purposes as part of a Software Quality Management course.
