from random import randint
from flask import Flask, render_template, request, jsonify, send_file
import os
from dotenv import load_dotenv
from azure.storage.blob import BlobServiceClient

load_dotenv()  # Load environment variables from .env file
from werkzeug.utils import secure_filename
from uuid import uuid4
from flask_sqlalchemy import SQLAlchemy
from io import BytesIO
import pillow_heif
from PIL import Image

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)


class Invoice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(80), nullable=False)
    name = db.Column(db.String(80), nullable=False)
    invoice_id = db.Column(db.Integer, unique=True, nullable=False)
    items = db.relationship('InvoiceItem', backref='invoice', lazy=True)

    def __repr__(self):
        return f"Invoice('{self.date}', '{self.name}', '{self.invoice_id}')"


class InvoiceItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoice.invoice_id'), nullable=False)
    approved = db.Column(db.Boolean, nullable=False, default=False)
    comments = db.Column(db.String(255), nullable=True)
    stock_number = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    picture_url = db.Column(db.String(512), nullable=True)  # New field
    head_lights = db.Column(db.Boolean, nullable=False, default=False)
    dents = db.Column(db.Boolean, nullable=False, default=False)
    chips_scratches = db.Column(db.Boolean, nullable=False, default=False)
    remediation = db.Column(db.Boolean, nullable=False, default=False)
    paint_body = db.Column(db.Boolean, nullable=False, default=False)
    parts = db.Column(db.Float, nullable=False)
    labor = db.Column(db.Float, nullable=False)
    total = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f"InvoiceItem('{self.stock_number}', '{self.description}', '{self.total}')"

def delete_invoice_if_exists(invoice_id):
    invoice = Invoice.query.filter_by(invoice_id=invoice_id).first()
    if invoice:
        InvoiceItem.query.filter_by(invoice_id=invoice_id).delete()
        db.session.delete(invoice)
        db.session.commit()
        return True
    else:
        return False

AZURE_CONNECTION_STRING = os.environ.get('AZURE_CONNECTION_STRING')
AZURE_CONTAINER = 'oneshotautobucket'

@app.route('/upload-picture', methods=['POST'])
def upload_picture():
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

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/invoice/<int:invoice_id>')
def invoice(invoice_id):
    invoice_items = InvoiceItem.query.filter_by(invoice_id=invoice_id).all()
    invoice = Invoice.query.filter_by(invoice_id=invoice_id).first()
    if invoice is None:
        return render_template('404.html'), 404
    data = {
        'INVOICE #': invoice.invoice_id,
        'NAME': invoice.name,
        'DATE': invoice.date,
        'invoiceItems': invoice_items
    }
    return render_template('index.html', data=data)

@app.route('/submit-invoice', methods=['POST'])
def submit_invoice():
    data = request.get_json()
    invoice_id = data.get('INVOICE #')
    name = data.get('NAME', '')
    date = data.get('DATE', '')
    #check for existing invoice
    if invoice_id is not None:
        invoice_id = int(invoice_id)
        old_invoice = Invoice.query.filter_by(invoice_id=invoice_id).first()
        if old_invoice:
            InvoiceItem.query.filter_by(invoice_id=invoice_id).delete()
            db.session.delete(old_invoice)
            db.session.commit()
    else:
        invoice_id = 1 if not Invoice.query.all() else Invoice.query.all()[-1].invoice_id + 1

    invoice = Invoice(date=date, name=name, invoice_id=invoice_id)
    db.session.add(invoice)
    db.session.commit()
    for item in data['invoiceItems']:
        parts = float(item.get('PARTS') or 0)
        labor = float(item.get('LABOR') or 0)
        total = parts + labor
        invoice_item = InvoiceItem(
            approved=item.get('APPROVED'),
            comments=item.get('COMMENTS'),
            invoice_id=invoice_id,
            stock_number=item.get('STOCK #'),
            description=item.get('DESCRIPTION'),
            picture_url=item.get('PICTURE_URL'),  # New field
            head_lights=bool(item.get('HEAD LIGHTS')),
            dents=bool(item.get('DENTS')),
            chips_scratches=bool(item.get('CHIPS/SCRATCHES')),
            remediation=bool(item.get('REMEDIATION')),
            paint_body=bool(item.get('PAINT & BODY')),
            parts=parts,
            labor=labor,
            total=total
        )
        db.session.add(invoice_item)
        db.session.commit()
    return jsonify({'id': invoice.invoice_id})

@app.route('/delete-invoice/<int:invoice_id>', methods=['DELETE'])
def delete_invoice(invoice_id):
    if delete_invoice_if_exists(invoice_id):
        return jsonify({'message': 'Invoice deleted successfully'}), 200
    else:
        return render_template('404.html'), 404

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create database tables for our data models
    app.run(host='0.0.0.0', port=5000, debug=True)