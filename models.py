from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Quote(db.Model):
    __tablename__ = 'quotes'
    
    id = db.Column(db.Integer, primary_key=True)

    # Base columns
    invoice_number = db.Column(db.String(50), nullable=False, unique=True)
    date = db.Column(db.Date, nullable=False)
    date_promised = db.Column(db.Date)
    date_delivered = db.Column(db.Date)
    stock_number = db.Column(db.String(50))
    to_name = db.Column(db.String(100))
    tag_number = db.Column(db.String(50))
    color = db.Column(db.String(50))
    vehicle = db.Column(db.String(100))
    instructions = db.Column(db.Text, nullable=True)

    # Service columns - headlights_resurfacing
    headlights_resurfacing_photo_link = db.Column(db.String(500))
    headlights_resurfacing_parts_cost = db.Column(db.Numeric(10, 2), default=0.00)
    headlights_resurfacing_labor_cost = db.Column(db.Numeric(10, 2), default=0.00)

    # Service columns - headlights_ceramic
    headlights_ceramic_photo_link = db.Column(db.String(500))
    headlights_ceramic_parts_cost = db.Column(db.Numeric(10, 2), default=0.00)
    headlights_ceramic_labor_cost = db.Column(db.Numeric(10, 2), default=0.00)

    # Service columns - trim_ceramic
    trim_ceramic_photo_link = db.Column(db.String(500))
    trim_ceramic_parts_cost = db.Column(db.Numeric(10, 2), default=0.00)
    trim_ceramic_labor_cost = db.Column(db.Numeric(10, 2), default=0.00)

    # Service columns - car_wizard_diy
    car_wizard_diy_photo_link = db.Column(db.String(500))
    car_wizard_diy_parts_cost = db.Column(db.Numeric(10, 2), default=0.00)
    car_wizard_diy_labor_cost = db.Column(db.Numeric(10, 2), default=0.00)

    # Service columns - carspa_sealant
    carspa_sealant_photo_link = db.Column(db.String(500))
    carspa_sealant_parts_cost = db.Column(db.Numeric(10, 2), default=0.00)
    carspa_sealant_labor_cost = db.Column(db.Numeric(10, 2), default=0.00)

    # Service columns - carspa_ceramic
    carspa_ceramic_photo_link = db.Column(db.String(500))
    carspa_ceramic_parts_cost = db.Column(db.Numeric(10, 2), default=0.00)
    carspa_ceramic_labor_cost = db.Column(db.Numeric(10, 2), default=0.00)

    # Service columns - mechanical
    mechanical_photo_link = db.Column(db.String(500))
    mechanical_parts_cost = db.Column(db.Numeric(10, 2), default=0.00)
    mechanical_labor_cost = db.Column(db.Numeric(10, 2), default=0.00)

    # Service columns - glass
    glass_photo_link = db.Column(db.String(500))
    glass_parts_cost = db.Column(db.Numeric(10, 2), default=0.00)
    glass_labor_cost = db.Column(db.Numeric(10, 2), default=0.00)

    # Service columns - tint
    tint_photo_link = db.Column(db.String(500))
    tint_parts_cost = db.Column(db.Numeric(10, 2), default=0.00)
    tint_labor_cost = db.Column(db.Numeric(10, 2), default=0.00)

    # Service columns - misc
    misc_photo_link = db.Column(db.String(500))
    misc_parts_cost = db.Column(db.Numeric(10, 2), default=0.00)
    misc_labor_cost = db.Column(db.Numeric(10, 2), default=0.00)
    
    def get_service_total(self, service_name):
        """Calculate total for a specific service (parts + labor)"""
        parts = getattr(self, f'{service_name}_parts_cost', 0) or 0
        labor = getattr(self, f'{service_name}_labor_cost', 0) or 0
        return float(parts) + float(labor)
    
    def get_grand_total(self):
        """Calculate grand total across all services"""
        services = ['headlights_resurfacing', 'headlights_ceramic', 'trim_ceramic',
                    'car_wizard_diy', 'carspa_sealant', 'carspa_ceramic',
                    'mechanical', 'glass', 'tint', 'misc']
        total = 0.0
        for service in services:
            total += self.get_service_total(service)
        return total
    
    def __repr__(self):
        return f'<Quote {self.invoice_number}>'
