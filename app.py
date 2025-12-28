"""
SpecGenie - A simple specification generator for software projects.

This Flask application takes a natural-language project description and generates:
1. User stories
2. A simple UML-like entity view
3. A basic risk list

Created for a university Software Quality Management project.
"""

import re
from flask import Flask, render_template, request, redirect, url_for, session, send_file
from fpdf import FPDF
import io 
app = Flask(__name__)
# Secret key for session management (in production, use a secure random key)
app.secret_key = 'specgenie-demo-secret-key-2024'


# =============================================================================
# TEXT PROCESSING FUNCTIONS
# =============================================================================

def generate_user_stories(description):
    """
    Generate user stories from a project description.
    
    Strategy:
    - Split the description into sentences (by period or newline).
    - For each meaningful sentence, create a user story.
    - Format: "As a user, I want [action] so that [benefit]."
    
    Args:
        description (str): The raw project description text.
    
    Returns:
        list: A list of user story strings.
    """
    user_stories = []
    
    # Split by period or newline to get individual statements
    # Using regex to split on period followed by space, or newline
    sentences = re.split(r'[.\n]+', description)
    
    for sentence in sentences:
        # Clean up whitespace
        sentence = sentence.strip()
        
        # Skip empty or very short sentences (less than 10 chars)
        if len(sentence) < 10:
            continue
        
        # Convert to lowercase for the action part
        action = sentence.lower()
        
        # Remove common starting words that don't add meaning
        action = re.sub(r'^(the system should |the app should |users can |the user can |it should |should )', '', action)
        
        # Create a simple user story
        # We use a generic benefit since we can't reliably extract it
        story = f"As a user, I want to {action} so that I can accomplish my goals efficiently."
        user_stories.append(story)
    
    # If no stories were generated, add a default one
    if not user_stories:
        user_stories.append("As a user, I want to use the system so that I can accomplish my tasks.")
    
    return user_stories


def extract_entities(description):
    """
    Extract potential entities from the project description for UML-like view.
    
    Strategy:
    - Define a list of common entity keywords.
    - Scan the description for these keywords.
    - Assign generic responsibilities based on entity type.
    
    Args:
        description (str): The raw project description text.
    
    Returns:
        list: A list of dictionaries with 'entity' and 'responsibilities' keys.
    """
    # Common entities and their typical responsibilities
    entity_patterns = {
        'user': 'Authenticate, view content, perform actions, manage profile',
        'admin': 'Manage users, configure system, view reports, moderate content',
        'customer': 'Browse products, place orders, track deliveries, leave reviews',
        'order': 'Store order details, track status, calculate totals, manage items',
        'product': 'Store product info, manage inventory, display details, handle pricing',
        'system': 'Process requests, manage data, handle errors, provide services',
        'database': 'Store data, handle queries, ensure integrity, manage backups',
        'payment': 'Process transactions, validate cards, handle refunds, generate receipts',
        'report': 'Aggregate data, generate visualizations, export formats, schedule delivery',
        'notification': 'Send alerts, manage preferences, track delivery, handle templates',
        'project': 'Store project info, track progress, manage members, handle deadlines',
        'task': 'Track status, assign owners, set deadlines, manage dependencies',
        'file': 'Store content, manage versions, handle uploads, control access',
        'message': 'Store content, track read status, manage threads, handle attachments',
        'account': 'Manage credentials, track activity, handle permissions, store preferences',
        'inventory': 'Track quantities, manage locations, handle transfers, set alerts',
        'category': 'Organize items, manage hierarchy, handle relationships, enable filtering',
        'review': 'Store ratings, manage comments, track helpfulness, moderate content',
        'cart': 'Manage items, calculate totals, handle quantities, persist session',
        'shipping': 'Calculate costs, track packages, manage addresses, handle returns',
    }
    
    entities = []
    description_lower = description.lower()
    
    # Search for each entity keyword in the description
    for entity, responsibilities in entity_patterns.items():
        if entity in description_lower:
            entities.append({
                'entity': entity.capitalize(),
                'responsibilities': responsibilities
            })
    
    # If no entities found, add a generic "System" entity
    if not entities:
        entities.append({
            'entity': 'System',
            'responsibilities': 'Handle core business logic and user interactions'
        })
    
    return entities


def generate_risks(description):
    """
    Generate a risk list based on the project description.
    
    Strategy:
    - Start with generic risks that apply to most software projects.
    - Add specific risks based on keywords found in the description.
    - Each risk has: name, impact (High/Medium/Low), likelihood (High/Medium/Low).
    
    Args:
        description (str): The raw project description text.
    
    Returns:
        list: A list of dictionaries with 'risk', 'impact', 'likelihood' keys.
    """
    risks = []
    description_lower = description.lower()
    
    # Always include these generic risks
    generic_risks = [
        {
            'risk': 'Performance issues with large datasets',
            'impact': 'Medium',
            'likelihood': 'Medium'
        },
        {
            'risk': 'Security vulnerabilities in user input handling',
            'impact': 'High',
            'likelihood': 'Medium'
        },
        {
            'risk': 'Insufficient error handling causing poor user experience',
            'impact': 'Medium',
            'likelihood': 'High'
        },
    ]
    risks.extend(generic_risks)
    
    # Keyword-based conditional risks
    keyword_risks = {
        'payment': {
            'risk': 'Payment gateway integration failure',
            'impact': 'High',
            'likelihood': 'Low'
        },
        'user data': {
            'risk': 'User data privacy and GDPR compliance issues',
            'impact': 'High',
            'likelihood': 'Medium'
        },
        'password': {
            'risk': 'Weak password storage leading to data breach',
            'impact': 'High',
            'likelihood': 'Medium'
        },
        'upload': {
            'risk': 'Malicious file upload vulnerability',
            'impact': 'High',
            'likelihood': 'Medium'
        },
        'api': {
            'risk': 'API rate limiting and availability issues',
            'impact': 'Medium',
            'likelihood': 'Medium'
        },
        'database': {
            'risk': 'Database corruption or data loss',
            'impact': 'High',
            'likelihood': 'Low'
        },
        'real-time': {
            'risk': 'Real-time synchronization failures',
            'impact': 'Medium',
            'likelihood': 'Medium'
        },
        'notification': {
            'risk': 'Notification delivery failures or spam issues',
            'impact': 'Low',
            'likelihood': 'Medium'
        },
        'third-party': {
            'risk': 'Third-party service dependency and downtime',
            'impact': 'Medium',
            'likelihood': 'Medium'
        },
        'mobile': {
            'risk': 'Cross-platform compatibility issues',
            'impact': 'Medium',
            'likelihood': 'High'
        },
    }
    
    # Add risks based on keywords found in description
    for keyword, risk_data in keyword_risks.items():
        if keyword in description_lower:
            risks.append(risk_data)
    
    return risks


# =============================================================================
# FLASK ROUTES
# =============================================================================

@app.route('/')
def index():
    """
    Home page route.
    Displays the form for entering a project description.
    If demo data exists in session, pre-fill the form.
    """
    # Check if there's demo data to pre-fill
    demo_description = session.get('demo_description', '')
    return render_template('index.html', description=demo_description)


@app.route('/analyze', methods=['POST'])
def analyze():
    """
    Analysis route.
    Takes the project description from the form, generates specifications,
    stores them in session, and redirects to the results page.
    """
    # Get the project description from the form
    description = request.form.get('description', '').strip()
    
    if not description:
        # If empty, redirect back to home
        return redirect(url_for('index'))
    
    # Generate the specifications
    user_stories = generate_user_stories(description)
    entities = extract_entities(description)
    risks = generate_risks(description)
    
    # Store in session for persistence
    session['analysis'] = {
        'description': description,
        'user_stories': user_stories,
        'entities': entities,
        'risks': risks
    }
    
    # Store user_stories separately for easy access by export route
    session['user_stories'] = user_stories
    
    # Clear demo flag after analysis
    session.pop('demo_description', None)
    
    return redirect(url_for('results'))


@app.route('/results')
def results():
    """
    Results page route.
    Displays the generated specifications from session data.
    If no analysis exists, redirects to home.
    """
    # Get analysis from session
    analysis = session.get('analysis')
    
    if not analysis:
        # No analysis found, redirect to home
        return redirect(url_for('index'))
    
    return render_template('results.html',
                           description=analysis['description'],
                           user_stories=analysis['user_stories'],
                           entities=analysis['entities'],
                           risks=analysis['risks'])


@app.route('/demo')
def demo():
    """
    Demo route.
    Pre-loads a sample project description and redirects to home page.
    This allows for quick demonstration of the application.
    """
    sample_description = """The system should allow users to register and login securely.
Users can create and manage their projects.
Each project can have multiple tasks with deadlines.
Admins can view reports and manage all users.
The system should send notifications for upcoming deadlines.
Users can upload files and attach them to tasks.
The database should store all project and task information.
Users can search and filter their tasks by status or date."""
    
    # Store in session for the form to pick up
    session['demo_description'] = sample_description
    
    return redirect(url_for('index'))


@app.route('/export_stories_pdf')
def export_stories_pdf():
    """
    Export user stories as a PDF file.
    Uses the fpdf2 library to generate the PDF.
    """
    stories = session.get('user_stories')
    if not stories:
        # No stories generated yet, redirect to home
        return redirect(url_for('index'))

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Arial', size=12)

    pdf.cell(0, 10, 'SpecGenie - User Stories', ln=True)
    pdf.ln(5)

    for s in stories:
        pdf.multi_cell(0, 8, f'- {s}')
        pdf.ln(1)

    # Get PDF as bytes - fpdf2 returns bytearray directly
    pdf_bytes = pdf.output()
    pdf_stream = io.BytesIO(pdf_bytes)

    return send_file(
        pdf_stream,
        as_attachment=True,
        download_name='specgenie_user_stories.pdf',
        mimetype='application/pdf',
    )


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

if __name__ == '__main__':
    # Run the Flask development server
    # Debug mode is enabled for development; disable in production
    app.run(debug=True, host='127.0.0.1', port=5000)
