from random import randint
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy

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
    stock_number = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    head_lights = db.Column(db.Float, nullable=False)
    dents = db.Column(db.Float, nullable=False)
    chips_scratches = db.Column(db.Float, nullable=False)
    remediation = db.Column(db.Float, nullable=False)
    paint_body = db.Column(db.Float, nullable=False)
    parts = db.Column(db.Float, nullable=False)
    labor = db.Column(db.Float, nullable=False)
    total = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f"InvoiceItem('{self.stock_number}', '{self.description}', '{self.total}')"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/invoice/<int:invoice_id>')
def invoice(invoice_id):
    invoice_items = InvoiceItem.query.filter_by(invoice_id=invoice_id).all()
    invoice =  Invoice.query.filter_by(invoice_id=invoice_id).first()
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
    if invoice_id:
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
        invoice_item = InvoiceItem(
            approved=item.get('APPROVED'),
            invoice_id=invoice_id,
            stock_number=item.get('STOCK #'),
            description=item.get('DESCRIPTION'),
            head_lights=float(item.get('HEAD LIGHTS') or 0),
            dents=float(item.get('DENTS') or 0),
            chips_scratches=float(item.get('CHIPS/SCRATCHES') or 0),
            remediation=float(item.get('REMEDIATION') or 0),
            paint_body=float(item.get('PAINT & BODY') or 0),
            parts=float(item.get('PARTS') or 0),
            labor=float(item.get('LABOR') or 0),
            total=float(item.get('TOTAL') or 0)
        )
        db.session.add(invoice_item)
        db.session.commit()
    return jsonify({'id': invoice.invoice_id})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create database tables for our data models
    app.run(debug=True)