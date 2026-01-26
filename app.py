from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from models import db, Quote
from forms import QuoteForm
from datetime import datetime
import os
from io import BytesIO
from uuid import uuid4
from werkzeug.utils import secure_filename
from azure.storage.blob import BlobServiceClient
from PIL import Image
import pillow_heif
from dotenv import load_dotenv
import requests
import secrets
import base64
from urllib.parse import urlencode
from token_manager import save_tokens, get_access_token, is_token_valid, clear_tokens
from xero_service import send_quote_to_xero

load_dotenv()

# Register HEIF opener with Pillow
pillow_heif.register_heif_opener()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quotes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Azure Blob Storage configuration (set via environment variables)
AZURE_CONNECTION_STRING = os.environ.get('AZURE_CONNECTION_STRING', '')
AZURE_CONTAINER = os.environ.get('AZURE_CONTAINER', 'pictures')

# Xero OAuth Configuration
XERO_CLIENT_ID = os.environ.get('XERO_CLIENT_ID')
XERO_CLIENT_SECRET = os.environ.get('XERO_CLIENT_SECRET')
XERO_REDIRECT_URI = os.environ.get('XERO_REDIRECT_URI')
XERO_TENANT_ID = os.environ.get('XERO_TENANT_ID')
XERO_AUTH_URL = 'https://login.xero.com/identity/connect/authorize'
XERO_TOKEN_URL = 'https://identity.xero.com/connect/token'
XERO_API_BASE = 'https://api.xero.com/api.xro/2.0'

db.init_app(app)

# Custom Jinja2 filter to get form field by name
@app.template_filter('get_field')
def get_field(form, field_name):
    """Get a form field by name"""
    return getattr(form, field_name, None)

# Make Xero connection status available in all templates
@app.context_processor
def inject_xero_status():
    """Make Xero connection status available in all templates."""
    return dict(is_xero_connected=is_token_valid)

# Service names for iteration
SERVICES = [
    ('chips', 'Chips'),
    ('scratches', 'Scratches'),
    ('dents', 'Dents'),
    ('headlights', 'Headlights'),
    ('wheels', 'Wheels'),
    ('interior', 'Interior'),
    ('detail', 'Detail'),
    ('carspabasic', 'CarsPA Basic'),
    ('carspaplus', 'CarsPA Plus'),
    ('bed_liner', 'Bed Liner'),
    ('paint_body', 'Paint & Body')
]

@app.route('/')
def index():
    """List all quotes with search/filter functionality"""
    search_vin = request.args.get('vin', '')
    search_quote_number = request.args.get('quote_number', '')
    search_make = request.args.get('make', '')
    search_model = request.args.get('model', '')
    search_date_from = request.args.get('date_from', '')
    search_date_to = request.args.get('date_to', '')
    
    query = Quote.query
    
    if search_vin:
        query = query.filter(Quote.vin_number.contains(search_vin))
    if search_quote_number:
        query = query.filter(Quote.quote_number.contains(search_quote_number))
    if search_make:
        query = query.filter(Quote.make.contains(search_make))
    if search_model:
        query = query.filter(Quote.model.contains(search_model))
    if search_date_from:
        try:
            date_from = datetime.strptime(search_date_from, '%Y-%m-%d').date()
            query = query.filter(Quote.date >= date_from)
        except ValueError:
            pass
    if search_date_to:
        try:
            date_to = datetime.strptime(search_date_to, '%Y-%m-%d').date()
            query = query.filter(Quote.date <= date_to)
        except ValueError:
            pass
    
    quotes = query.order_by(Quote.date.desc()).all()
    
    return render_template('index.html', quotes=quotes, 
                         search_vin=search_vin,
                         search_quote_number=search_quote_number,
                         search_make=search_make,
                         search_model=search_model,
                         search_date_from=search_date_from,
                         search_date_to=search_date_to)

@app.route('/create', methods=['GET', 'POST'])
def create_quote():
    """Create a new quote"""
    form = QuoteForm()
    
    if form.validate_on_submit():
        quote = Quote(
            quote_number=form.quote_number.data,
            date=form.date.data,
            vin_number=form.vin_number.data,
            vin_picture_link=form.vin_picture_link.data or None,
            year=form.year.data,
            make=form.make.data or None,
            model=form.model.data or None,
            instructions=form.instructions.data or None,
        )
        
        # Set service fields
        for service_key, _ in SERVICES:
            photo_link = getattr(form, f'{service_key}_photo_link').data
            parts_cost = getattr(form, f'{service_key}_parts_cost').data or 0
            labor_cost = getattr(form, f'{service_key}_labor_cost').data or 0
            
            setattr(quote, f'{service_key}_photo_link', photo_link or None)
            setattr(quote, f'{service_key}_parts_cost', parts_cost)
            setattr(quote, f'{service_key}_labor_cost', labor_cost)
        
        try:
            db.session.add(quote)
            db.session.commit()
            flash('Quote created successfully!', 'success')
            return redirect(url_for('quote_detail', id=quote.id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating quote: {str(e)}', 'error')
    
    return render_template('create_quote.html', form=form, services=SERVICES)

@app.route('/quote/<int:id>', methods=['GET', 'POST'])
def quote_detail(id):
    """View and edit a single quote"""
    quote = Quote.query.get_or_404(id)
    form = QuoteForm(obj=quote)
    
    if form.validate_on_submit():
        quote.quote_number = form.quote_number.data
        quote.date = form.date.data
        quote.vin_number = form.vin_number.data
        quote.vin_picture_link = form.vin_picture_link.data or None
        quote.year = form.year.data
        quote.make = form.make.data or None
        quote.model = form.model.data or None
        quote.instructions = form.instructions.data or None

        # Update service fields
        for service_key, _ in SERVICES:
            photo_link = getattr(form, f'{service_key}_photo_link').data
            parts_cost = getattr(form, f'{service_key}_parts_cost').data or 0
            labor_cost = getattr(form, f'{service_key}_labor_cost').data or 0
            
            setattr(quote, f'{service_key}_photo_link', photo_link or None)
            setattr(quote, f'{service_key}_parts_cost', parts_cost)
            setattr(quote, f'{service_key}_labor_cost', labor_cost)
        
        try:
            db.session.commit()
            flash('Quote updated successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating quote: {str(e)}', 'error')
    
    return render_template('quote_detail.html', quote=quote, form=form, services=SERVICES)

@app.route('/quote/<int:id>/send-to-xero', methods=['POST'])
def send_quote_to_xero_route(id):
    """Send quote to Xero Quotes API."""

    # Check if connected to Xero
    if not is_token_valid():
        flash('Please connect to Xero first.', 'error')
        return redirect(url_for('xero_authorize'))

    # Get quote
    quote = Quote.query.get_or_404(id)

    # Send to Xero
    result = send_quote_to_xero(quote)

    if result['success']:
        flash(result['message'], 'success')
    else:
        flash(f"Failed to send to Xero: {result['error']}", 'error')

    # Redirect back to quote detail
    return redirect(url_for('quote_detail', id=id))

@app.route('/quote/<int:id>/delete', methods=['POST'])
def delete_quote(id):
    """Delete a quote"""
    quote = Quote.query.get_or_404(id)
    try:
        db.session.delete(quote)
        db.session.commit()
        flash('Quote deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting quote: {str(e)}', 'error')
    return redirect(url_for('index'))

@app.route('/upload-picture', methods=['POST'])
def upload_picture():
    """Upload a picture to Azure Blob Storage"""
    if not AZURE_CONNECTION_STRING:
        return jsonify({'error': 'Azure storage not configured'}), 500
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    filename = secure_filename(file.filename)
    ext = os.path.splitext(filename)[1].lower()
    blob_service_client = BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)
    
    # Convert HEIC to JPG if needed
    if ext == '.heic':
        heif_file = pillow_heif.read_heif(file)
        image = Image.frombytes(
            heif_file.mode,
            heif_file.size,
            heif_file.data,
            "raw",
        )
        output = BytesIO()
        image.save(output, format="JPEG")
        output.seek(0)
        blob_name = f"{uuid4().hex}.jpg"
        blob_client = blob_service_client.get_blob_client(container=AZURE_CONTAINER, blob=blob_name)
        blob_client.upload_blob(output, overwrite=True, content_type="image/jpeg")
        blob_url = f"https://{blob_service_client.account_name}.blob.core.windows.net/{AZURE_CONTAINER}/{blob_name}"
        return jsonify({'url': blob_url})
    else:
        # Not HEIC, upload as-is
        blob_name = f"{uuid4().hex}{ext}"
        blob_client = blob_service_client.get_blob_client(container=AZURE_CONTAINER, blob=blob_name)
        blob_client.upload_blob(file, overwrite=True)
        blob_url = f"https://{blob_service_client.account_name}.blob.core.windows.net/{AZURE_CONTAINER}/{blob_name}"
        return jsonify({'url': blob_url})

# Xero OAuth Helper Function
def get_xero_auth_header():
    """Generate Basic Auth header for token exchange."""
    credentials = f"{XERO_CLIENT_ID}:{XERO_CLIENT_SECRET}"
    encoded = base64.b64encode(credentials.encode()).decode()
    return f"Basic {encoded}"

# Xero OAuth Routes
@app.route('/auth/xero/authorize')
def xero_authorize():
    """Redirect user to Xero authorization page."""
    from flask import session
    # Generate and store state for CSRF protection
    state = secrets.token_urlsafe(32)
    session['oauth_state'] = state

    # Build authorization URL
    params = {
        'response_type': 'code',
        'client_id': XERO_CLIENT_ID,
        'redirect_uri': XERO_REDIRECT_URI,
        'scope': 'openid accounting.transactions',
        'state': state
    }

    auth_url = f"{XERO_AUTH_URL}?{urlencode(params)}"
    return redirect(auth_url)

@app.route('/auth/xero/callback')
def xero_callback():
    """Handle OAuth callback from Xero."""
    from flask import session
    # Verify state to prevent CSRF
    state = request.args.get('state')
    if state != session.get('oauth_state'):
        flash('Invalid state parameter. Authorization failed.', 'error')
        return redirect(url_for('index'))

    # Get authorization code
    code = request.args.get('code')
    if not code:
        error = request.args.get('error', 'Unknown error')
        flash(f'Authorization failed: {error}', 'error')
        return redirect(url_for('index'))

    # Exchange code for access token
    token_data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': XERO_REDIRECT_URI
    }

    headers = {
        'Authorization': get_xero_auth_header(),
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    try:
        response = requests.post(XERO_TOKEN_URL, data=token_data, headers=headers)
        response.raise_for_status()
        token_response = response.json()

        # Store tokens in JSON file
        save_tokens(
            token_response.get('access_token'),
            token_response.get('refresh_token'),
            token_response.get('expires_in')
        )

        flash('Successfully connected to Xero!', 'success')
        return redirect(url_for('index'))

    except requests.exceptions.RequestException as e:
        flash(f'Token exchange failed: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/auth/xero/test')
def xero_test():
    """Make test API call to Xero Quotes endpoint."""
    access_token = get_access_token()

    if not access_token:
        flash('No access token found. Please authorize first.', 'error')
        return redirect(url_for('index'))

    # Make API call to Xero Quotes endpoint
    headers = {
        'Authorization': f'Bearer {access_token}',
        'xero-tenant-id': XERO_TENANT_ID,
        'Accept': 'application/json'
    }

    try:
        response = requests.get(f'{XERO_API_BASE}/Quotes', headers=headers)
        response.raise_for_status()
        quotes_data = response.json()

        # Render template with JSON response (token NOT included for security)
        return render_template('xero_test.html',
                             quotes_data=quotes_data)

    except requests.exceptions.RequestException as e:
        error_message = str(e)
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_data = e.response.json()
                error_message = f"{e.response.status_code}: {error_data}"
            except:
                error_message = f"{e.response.status_code}: {e.response.text}"

        return render_template('xero_test.html',
                             error_message=error_message)

@app.route('/auth/xero/disconnect')
def xero_disconnect():
    """Clear Xero tokens."""
    clear_tokens()
    flash('Disconnected from Xero.', 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', debug=True)                                                                                                                                                                   